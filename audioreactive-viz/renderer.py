"""
Renderer — Shader compilation, FBO management, Spout output, display
Handles ping-pong framebuffers and special dual-pass for reaction-diffusion.
"""

import os
import moderngl
import numpy as np
from presets import MODE_REACTION

SHADER_DIR = os.path.join(os.path.dirname(__file__), "shaders")


class Renderer:
    def __init__(self, ctx: moderngl.Context, width: int, height: int):
        self.ctx = ctx
        self.width = width
        self.height = height

        # Load common GLSL header
        with open(os.path.join(SHADER_DIR, "common.glsl"), "r") as f:
            self.common_glsl = f.read()
        with open(os.path.join(SHADER_DIR, "fullscreen.vert"), "r") as f:
            self.vert_src = f.read()

        # Fullscreen quad VAO
        vbo = ctx.buffer(np.array([
            -1, -1,  1, -1,  -1, 1,
             1, -1,  1,  1,  -1, 1,
        ], dtype='f4').tobytes())
        self._quad_vbo = vbo  # keep reference

        # Shader programs cache: filename -> program
        self._programs = {}
        self._vaos = {}

        # ─── Framebuffers (ping-pong) ───
        self.fbo = [self._make_fbo(), self._make_fbo()]
        self.fbo_idx = 0

        # Extra FBO pair for reaction-diffusion state
        self.rd_state_fbo = [self._make_fbo(), self._make_fbo()]
        self.rd_state_idx = 0
        self._rd_initialized = False

        # Spectrum 1D texture
        self.spectrum_tex = ctx.texture((512, 1), 1, dtype='f4')
        self.spectrum_tex.filter = (moderngl.LINEAR, moderngl.LINEAR)

        # Spout sender (optional)
        self.spout_sender = None
        self.spout_enabled = False

    def _make_fbo(self):
        tex = self.ctx.texture((self.width, self.height), 4, dtype='f4')
        tex.filter = (moderngl.LINEAR, moderngl.LINEAR)
        tex.repeat_x = True
        tex.repeat_y = True
        fbo = self.ctx.framebuffer(color_attachments=[tex])
        return fbo

    def _get_program(self, frag_filename):
        if frag_filename not in self._programs:
            frag_path = os.path.join(SHADER_DIR, frag_filename)
            with open(frag_path, "r") as f:
                frag_body = f.read()

            # Prepend version + common header
            frag_src = "#version 330 core\n" + self.common_glsl + "\n" + frag_body

            try:
                prog = self.ctx.program(
                    vertex_shader=self.vert_src,
                    fragment_shader=frag_src,
                )
            except Exception as e:
                print(f"[Shader] Compilation error in {frag_filename}:")
                print(e)
                return None

            self._programs[frag_filename] = prog

            # Create a VAO for this program
            vao = self.ctx.vertex_array(prog, [(self._quad_vbo, '2f', 'in_position')])
            self._vaos[frag_filename] = vao

        return self._programs[frag_filename]

    def set_uniforms(self, prog, audio, preset, time_val):
        """Set all uniforms on a shader program."""
        def _set(name, value):
            if name in prog:
                prog[name].value = value

        _set('u_time', time_val)
        _set('u_resolution', (float(self.width), float(self.height)))
        _set('u_bass', audio.bass)
        _set('u_mid', audio.mid)
        _set('u_high', audio.high)
        _set('u_rms', audio.rms)
        _set('u_beat', audio.beat)
        _set('u_color1', preset['color1'])
        _set('u_color2', preset['color2'])
        _set('u_color3', preset['color3'])
        _set('u_params', preset['params'])
        _set('u_feedback_amt', preset['feedback'])
        _set('u_speed', preset['speed'])

        # Bind textures
        if 'u_spectrum' in prog:
            self.spectrum_tex.use(location=0)
            prog['u_spectrum'].value = 0

    def update_spectrum(self, spectrum_data):
        """Upload spectrum data to GPU texture."""
        self.spectrum_tex.write(spectrum_data.tobytes())

    def render(self, shader_file, audio, preset, time_val, mode):
        """Main render call. Returns the display FBO texture."""

        is_rd = (mode == MODE_REACTION)

        if is_rd:
            return self._render_reaction_diffusion(shader_file, audio, preset, time_val)
        else:
            return self._render_standard(shader_file, audio, preset, time_val)

    def _render_standard(self, shader_file, audio, preset, time_val):
        prog = self._get_program(shader_file)
        if prog is None:
            return None

        # Ping-pong
        current = self.fbo[self.fbo_idx]
        prev = self.fbo[1 - self.fbo_idx]

        # Bind feedback texture
        prev.color_attachments[0].use(location=1)
        if 'u_feedback' in prog:
            prog['u_feedback'].value = 1

        self.set_uniforms(prog, audio, preset, time_val)

        current.use()
        self._vaos[shader_file].render()

        self.fbo_idx = 1 - self.fbo_idx
        return current

    def _render_reaction_diffusion(self, shader_file, audio, preset, time_val):
        # Initialize RD state if needed
        if not self._rd_initialized:
            self._init_rd_state()
            self._rd_initialized = True

        # === Pass 1: Simulation step (state FBO) ===
        prog = self._get_program(shader_file)
        if prog is None:
            return None

        current_state = self.rd_state_fbo[self.rd_state_idx]
        prev_state = self.rd_state_fbo[1 - self.rd_state_idx]

        prev_state.color_attachments[0].use(location=1)
        if 'u_feedback' in prog:
            prog['u_feedback'].value = 1

        self.set_uniforms(prog, audio, preset, time_val)

        # Run multiple simulation steps per frame for speed
        for _ in range(4):
            current_state = self.rd_state_fbo[self.rd_state_idx]
            prev_state = self.rd_state_fbo[1 - self.rd_state_idx]
            prev_state.color_attachments[0].use(location=1)

            current_state.use()
            self._vaos[shader_file].render()
            self.rd_state_idx = 1 - self.rd_state_idx

        # === Pass 2: Colorize (display FBO) ===
        color_prog = self._get_program("colorize_rd.frag")
        if color_prog is None:
            return None

        display_fbo = self.fbo[self.fbo_idx]

        # Bind the RD state texture as feedback for the colorizer
        last_state = self.rd_state_fbo[1 - self.rd_state_idx]
        last_state.color_attachments[0].use(location=1)
        if 'u_feedback' in color_prog:
            color_prog['u_feedback'].value = 1

        self.set_uniforms(color_prog, audio, preset, time_val)

        display_fbo.use()
        self._vaos["colorize_rd.frag"].render()

        self.fbo_idx = 1 - self.fbo_idx
        return display_fbo

    def _init_rd_state(self):
        """Seed the reaction-diffusion state with chemical A=1, B=0 + some B seeds."""
        w, h = self.width, self.height
        data = np.zeros((h, w, 4), dtype=np.float32)
        data[:, :, 0] = 1.0  # Chemical A = 1 everywhere
        data[:, :, 3] = 1.0

        # Random seeds of chemical B
        rng = np.random.default_rng(42)
        for _ in range(15):
            cx, cy = rng.integers(0, w), rng.integers(0, h)
            r = rng.integers(5, 20)
            y, x = np.ogrid[-cy:h-cy, -cx:w-cx]
            mask = x*x + y*y <= r*r
            data[mask, 1] = 1.0  # Chemical B = 1 in seed spots

        for fbo in self.rd_state_fbo:
            fbo.color_attachments[0].write(data.tobytes())

    def reset_feedback(self):
        """Clear all framebuffers."""
        for fbo in self.fbo:
            fbo.clear(0.0, 0.0, 0.0, 1.0)
        self._rd_initialized = False
        for fbo in self.rd_state_fbo:
            fbo.clear(0.0, 0.0, 0.0, 1.0)

    def invalidate_shader(self, shader_file):
        """Remove cached shader to force recompilation."""
        if shader_file in self._programs:
            del self._programs[shader_file]
        if shader_file in self._vaos:
            del self._vaos[shader_file]

    def init_spout(self):
        """Initialize Spout sender (Windows only, graceful fallback)."""
        try:
            import SpoutGL
            self.spout_sender = SpoutGL.SpoutSender()
            self.spout_sender.setSenderName("AudioReactiveViz")
            self.spout_enabled = True
            print("[Spout] Sender initialized: AudioReactiveViz")
        except ImportError:
            print("[Spout] SpoutGL not installed — Spout output disabled")
            self.spout_enabled = False
        except Exception as e:
            print(f"[Spout] Init error: {e}")
            self.spout_enabled = False

    def send_spout(self, fbo):
        """Send framebuffer to Spout."""
        if not self.spout_enabled or fbo is None:
            return
        try:
            tex_id = fbo.color_attachments[0].glo
            # GL_TEXTURE_2D = 0x0DE1
            self.spout_sender.sendTexture(tex_id, 0x0DE1,
                                          self.width, self.height, False, 0)
        except Exception:
            pass  # silently skip Spout errors

    def blit_to_screen(self, fbo):
        """Copy FBO to default framebuffer (screen)."""
        if fbo is None:
            return
        self.ctx.copy_framebuffer(self.ctx.screen, fbo)

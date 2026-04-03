"""
╔══════════════════════════════════════════════════════╗
║   AUDIOREACTIVE VISUALIZER                          ║
║   5 modes × 4 presets = 20 generative shaders       ║
║   Audio input → FFT → GLSL → Spout                  ║
╚══════════════════════════════════════════════════════╝

Controls:
  1-5          Switch mode
  Left/Right   Cycle presets
  Up/Down      Adjust sensitivity
  F            Toggle fullscreen
  S            Toggle Spout output
  R            Reset feedback buffers
  H            Toggle HUD overlay
  Tab          Toggle parameter panel
  Space        Pause time
  Escape       Quit
"""

import sys
import time
import glfw
import moderngl
import numpy as np

from audio_engine import AudioEngine
from renderer import Renderer
from presets import PresetManager, MODE_NAMES
from gui import GUI


# ─── Config ───
WINDOW_W = 1280
WINDOW_H = 720
TITLE = "Audioreactive Visualizer"


class App:
    def __init__(self):
        self.audio = AudioEngine(smoothing=0.18)
        self.presets = PresetManager()
        self.renderer = None
        self.gui = None

        self.time_val = 0.0
        self.paused = False
        self.show_hud = True
        self.fullscreen = False

        self.window = None
        self.ctx = None
        self.monitor = None

        self._last_mode_shader = None

    def run(self):
        if not self._init_window():
            return
        if not self.audio.start():
            print("[App] Audio failed — running without audio input")

        self.renderer = Renderer(self.ctx, WINDOW_W, WINDOW_H)
        self.renderer.init_spout()
        self.gui = GUI(self.window)

        self._print_info()
        self._main_loop()
        self._cleanup()

    def _init_window(self):
        if not glfw.init():
            print("[GLFW] Failed to initialize")
            return False

        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, True)
        glfw.window_hint(glfw.RESIZABLE, False)

        self.monitor = glfw.get_primary_monitor()
        self.window = glfw.create_window(WINDOW_W, WINDOW_H, TITLE, None, None)

        if not self.window:
            print("[GLFW] Failed to create window")
            glfw.terminate()
            return False

        glfw.make_context_current(self.window)
        glfw.swap_interval(1)  # VSync

        glfw.set_key_callback(self.window, self._key_callback)

        self.ctx = moderngl.create_context()
        return True

    def _key_callback(self, window, key, scancode, action, mods):
        if action != glfw.PRESS:
            return

        # Toggle GUI panel with Tab
        if key == glfw.KEY_TAB:
            self.gui.visible = not self.gui.visible
            return

        # Don't process hotkeys when imgui wants keyboard
        if self.gui and self.gui.wants_keyboard():
            return

        # Mode switching: 1-5
        if glfw.KEY_1 <= key <= glfw.KEY_5:
            mode = key - glfw.KEY_1
            if self.presets.set_mode(mode):
                self.renderer.reset_feedback()
                print(f"  → {self.presets.info()}")

        # Preset cycling
        elif key == glfw.KEY_RIGHT:
            self.presets.next_preset()
            self.renderer.reset_feedback()
            print(f"  → {self.presets.info()}")
        elif key == glfw.KEY_LEFT:
            self.presets.prev_preset()
            self.renderer.reset_feedback()
            print(f"  → {self.presets.info()}")

        # Sensitivity
        elif key == glfw.KEY_UP:
            self.audio.sensitivity = min(5.0, self.audio.sensitivity + 0.1)
            print(f"  Sensitivity: {self.audio.sensitivity:.1f}")
        elif key == glfw.KEY_DOWN:
            self.audio.sensitivity = max(0.1, self.audio.sensitivity - 0.1)
            print(f"  Sensitivity: {self.audio.sensitivity:.1f}")

        # Fullscreen toggle
        elif key == glfw.KEY_F:
            self._toggle_fullscreen()

        # Spout toggle
        elif key == glfw.KEY_S:
            self.renderer.spout_enabled = not self.renderer.spout_enabled
            state = "ON" if self.renderer.spout_enabled else "OFF"
            print(f"  Spout: {state}")

        # Reset
        elif key == glfw.KEY_R:
            self.renderer.reset_feedback()
            print("  Feedback reset")

        # HUD toggle
        elif key == glfw.KEY_H:
            self.show_hud = not self.show_hud

        # Pause
        elif key == glfw.KEY_SPACE:
            self.paused = not self.paused
            state = "PAUSED" if self.paused else "RUNNING"
            print(f"  {state}")

        # Quit
        elif key == glfw.KEY_ESCAPE:
            glfw.set_window_should_close(window, True)

    def _toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            mode = glfw.get_video_mode(self.monitor)
            glfw.set_window_monitor(self.window, self.monitor,
                                    0, 0, mode.size.width, mode.size.height,
                                    mode.refresh_rate)
        else:
            glfw.set_window_monitor(self.window, None,
                                    100, 100, WINDOW_W, WINDOW_H, 0)
        glfw.swap_interval(1)

    def _main_loop(self):
        prev_time = time.perf_counter()

        while not glfw.window_should_close(self.window):
            self.gui.process_inputs()
            glfw.poll_events()

            # Delta time
            now = time.perf_counter()
            dt = now - prev_time
            prev_time = now

            if not self.paused:
                self.time_val += dt

            # Update audio
            self.audio.update()
            self.renderer.update_spectrum(self.audio.spectrum)

            # Get current preset with GUI overrides applied
            preset = self.gui.get_preset_override(self.presets.preset)
            shader_file = self.presets.shader_file
            mode = self.presets.current_mode

            # Render
            fbo = self.renderer.render(shader_file, self.audio, preset,
                                       self.time_val, mode)

            # Spout output
            if self.renderer.spout_enabled:
                self.renderer.send_spout(fbo)

            # Display
            self.renderer.blit_to_screen(fbo)

            # Render GUI overlay
            self.gui.render(self)

            # Update window title as simple HUD
            if self.show_hud:
                fps = 1.0 / max(dt, 0.001)
                spout = " [SPOUT]" if self.renderer.spout_enabled else ""
                title = (f"{TITLE} | {self.presets.info()} | "
                         f"B:{self.audio.bass:.2f} M:{self.audio.mid:.2f} "
                         f"H:{self.audio.high:.2f} | {fps:.0f}fps{spout}")
                glfw.set_window_title(self.window, title)

            glfw.swap_buffers(self.window)

    def _cleanup(self):
        self.audio.stop()
        if self.gui:
            self.gui.shutdown()
        if self.renderer and self.renderer.spout_sender:
            self.renderer.spout_sender.releaseSender()
        glfw.terminate()
        print("\n[App] Bye!")

    def _print_info(self):
        print(f"""
╔══════════════════════════════════════════════╗
║   AUDIOREACTIVE VISUALIZER                   ║
╠══════════════════════════════════════════════╣
║  1-5         Switch mode                     ║
║  ←/→         Cycle presets                   ║
║  ↑/↓         Sensitivity ±                   ║
║  F           Fullscreen                      ║
║  S           Toggle Spout                    ║
║  R           Reset feedback                  ║
║  H           Toggle HUD                      ║
║  Tab         Toggle parameters               ║
║  Space       Pause                           ║
║  Esc         Quit                            ║
╠══════════════════════════════════════════════╣""")
        for i, name in enumerate(MODE_NAMES):
            print(f"║  [{i+1}] {name:38s} ║")
        print(f"╚══════════════════════════════════════════════╝")
        print(f"\n  → {self.presets.info()}\n")


# ─── Entry point ───

def main():
    if "--list-devices" in sys.argv:
        AudioEngine.list_devices()
        return

    app = App()
    app.run()


if __name__ == "__main__":
    main()

"""
Preset Manager — 5 modes × 4 presets each = 20 presets
Each preset defines colors, shader parameters, and feedback settings.
"""


def hex_to_rgb(h):
    """Convert '#RRGGBB' to (r, g, b) floats 0-1."""
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) / 255.0 for i in (0, 2, 4))


# ─── Mode indices ───
MODE_FLUID = 0
MODE_PARTICLES = 1
MODE_REACTION = 2
MODE_KALEIDOSCOPE = 3
MODE_GLITCH = 4

MODE_NAMES = [
    "Fluid Noise",
    "Particles",
    "Reaction-Diffusion",
    "Kaleidoscope",
    "Glitch HUD"
]

SHADER_FILES = [
    "fluid_noise.frag",
    "particles.frag",
    "reaction_diffusion.frag",
    "kaleidoscope.frag",
    "glitch_hud.frag"
]


def _p(name, mode, c1, c2, c3, params, feedback=0.0, speed=1.0):
    return {
        "name": name,
        "mode": mode,
        "color1": hex_to_rgb(c1),
        "color2": hex_to_rgb(c2),
        "color3": hex_to_rgb(c3),
        "params": params,       # vec4: shader-specific (x,y,z,w)
        "feedback": feedback,   # 0-1: previous frame blend
        "speed": speed,         # time multiplier
    }


# ══════════════════════════════════════════════════════════
#  PRESETS — params meaning per mode:
#
#  Fluid:    (octaves_intensity, warp_amount, height_scale, color_spread)
#  Particles:(density, trail_length, glow_size, connection_dist)
#  Reaction: (feed_rate, kill_rate, diffusion_a, diffusion_b)
#  Kaleidoscope: (segments, inner_zoom, rotation_speed, shape_complexity)
#  Glitch:   (grid_density, scanline_intensity, glitch_amount, data_density)
# ══════════════════════════════════════════════════════════

PRESETS = {
    # ─── MODE 0: FLUID NOISE ───
    MODE_FLUID: [
        _p("Deep Ocean",     MODE_FLUID, "#0a1628", "#0d4f6b", "#1a9bb5",
           (6.0, 1.2, 0.8, 0.6), feedback=0.05, speed=0.6),
        _p("Volcanic",       MODE_FLUID, "#1a0a00", "#c43e00", "#ffb627",
           (5.0, 1.8, 1.2, 0.8), feedback=0.02, speed=1.2),
        _p("Aurora Borealis", MODE_FLUID, "#020d1a", "#00c9a7", "#a855f7",
           (7.0, 1.5, 0.6, 1.2), feedback=0.1, speed=0.4),
        _p("Midnight Bloom", MODE_FLUID, "#0d0015", "#7c2d8e", "#ff3c8e",
           (5.0, 2.0, 0.9, 0.9), feedback=0.08, speed=0.7),
    ],

    # ─── MODE 1: PARTICLES ───
    MODE_PARTICLES: [
        _p("Nebula",         MODE_PARTICLES, "#1a0a2e", "#ff6b3d", "#ffc8a2",
           (0.7, 0.85, 0.03, 0.15), feedback=0.88, speed=0.5),
        _p("Neural Net",     MODE_PARTICLES, "#020810", "#00d4ff", "#e0f0ff",
           (0.5, 0.7, 0.02, 0.25), feedback=0.82, speed=1.0),
        _p("Fireflies",      MODE_PARTICLES, "#050805", "#c8e64a", "#ffe066",
           (0.3, 0.9, 0.04, 0.08), feedback=0.92, speed=0.3),
        _p("Stardust",       MODE_PARTICLES, "#05050f", "#b0c4de", "#ffffff",
           (0.6, 0.8, 0.025, 0.2), feedback=0.85, speed=0.7),
    ],

    # ─── MODE 2: REACTION-DIFFUSION ───
    MODE_REACTION: [
        _p("Coral Reef",     MODE_REACTION, "#1a0500", "#ff6b6b", "#ffecd2",
           (0.055, 0.062, 1.0, 0.5), feedback=0.99, speed=1.0),
        _p("Mycelium",       MODE_REACTION, "#000d05", "#00ff88", "#003322",
           (0.042, 0.065, 1.0, 0.5), feedback=0.99, speed=0.8),
        _p("Acid Bath",      MODE_REACTION, "#0a000a", "#39ff14", "#ff00ff",
           (0.06, 0.058, 1.2, 0.6), feedback=0.99, speed=1.5),
        _p("Petri Dish",     MODE_REACTION, "#0a0a14", "#6ec6ff", "#f0f0ff",
           (0.05, 0.063, 0.9, 0.45), feedback=0.99, speed=0.6),
    ],

    # ─── MODE 3: KALEIDOSCOPE ───
    MODE_KALEIDOSCOPE: [
        _p("Sacred Geometry", MODE_KALEIDOSCOPE, "#0d0a1a", "#d4a843", "#f5e6c8",
           (12.0, 2.5, 0.3, 3.0), feedback=0.3, speed=0.5),
        _p("Prism",          MODE_KALEIDOSCOPE, "#0a0a0a", "#ff3366", "#33ccff",
           (6.0, 1.8, 0.6, 2.0), feedback=0.2, speed=1.0),
        _p("Obsidian Mirror", MODE_KALEIDOSCOPE, "#080808", "#aaaaaa", "#ffffff",
           (4.0, 3.0, 0.2, 1.5), feedback=0.4, speed=0.4),
        _p("Neon Mandala",   MODE_KALEIDOSCOPE, "#05000d", "#ff00aa", "#00ffcc",
           (8.0, 2.0, 0.8, 2.5), feedback=0.25, speed=0.8),
    ],

    # ─── MODE 4: GLITCH HUD ───
    MODE_GLITCH: [
        _p("PHASE(S)",       MODE_GLITCH, "#0d0015", "#a855f7", "#00e5ff",
           (20.0, 0.8, 0.6, 0.7), feedback=0.15, speed=1.0),
        _p("Matrix Terminal", MODE_GLITCH, "#000a00", "#00ff41", "#003300",
           (30.0, 0.6, 0.4, 0.9), feedback=0.2, speed=1.2),
        _p("Surveillance",   MODE_GLITCH, "#0a0a0a", "#8899aa", "#556677",
           (15.0, 1.0, 0.5, 0.5), feedback=0.1, speed=0.6),
        _p("Vaporwave",      MODE_GLITCH, "#1a0028", "#ff71ce", "#01cdfe",
           (12.0, 0.5, 0.7, 0.6), feedback=0.18, speed=0.8),
    ],
}


class PresetManager:
    def __init__(self):
        self.current_mode = MODE_FLUID
        self.current_preset_idx = 0

    @property
    def preset(self):
        return PRESETS[self.current_mode][self.current_preset_idx]

    @property
    def mode_name(self):
        return MODE_NAMES[self.current_mode]

    @property
    def preset_name(self):
        return self.preset["name"]

    @property
    def shader_file(self):
        return SHADER_FILES[self.current_mode]

    def set_mode(self, mode):
        if 0 <= mode < len(MODE_NAMES):
            self.current_mode = mode
            self.current_preset_idx = 0
            return True
        return False

    def next_preset(self):
        presets = PRESETS[self.current_mode]
        self.current_preset_idx = (self.current_preset_idx + 1) % len(presets)

    def prev_preset(self):
        presets = PRESETS[self.current_mode]
        self.current_preset_idx = (self.current_preset_idx - 1) % len(presets)

    def info(self):
        return f"[{self.mode_name}] {self.preset_name}"

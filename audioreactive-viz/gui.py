"""
GUI — Dear ImGui overlay for real-time parameter control.
Replaces console-based parameter tweaking with visual sliders.
"""

import imgui
from imgui.integrations.glfw import GlfwRenderer
from presets import MODE_NAMES


# Parameter labels per mode (matches vec4 params x,y,z,w)
PARAM_LABELS = {
    0: ["Octaves Intensity", "Warp Amount", "Height Scale", "Color Spread"],
    1: ["Density", "Trail Length", "Glow Size", "Connection Dist"],
    2: ["Feed Rate", "Kill Rate", "Diffusion A", "Diffusion B"],
    3: ["Segments", "Inner Zoom", "Rotation Speed", "Shape Complexity"],
    4: ["Grid Density", "Scanline Intensity", "Glitch Amount", "Data Density"],
}

# Reasonable min/max ranges per mode for each param
PARAM_RANGES = {
    0: [(1.0, 10.0), (0.0, 4.0), (0.0, 2.0), (0.0, 2.0)],
    1: [(0.1, 1.0), (0.1, 1.0), (0.005, 0.1), (0.02, 0.4)],
    2: [(0.01, 0.1), (0.03, 0.08), (0.5, 2.0), (0.2, 1.0)],
    3: [(2.0, 24.0), (0.5, 5.0), (0.0, 2.0), (1.0, 5.0)],
    4: [(5.0, 50.0), (0.0, 2.0), (0.0, 1.0), (0.0, 1.0)],
}


class GUI:
    def __init__(self, window):
        imgui.create_context()
        self.impl = GlfwRenderer(window, attach_callbacks=False)
        self.visible = True

        # Live override values (None = use preset default)
        self.overrides = {
            "params": [None, None, None, None],
            "feedback": None,
            "speed": None,
            "sensitivity": None,
            "smoothing": None,
            "beat_threshold": None,
            "beat_decay": None,
        }

        # Track which values are being overridden
        self._initialized_from_preset = False
        self._current_mode = -1
        self._current_preset_idx = -1
        self._cached_preset = {}  # reused dict to avoid per-frame alloc

    def _sync_from_preset(self, preset, mode, preset_idx, audio):
        """Reset overrides when preset/mode changes."""
        if mode != self._current_mode or preset_idx != self._current_preset_idx:
            self.overrides["params"] = list(preset["params"])
            self.overrides["feedback"] = preset["feedback"]
            self.overrides["speed"] = preset["speed"]
            self.overrides["sensitivity"] = audio.sensitivity
            self.overrides["smoothing"] = audio.smoothing
            self.overrides["beat_threshold"] = audio._beat_threshold
            self.overrides["beat_decay"] = audio._beat_decay
            self._current_mode = mode
            self._current_preset_idx = preset_idx
            self._initialized_from_preset = True

    def process_inputs(self):
        """Call before glfw.poll_events or after — feeds input to imgui."""
        self.impl.process_inputs()

    def wants_keyboard(self):
        """Returns True if imgui wants keyboard (user typing in a widget)."""
        return imgui.get_io().want_capture_keyboard

    def wants_mouse(self):
        """Returns True if imgui wants mouse (hovering/clicking UI)."""
        return imgui.get_io().want_capture_mouse

    def render(self, app):
        """Draw the full parameter panel. Call once per frame."""
        if not self.visible:
            imgui.new_frame()
            imgui.render()
            self.impl.render(imgui.get_draw_data())
            return

        preset = app.presets.preset
        mode = app.presets.current_mode
        preset_idx = app.presets.current_preset_idx

        # Sync overrides on preset change
        self._sync_from_preset(preset, mode, preset_idx, app.audio)

        imgui.new_frame()

        imgui.set_next_window_position(10, 10, imgui.FIRST_USE_EVER)
        imgui.set_next_window_size(320, 0, imgui.FIRST_USE_EVER)

        imgui.begin("Parameters", flags=imgui.WINDOW_NO_SAVED_SETTINGS)

        # ─── Mode & Preset ───
        imgui.text_colored(f"Mode: {MODE_NAMES[mode]}", 0.4, 0.8, 1.0)
        imgui.text(f"Preset: {preset['name']}")
        imgui.separator()

        # ─── Shader Parameters (vec4) ───
        if imgui.collapsing_header("Shader Parameters", imgui.TREE_NODE_DEFAULT_OPEN)[0]:
            labels = PARAM_LABELS.get(mode, ["Param X", "Param Y", "Param Z", "Param W"])
            ranges = PARAM_RANGES.get(mode, [(0, 1)] * 4)
            for i in range(4):
                lo, hi = ranges[i]
                changed, val = imgui.slider_float(
                    labels[i], self.overrides["params"][i], lo, hi,
                    format="%.4f" if hi < 1 else "%.2f"
                )
                if changed:
                    self.overrides["params"][i] = val

        # ─── Feedback & Speed ───
        if imgui.collapsing_header("Feedback & Speed", imgui.TREE_NODE_DEFAULT_OPEN)[0]:
            changed, val = imgui.slider_float("Feedback", self.overrides["feedback"], 0.0, 1.0, "%.3f")
            if changed:
                self.overrides["feedback"] = val

            changed, val = imgui.slider_float("Speed", self.overrides["speed"], 0.0, 3.0, "%.2f")
            if changed:
                self.overrides["speed"] = val

        # ─── Audio Settings ───
        if imgui.collapsing_header("Audio Settings", imgui.TREE_NODE_DEFAULT_OPEN)[0]:
            changed, val = imgui.slider_float("Sensitivity", self.overrides["sensitivity"], 0.1, 5.0, "%.2f")
            if changed:
                self.overrides["sensitivity"] = val
                app.audio.sensitivity = val

            changed, val = imgui.slider_float("Smoothing", self.overrides["smoothing"], 0.01, 0.5, "%.3f")
            if changed:
                self.overrides["smoothing"] = val
                app.audio.smoothing = val

            changed, val = imgui.slider_float("Beat Threshold", self.overrides["beat_threshold"], 0.05, 1.0, "%.3f")
            if changed:
                self.overrides["beat_threshold"] = val
                app.audio._beat_threshold = val

            changed, val = imgui.slider_float("Beat Decay", self.overrides["beat_decay"], 0.8, 0.99, "%.3f")
            if changed:
                self.overrides["beat_decay"] = val
                app.audio._beat_decay = val

        # ─── Audio Levels (read-only meters) ───
        if imgui.collapsing_header("Audio Levels")[0]:
            imgui.progress_bar(app.audio.bass, (280, 0), f"Bass  {app.audio.bass:.3f}")
            imgui.progress_bar(app.audio.mid, (280, 0), f"Mid   {app.audio.mid:.3f}")
            imgui.progress_bar(app.audio.high, (280, 0), f"High  {app.audio.high:.3f}")
            imgui.progress_bar(app.audio.rms, (280, 0), f"RMS   {app.audio.rms:.3f}")
            imgui.progress_bar(app.audio.beat, (280, 0), f"Beat  {app.audio.beat:.3f}")

        # ─── Reset button ───
        imgui.separator()
        if imgui.button("Reset to Preset Defaults"):
            self._current_mode = -1  # force re-sync

        imgui.same_line()
        if imgui.button("Reset Feedback"):
            app.renderer.reset_feedback()

        imgui.separator()
        imgui.text_colored("Tab to toggle panel", 0.5, 0.5, 0.5)

        imgui.end()

        imgui.render()
        self.impl.render(imgui.get_draw_data())

    def get_preset_override(self, preset):
        """Return a modified preset dict with current slider values applied."""
        if not self._initialized_from_preset:
            return preset

        p = self._cached_preset
        p.update(preset)
        p["params"] = tuple(self.overrides["params"])
        p["feedback"] = self.overrides["feedback"]
        p["speed"] = self.overrides["speed"]
        return p

    def shutdown(self):
        self.impl.shutdown()

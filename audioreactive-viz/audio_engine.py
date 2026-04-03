"""
Audio Engine — Capture audio + FFT analysis
Outputs smoothed bass/mid/high/rms/beat values + spectrum texture data
"""

import numpy as np
import sounddevice as sd
import threading


class AudioEngine:
    def __init__(self, device=None, sample_rate=44100, block_size=1024, smoothing=0.15):
        self.sample_rate = sample_rate
        self.block_size = block_size
        self.smoothing = smoothing

        # Raw FFT buffer
        self._buffer = np.zeros(block_size, dtype=np.float32)
        self._lock = threading.Lock()

        # Smoothed outputs
        self.bass = 0.0
        self.mid = 0.0
        self.high = 0.0
        self.rms = 0.0
        self.beat = 0.0
        self.spectrum = np.zeros(512, dtype=np.float32)

        # Beat detection state
        self._prev_bass = 0.0
        self._beat_decay = 0.92
        self._beat_threshold = 0.3

        # Sensitivity multiplier (adjustable at runtime)
        self.sensitivity = 1.5

        # Pre-computed DSP arrays (avoid per-frame allocation)
        self._window = np.hanning(block_size).astype(np.float32)
        freqs = np.fft.rfftfreq(block_size, 1.0 / sample_rate)
        self._bass_mask = (freqs >= 20) & (freqs < 250)
        self._mid_mask = (freqs >= 250) & (freqs < 4000)
        self._high_mask = (freqs >= 4000) & (freqs < 16000)
        self._spectrum_indices = np.linspace(0, len(freqs) - 1, 512)
        self._fft_arange = np.arange(len(freqs))

        # Find device
        self.device = device
        self.stream = None

    def start(self):
        try:
            self.stream = sd.InputStream(
                device=self.device,
                channels=1,
                samplerate=self.sample_rate,
                blocksize=self.block_size,
                callback=self._audio_callback,
                dtype='float32'
            )
            self.stream.start()
            print(f"[Audio] Started — device: {self.stream.device}, sr: {self.sample_rate}")
            return True
        except Exception as e:
            print(f"[Audio] Error starting stream: {e}")
            print("[Audio] Available devices:")
            print(sd.query_devices())
            return False

    def stop(self):
        if self.stream:
            self.stream.stop()
            self.stream.close()

    def _audio_callback(self, indata, frames, time_info, status):
        if status:
            pass  # ignore xruns silently
        with self._lock:
            self._buffer[:] = indata[:, 0]

    def update(self):
        """Call once per frame to compute smoothed audio features."""
        with self._lock:
            samples = self._buffer.copy()

        # Windowed FFT (pre-computed window + masks)
        fft = np.abs(np.fft.rfft(samples * self._window))
        fft_db = np.clip(20.0 * np.log10(fft + 1e-10) + 60.0, 0.0, 60.0) / 60.0

        # Band energies (pre-computed masks)
        sens = self.sensitivity
        raw_bass = float(np.mean(fft_db[self._bass_mask])) * sens
        raw_mid = float(np.mean(fft_db[self._mid_mask])) * sens
        raw_high = float(np.mean(fft_db[self._high_mask])) * sens
        raw_rms = float(np.sqrt(np.mean(samples * samples))) * sens * 5.0

        # Smooth (scalar math, no np.clip overhead)
        s = self.smoothing
        inv_s = 1.0 - s
        self.bass = self.bass * inv_s + min(max(raw_bass, 0.0), 1.0) * s
        self.mid = self.mid * inv_s + min(max(raw_mid, 0.0), 1.0) * s
        self.high = self.high * inv_s + min(max(raw_high, 0.0), 1.0) * s
        self.rms = self.rms * inv_s + min(max(raw_rms, 0.0), 1.0) * s

        # Beat detection (onset on bass)
        bass_delta = self.bass - self._prev_bass
        if bass_delta > self._beat_threshold:
            self.beat = min(1.0, self.beat + bass_delta * 2.0)
        else:
            self.beat *= self._beat_decay
        self._prev_bass = self.bass

        # Spectrum texture (pre-computed indices)
        if len(fft_db) > 1:
            self.spectrum = np.interp(self._spectrum_indices, self._fft_arange, fft_db).astype(np.float32)

    @staticmethod
    def list_devices():
        print(sd.query_devices())

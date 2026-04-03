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

        # Windowed FFT
        window = np.hanning(len(samples))
        fft = np.abs(np.fft.rfft(samples * window))
        fft_db = np.clip(20.0 * np.log10(fft + 1e-10) + 60.0, 0.0, 60.0) / 60.0

        # Frequency bins
        freqs = np.fft.rfftfreq(len(samples), 1.0 / self.sample_rate)

        # Band energies
        bass_mask = (freqs >= 20) & (freqs < 250)
        mid_mask = (freqs >= 250) & (freqs < 4000)
        high_mask = (freqs >= 4000) & (freqs < 16000)

        raw_bass = np.mean(fft_db[bass_mask]) * self.sensitivity if np.any(bass_mask) else 0.0
        raw_mid = np.mean(fft_db[mid_mask]) * self.sensitivity if np.any(mid_mask) else 0.0
        raw_high = np.mean(fft_db[high_mask]) * self.sensitivity if np.any(high_mask) else 0.0
        raw_rms = np.sqrt(np.mean(samples ** 2)) * self.sensitivity * 5.0

        # Smooth
        s = self.smoothing
        self.bass = self.bass * (1 - s) + np.clip(raw_bass, 0, 1) * s
        self.mid = self.mid * (1 - s) + np.clip(raw_mid, 0, 1) * s
        self.high = self.high * (1 - s) + np.clip(raw_high, 0, 1) * s
        self.rms = self.rms * (1 - s) + np.clip(raw_rms, 0, 1) * s

        # Beat detection (onset on bass)
        bass_delta = self.bass - self._prev_bass
        if bass_delta > self._beat_threshold:
            self.beat = min(1.0, self.beat + bass_delta * 2.0)
        else:
            self.beat *= self._beat_decay
        self._prev_bass = self.bass

        # Spectrum texture (resample to 512 bins, normalized)
        if len(fft_db) > 1:
            indices = np.linspace(0, len(fft_db) - 1, 512)
            self.spectrum = np.interp(indices, np.arange(len(fft_db)), fft_db).astype(np.float32)

    @staticmethod
    def list_devices():
        print(sd.query_devices())

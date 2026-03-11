"""
Test suite — utils/signal_processing.py
Copre: taper_signal, bandpass_filter, compute_fft, compute_psd,
       compute_spectrogram, compute_sta_lta, detect_p_wave, spectral_metrics.
"""

import unittest
import numpy as np

from utils.signal_processing import (
    taper_signal,
    bandpass_filter,
    compute_fft,
    compute_psd,
    compute_spectrogram,
    compute_sta_lta,
    detect_p_wave,
    spectral_metrics,
)


# ─────────────────────────────────────────────────────────────────────────────
# Segnali di test riutilizzabili
# ─────────────────────────────────────────────────────────────────────────────

FS = 100.0                         # Hz
DURATION = 10.0                    # s
N = int(FS * DURATION)
T = np.linspace(0, DURATION, N, endpoint=False)

SINE_10HZ    = np.sin(2 * np.pi * 10.0 * T)   # puro 10 Hz
NOISE        = np.random.default_rng(0).normal(0, 1, N)
IMPULSE      = np.zeros(N); IMPULSE[N // 2] = 1.0
RAMP         = np.linspace(-1, 1, N)


# ─────────────────────────────────────────────────────────────────────────────
# taper_signal
# ─────────────────────────────────────────────────────────────────────────────

class TestTaperSignal(unittest.TestCase):

    def test_output_length_unchanged(self):
        out = taper_signal(SINE_10HZ.copy())
        self.assertEqual(len(out), len(SINE_10HZ))

    def test_edges_forced_toward_zero(self):
        out = taper_signal(RAMP.copy(), p=0.10)
        self.assertAlmostEqual(out[0], 0.0, delta=1e-6)
        self.assertAlmostEqual(out[-1], 0.0, delta=1e-6)

    def test_centre_unaffected(self):
        """Con taper del 5 % il centro deve rimanere quasi invariato."""
        out = taper_signal(RAMP.copy(), p=0.05)
        mid = N // 2
        self.assertAlmostEqual(out[mid], RAMP[mid], delta=1e-3)

    def test_returns_ndarray(self):
        out = taper_signal(NOISE.copy())
        self.assertIsInstance(out, np.ndarray)

    def test_zero_taper_unchanged(self):
        out = taper_signal(SINE_10HZ.copy(), p=0.0)
        np.testing.assert_allclose(out, SINE_10HZ, rtol=1e-6)

    def test_dtype_preserved(self):
        data = SINE_10HZ.astype(np.float32)
        out = taper_signal(data, p=0.05)
        # deve rimanere float (numpy broadcastato a float64 o float32)
        self.assertTrue(np.issubdtype(out.dtype, np.floating))


# ─────────────────────────────────────────────────────────────────────────────
# bandpass_filter
# ─────────────────────────────────────────────────────────────────────────────

class TestBandpassFilter(unittest.TestCase):

    def test_output_length_unchanged(self):
        out = bandpass_filter(SINE_10HZ.copy(), 5.0, 20.0, FS)
        self.assertEqual(len(out), N)

    def test_passes_in_band_frequency(self):
        """10 Hz all'interno di [5, 20] Hz: ampiezza quasi invariata."""
        out = bandpass_filter(SINE_10HZ.copy(), 5.0, 20.0, FS)
        ratio = float(np.std(out)) / float(np.std(SINE_10HZ))
        self.assertAlmostEqual(ratio, 1.0, delta=0.05)

    def test_attenuates_out_of_band(self):
        """Segnale 40 Hz fuori da [5, 20] Hz: ampiezza drasticamente ridotta."""
        sine_40hz = np.sin(2 * np.pi * 40.0 * T)
        out = bandpass_filter(sine_40hz, 5.0, 20.0, FS)
        self.assertLess(np.std(out), 0.05)

    def test_f_high_above_nyquist_raises(self):
        with self.assertRaises(ValueError):
            bandpass_filter(SINE_10HZ.copy(), 5.0, FS / 2 + 1, FS)

    def test_f_low_zero_raises(self):
        with self.assertRaises(ValueError):
            bandpass_filter(SINE_10HZ.copy(), 0.0, 20.0, FS)

    def test_f_low_greater_than_f_high_raises(self):
        with self.assertRaises(ValueError):
            bandpass_filter(SINE_10HZ.copy(), 30.0, 10.0, FS)

    def test_returns_ndarray(self):
        out = bandpass_filter(NOISE.copy(), 1.0, 10.0, FS)
        self.assertIsInstance(out, np.ndarray)

    def test_zero_phase_symmetric_impulse(self):
        """Il filtro zero-phase applicato a un impulso centrato deve essere simmetrico."""
        out = bandpass_filter(IMPULSE.copy(), 1.0, 10.0, FS)
        mid = N // 2
        # Verifica simmetria approssimativa attorno al centro (entro 10 campioni)
        left  = out[mid - 20: mid]
        right = out[mid + 1: mid + 21]
        np.testing.assert_allclose(left, right[::-1], atol=1e-6)


# ─────────────────────────────────────────────────────────────────────────────
# compute_fft
# ─────────────────────────────────────────────────────────────────────────────

class TestComputeFFT(unittest.TestCase):

    def setUp(self):
        self.freqs, self.amps, self.phases = compute_fft(SINE_10HZ.copy(), FS)

    def test_returns_three_arrays(self):
        result = compute_fft(SINE_10HZ.copy(), FS)
        self.assertEqual(len(result), 3)

    def test_peak_at_10hz(self):
        peak_idx = np.argmax(self.amps)
        peak_freq = self.freqs[peak_idx]
        self.assertAlmostEqual(peak_freq, 10.0, delta=0.5)

    def test_freqs_start_at_zero(self):
        self.assertAlmostEqual(self.freqs[0], 0.0)

    def test_freqs_max_is_nyquist(self):
        self.assertAlmostEqual(self.freqs[-1], FS / 2, delta=1.0)

    def test_amplitudes_non_negative(self):
        self.assertTrue(np.all(self.amps >= 0))

    def test_phases_range(self):
        self.assertTrue(np.all(self.phases >= -180.1))
        self.assertTrue(np.all(self.phases <= 180.1))

    def test_length_consistent(self):
        self.assertEqual(len(self.freqs), len(self.amps))
        self.assertEqual(len(self.freqs), len(self.phases))

    def test_dc_component_near_zero_for_sine(self):
        """Un seno puro non ha componente DC significativa."""
        self.assertLess(self.amps[0], 0.05)


# ─────────────────────────────────────────────────────────────────────────────
# compute_psd
# ─────────────────────────────────────────────────────────────────────────────

class TestComputePSD(unittest.TestCase):

    def setUp(self):
        self.f, self.psd = compute_psd(SINE_10HZ.copy(), FS)

    def test_returns_two_arrays(self):
        result = compute_psd(SINE_10HZ.copy(), FS)
        self.assertEqual(len(result), 2)

    def test_peak_near_10hz(self):
        peak_idx = np.argmax(self.psd)
        self.assertAlmostEqual(self.f[peak_idx], 10.0, delta=1.0)

    def test_psd_non_negative(self):
        self.assertTrue(np.all(self.psd >= 0))

    def test_lengths_match(self):
        self.assertEqual(len(self.f), len(self.psd))

    def test_white_noise_flat_psd(self):
        """Rumore bianco: PSD deve essere approssimativamente piatta."""
        rng = np.random.default_rng(42)
        white = rng.normal(0, 1, N)
        f, psd = compute_psd(white, FS)
        # Coefficiente di variazione < 1.0 (piatto = CV basso)
        cv = np.std(psd) / (np.mean(psd) + 1e-12)
        self.assertLess(cv, 1.0)


# ─────────────────────────────────────────────────────────────────────────────
# compute_spectrogram
# ─────────────────────────────────────────────────────────────────────────────

class TestComputeSpectrogram(unittest.TestCase):

    def setUp(self):
        self.t, self.f, self.Sxx = compute_spectrogram(SINE_10HZ.copy(), FS)

    def test_returns_three_arrays(self):
        result = compute_spectrogram(SINE_10HZ.copy(), FS)
        self.assertEqual(len(result), 3)

    def test_sxx_is_2d(self):
        self.assertEqual(self.Sxx.ndim, 2)

    def test_sxx_non_negative(self):
        self.assertTrue(np.all(self.Sxx >= 0))

    def test_sxx_shape_consistent(self):
        self.assertEqual(self.Sxx.shape, (len(self.f), len(self.t)))

    def test_peak_frequency_at_10hz(self):
        mean_spectrum = np.mean(self.Sxx, axis=1)
        peak_idx = np.argmax(mean_spectrum)
        self.assertAlmostEqual(self.f[peak_idx], 10.0, delta=2.0)

    def test_custom_nperseg(self):
        t, f, Sxx = compute_spectrogram(SINE_10HZ.copy(), FS, nperseg=64)
        self.assertEqual(Sxx.ndim, 2)


# ─────────────────────────────────────────────────────────────────────────────
# compute_sta_lta
# ─────────────────────────────────────────────────────────────────────────────

class TestComputeStaLta(unittest.TestCase):

    def _signal_with_onset(self, onset_s: float = 5.0) -> np.ndarray:
        """Rumore basso, poi segnale forte dopo onset_s."""
        sig = np.random.default_rng(1).normal(0, 0.1, N)
        onset = int(onset_s * FS)
        sig[onset:] += np.sin(2 * np.pi * 5.0 * T[onset:]) * 5.0
        return sig

    def test_output_length_same_as_input(self):
        out = compute_sta_lta(SINE_10HZ.copy(), FS)
        self.assertEqual(len(out), N)

    def test_non_negative(self):
        out = compute_sta_lta(SINE_10HZ.copy(), FS)
        self.assertTrue(np.all(out >= 0))

    def test_spike_at_onset(self):
        """Il massimo STA/LTA deve essere vicino all'onset del segnale."""
        onset_s = 5.0
        sig = self._signal_with_onset(onset_s)
        stalta = compute_sta_lta(sig, FS, sta_s=0.5, lta_s=5.0)
        peak_s = float(np.argmax(stalta)) / FS
        self.assertAlmostEqual(peak_s, onset_s, delta=1.5)

    def test_constant_signal_near_one(self):
        """Segnale costante: STA/LTA ≈ 1.0 dopo la fase di riempimento LTA."""
        const = np.ones(N) * 3.0
        stalta = compute_sta_lta(const, FS, sta_s=0.5, lta_s=5.0)
        lta_n = int(5.0 * FS)
        valid = stalta[lta_n:]
        np.testing.assert_allclose(valid, 1.0, atol=1e-6)

    def test_sta_shorter_than_lta(self):
        """Non deve sollevare eccezioni con finestre tipiche."""
        out = compute_sta_lta(NOISE.copy(), FS, sta_s=1.0, lta_s=20.0)
        self.assertEqual(len(out), N)


# ─────────────────────────────────────────────────────────────────────────────
# detect_p_wave
# ─────────────────────────────────────────────────────────────────────────────

class TestDetectPWave(unittest.TestCase):

    def _signal_with_onset(self, onset_s: float = 4.0) -> np.ndarray:
        sig = np.random.default_rng(7).normal(0, 0.05, N)
        onset = int(onset_s * FS)
        sig[onset:] += np.sin(2 * np.pi * 5.0 * T[onset:]) * 10.0
        return sig

    def test_detects_onset(self):
        onset_s = 4.0
        sig = self._signal_with_onset(onset_s)
        detected = detect_p_wave(sig, FS, sta_s=0.5, lta_s=4.0, threshold=3.0)
        self.assertIsNotNone(detected)
        self.assertAlmostEqual(detected, onset_s, delta=1.5)

    def test_returns_float_when_found(self):
        sig = self._signal_with_onset()
        result = detect_p_wave(sig, FS, threshold=2.0)
        if result is not None:
            self.assertIsInstance(result, float)

    def test_returns_none_on_quiet_signal(self):
        """Segnale costante: nessun trigger deve essere rilevato."""
        quiet = np.ones(N) * 0.001
        result = detect_p_wave(quiet, FS, threshold=100.0)
        self.assertIsNone(result)

    def test_detected_time_within_duration(self):
        sig = self._signal_with_onset()
        detected = detect_p_wave(sig, FS, threshold=2.0)
        if detected is not None:
            self.assertLessEqual(detected, DURATION)
            self.assertGreaterEqual(detected, 0.0)


# ─────────────────────────────────────────────────────────────────────────────
# spectral_metrics
# ─────────────────────────────────────────────────────────────────────────────

class TestSpectralMetrics(unittest.TestCase):

    def setUp(self):
        self.freqs, self.amps, _ = compute_fft(SINE_10HZ.copy(), FS)
        self.dom, self.cent, self.bw = spectral_metrics(self.freqs, self.amps)

    def test_dominant_frequency_at_10hz(self):
        self.assertAlmostEqual(self.dom, 10.0, delta=0.5)

    def test_centroid_near_10hz(self):
        self.assertAlmostEqual(self.cent, 10.0, delta=2.0)

    def test_bandwidth_non_negative(self):
        self.assertGreaterEqual(self.bw, 0.0)

    def test_returns_three_floats(self):
        result = spectral_metrics(self.freqs, self.amps)
        self.assertEqual(len(result), 3)
        for v in result:
            self.assertIsInstance(v, float)

    def test_uniform_spectrum_centroid_at_nyquist_half(self):
        """Spettro uniforme: centroide ≈ metà della frequenza massima."""
        f = np.linspace(0, FS / 2, 100)
        a = np.ones(100)
        _, centroid, _ = spectral_metrics(f, a)
        self.assertAlmostEqual(centroid, FS / 4, delta=2.0)

    def test_zero_amplitude_returns_finite(self):
        f = np.linspace(0, 50, 100)
        a = np.zeros(100)
        dom, cent, bw = spectral_metrics(f, a)
        self.assertTrue(np.isfinite(dom))
        self.assertTrue(np.isfinite(cent))
        self.assertTrue(np.isfinite(bw))


if __name__ == "__main__":
    unittest.main(verbosity=2)


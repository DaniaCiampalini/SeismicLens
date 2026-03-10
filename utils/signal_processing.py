"""
Signal processing utilities for SeismicLens.
Wraps SciPy routines with seismology-specific defaults.
"""

import numpy as np
from scipy import signal as sp_signal
from scipy.fft import rfft, rfftfreq


# ── Tapering ─────────────────────────────────────────────────────────────────

def taper_signal(data: np.ndarray, p: float = 0.05) -> np.ndarray:
    """
    Apply a cosine taper to both ends of the signal (Tukey window).

    Parameters
    ----------
    data : array_like
        Raw signal samples.
    p : float
        Fraction of the signal to taper on each side (default 5%).

    Returns
    -------
    np.ndarray
        Tapered signal.
    """
    window = sp_signal.windows.tukey(len(data), alpha=2 * p)
    return data * window


# ── Bandpass filter ──────────────────────────────────────────────────────────

def bandpass_filter(
        data: np.ndarray,
        f_low: float,
        f_high: float,
        fs: float,
        order: int = 4,
) -> np.ndarray:
    """
    Zero-phase Butterworth bandpass filter.

    Parameters
    ----------
    data    : input signal
    f_low   : lower corner frequency (Hz)
    f_high  : upper corner frequency (Hz)
    fs      : sampling rate (Hz)
    order   : filter order (applied twice due to zero-phase → effective 2×order)

    Returns
    -------
    np.ndarray
        Filtered signal.
    """
    nyq = fs / 2.0
    if f_high >= nyq:
        raise ValueError(f"High-cut {f_high} Hz >= Nyquist {nyq} Hz")
    if f_low <= 0:
        raise ValueError("Low-cut must be > 0 Hz")
    if f_low >= f_high:
        raise ValueError("Low-cut must be < high-cut")

    sos = sp_signal.butter(
        order, [f_low / nyq, f_high / nyq],
        btype="band", output="sos"
    )
    return sp_signal.sosfiltfilt(sos, data)


# ── FFT ──────────────────────────────────────────────────────────────────────

def compute_fft(data: np.ndarray, fs: float):
    """
    Single-sided amplitude spectrum via real FFT.

    Returns
    -------
    freqs      : frequency axis (Hz), length N//2+1
    amplitudes : |A(f)| normalised by N
    """
    n = len(data)
    window = np.hanning(n)
    fft_vals = rfft(data * window)
    amplitudes = (2.0 / n) * np.abs(fft_vals)
    freqs = rfftfreq(n, d=1.0 / fs)
    return freqs, amplitudes


# ── Spectrogram ──────────────────────────────────────────────────────────────

def compute_spectrogram(data: np.ndarray, fs: float, nperseg: int = None):
    """
    Short-Time Fourier Transform spectrogram.

    Returns
    -------
    t   : time axis
    f   : frequency axis
    Sxx : power spectral density matrix
    """
    if nperseg is None:
        # Aim for ~256 frequency bins, but no longer than signal
        nperseg = min(256, len(data) // 4)
    f, t, Sxx = sp_signal.spectrogram(data, fs=fs, nperseg=nperseg,
                                      window="hann", noverlap=nperseg // 2)
    return t, f, Sxx


# ── STA/LTA ──────────────────────────────────────────────────────────────────

def compute_sta_lta(
        data: np.ndarray,
        fs: float,
        sta_s: float = 1.0,
        lta_s: float = 20.0,
) -> np.ndarray:
    """
    Classic recursive STA/LTA characteristic function for event detection.

    Parameters
    ----------
    data  : signal samples
    fs    : sampling rate (Hz)
    sta_s : short-term average window length (seconds)
    lta_s : long-term average window length (seconds)

    Returns
    -------
    np.ndarray
        STA/LTA ratio time series (same length as data).
    """
    sta_n = max(1, int(sta_s * fs))
    lta_n = max(sta_n + 1, int(lta_s * fs))

    data2 = data ** 2  # energy
    n = len(data2)
    stalta = np.zeros(n)

    # Cumulative sum approach — O(N)
    cs = np.cumsum(np.concatenate([[0], data2]))

    for i in range(lta_n, n):
        sta = (cs[i + 1] - cs[i - sta_n + 1]) / sta_n
        lta = (cs[i + 1] - cs[i - lta_n + 1]) / lta_n
        stalta[i] = sta / lta if lta > 0 else 0.0

    return stalta


def detect_p_wave(
        data: np.ndarray,
        fs: float,
        sta_s: float = 1.0,
        lta_s: float = 20.0,
        threshold: float = 3.5,
) -> float | None:
    """
    Return the time (seconds) of the first STA/LTA trigger above threshold,
    or None if no trigger is found.
    """
    stalta = compute_sta_lta(data, fs, sta_s, lta_s)
    indices = np.where(stalta > threshold)[0]
    if len(indices) == 0:
        return None
    return float(indices[0]) / fs

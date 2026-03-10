"""
Data loading utilities for SeismicLens.
Supports MiniSEED (via ObsPy), CSV, and synthetic earthquake generation.
"""

import numpy as np
import pandas as pd
import io
from typing import Tuple


# ── MiniSEED ─────────────────────────────────────────────────────────────────

def load_mseed(file_obj) -> Tuple[np.ndarray, float, dict]:
    """
    Load a MiniSEED file using ObsPy.

    Returns
    -------
    signal   : numpy array of samples (first trace, detrended)
    fs       : sampling rate (Hz)
    metadata : dict with network/station/channel/starttime info
    """
    try:
        from obspy import read
    except ImportError:
        raise ImportError(
            "ObsPy is required for MiniSEED support. "
            "Install it with: pip install obspy"
        )

    buf = io.BytesIO(file_obj.read())
    st = read(buf)
    st.detrend("demean")

    tr = st[0]
    signal = tr.data.astype(np.float64)
    fs = float(tr.stats.sampling_rate)

    metadata = {
        "network":   tr.stats.network,
        "station":   tr.stats.station,
        "location":  tr.stats.location,
        "channel":   tr.stats.channel,
        "starttime": str(tr.stats.starttime),
        "endtime":   str(tr.stats.endtime),
        "npts":      int(tr.stats.npts),
        "sampling_rate_hz": fs,
    }

    return signal, fs, metadata


# ── CSV ──────────────────────────────────────────────────────────────────────

def load_csv_signal(file_obj) -> Tuple[np.ndarray, float, dict]:
    """
    Load a seismic signal from a CSV file.

    Expected formats (auto-detected):
      - Single column: amplitude values only (fs assumed 100 Hz)
      - Two columns:   time(s), amplitude  → fs inferred from time column
      - Column names are flexible (time/t/seconds + amplitude/amp/counts/data)

    Returns
    -------
    signal   : numpy array of amplitude values
    fs       : sampling rate in Hz
    metadata : basic info dict
    """
    df = pd.read_csv(file_obj)
    df.columns = [c.strip().lower() for c in df.columns]

    time_cols = [c for c in df.columns if any(k in c for k in ["time", "t", "sec", "s"])]
    amp_cols  = [c for c in df.columns if any(k in c for k in ["amp", "count", "data", "val", "y"])]

    if len(df.columns) == 1:
        signal = df.iloc[:, 0].to_numpy(dtype=np.float64)
        fs = 100.0
    elif time_cols and amp_cols:
        t_arr = df[time_cols[0]].to_numpy(dtype=np.float64)
        signal = df[amp_cols[0]].to_numpy(dtype=np.float64)
        dt_median = np.median(np.diff(t_arr))
        fs = 1.0 / dt_median if dt_median > 0 else 100.0
    else:
        # Fall back: assume col 0 = time, col 1 = amplitude
        t_arr = df.iloc[:, 0].to_numpy(dtype=np.float64)
        signal = df.iloc[:, 1].to_numpy(dtype=np.float64)
        dt_median = np.median(np.diff(t_arr))
        fs = 1.0 / dt_median if dt_median > 0 else 100.0

    # Remove NaNs
    signal = np.nan_to_num(signal)

    metadata = {
        "source":      "CSV upload",
        "n_samples":   len(signal),
        "sampling_rate_hz": round(fs, 4),
        "duration_s":  round(len(signal) / fs, 2),
    }
    return signal, fs, metadata


# ── Synthetic earthquake ─────────────────────────────────────────────────────

def generate_synthetic_quake(
        magnitude: float = 5.5,
        depth_km:  float = 30.0,
        noise_level: float = 0.15,
        duration_s:  float = 120.0,
        fs:          float = 100.0,
) -> Tuple[np.ndarray, float, dict]:
    """
    Generate a physically-inspired synthetic earthquake waveform.

    Model
    -----
    - Pre-event noise
    - P-wave onset: high-frequency, low-amplitude pulse
    - S-wave onset: lower-frequency, higher-amplitude phase
    - Surface waves: long-period coda
    - Superimposed broadband noise

    The arrival times are estimated from a simple velocity model:
        Vp ≈ 6 km/s,  Vs ≈ 3.5 km/s (crustal average)
    """
    rng = np.random.default_rng(seed=42)
    n = int(duration_s * fs)
    t = np.linspace(0, duration_s, n)

    # Epicentral distance: rough proxy from depth (teleseismic simplification)
    dist_km = depth_km * 2.0 + magnitude * 15.0
    vp, vs = 6.0, 3.5
    t_p = dist_km / vp          # P-wave arrival (s)
    t_s = dist_km / vs          # S-wave arrival (s)
    t_surface = t_s + dist_km * 0.02  # rough surface wave delay

    # Clamp arrivals within duration
    t_p = min(t_p, duration_s * 0.25)
    t_s = min(t_s, duration_s * 0.50)
    t_surface = min(t_surface, duration_s * 0.70)

    # Amplitude scaling with magnitude (log scale)
    amp_scale = 10 ** (0.8 * magnitude - 2.5)
    amp_scale = np.clip(amp_scale, 50, 5e5)

    signal = np.zeros(n)

    # ── P-wave (high freq, short) ────────────────────────────────────────────
    p_freq = 8.0 + magnitude * 0.5
    p_width = max(0.5, 3.0 - magnitude * 0.2)
    p_env = np.exp(-((t - t_p) ** 2) / (2 * p_width ** 2))
    signal += amp_scale * 0.15 * p_env * np.sin(2 * np.pi * p_freq * (t - t_p))

    # ── S-wave (lower freq, higher amp) ─────────────────────────────────────
    s_freq = 3.0 + magnitude * 0.2
    s_width = max(1.0, 5.0 - magnitude * 0.1)
    s_env = np.exp(-((t - t_s) ** 2) / (2 * s_width ** 2))
    signal += amp_scale * 0.65 * s_env * np.sin(2 * np.pi * s_freq * (t - t_s))

    # ── Surface waves (very low freq, long coda) ─────────────────────────────
    if t_surface < duration_s * 0.9:
        surf_freq = 0.5 + magnitude * 0.05
        surf_decay = 0.05 + 0.01 * magnitude
        surf_env = np.where(t >= t_surface,
                            np.exp(-surf_decay * (t - t_surface)), 0.0)
        signal += amp_scale * 0.4 * surf_env * np.sin(
            2 * np.pi * surf_freq * (t - t_surface)
        )

    # ── Broadband noise ──────────────────────────────────────────────────────
    noise = rng.normal(0, 1, n)
    # Colour the noise (1/f tendency) via simple lowpass
    from scipy.signal import butter, sosfiltfilt
    sos = butter(2, [0.5 / (fs / 2), 30.0 / (fs / 2)], btype="band", output="sos")
    noise = sosfiltfilt(sos, noise)
    noise /= np.std(noise) + 1e-12

    signal += noise_level * amp_scale * 0.05 * noise

    metadata = {
        "type":            "synthetic",
        "magnitude":       magnitude,
        "depth_km":        depth_km,
        "dist_km":         round(dist_km, 1),
        "p_arrival_s":     round(t_p, 2),
        "s_arrival_s":     round(t_s, 2),
        "surface_wave_s":  round(t_surface, 2),
        "fs_hz":           fs,
        "duration_s":      duration_s,
        "n_samples":       n,
    }

    return signal.astype(np.float64), fs, metadata

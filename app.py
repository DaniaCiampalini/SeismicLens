"""
SeismicLens — Interactive Seismic Waveform Analyzer
A tool for loading, filtering, and analyzing seismic signals with FFT spectral analysis.
"""

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io
from utils.signal_processing import (
    bandpass_filter, compute_fft, compute_spectrogram,
    compute_sta_lta, detect_p_wave, taper_signal
)
from utils.data_loader import (
    load_mseed, load_csv_signal, generate_synthetic_quake
)

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SeismicLens",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Inter:wght@300;400;600&display=swap');

  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

  .stApp { background: #0d1117; color: #e6edf3; }

  /* Sidebar */
  section[data-testid="stSidebar"] {
    background: #161b22;
    border-right: 1px solid #30363d;
  }

  /* Cards */
  .metric-card {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 16px 20px;
    margin-bottom: 12px;
  }
  .metric-label {
    font-family: 'Space Mono', monospace;
    font-size: 11px;
    color: #7d8590;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 4px;
  }
  .metric-value {
    font-family: 'Space Mono', monospace;
    font-size: 22px;
    color: #58a6ff;
    font-weight: 700;
  }
  .metric-unit {
    font-size: 12px;
    color: #7d8590;
    margin-left: 4px;
  }

  /* Section headers */
  .section-title {
    font-family: 'Space Mono', monospace;
    font-size: 13px;
    color: #f78166;
    text-transform: uppercase;
    letter-spacing: 2px;
    border-bottom: 1px solid #30363d;
    padding-bottom: 8px;
    margin: 24px 0 16px 0;
  }

  /* Hero */
  .hero {
    background: linear-gradient(135deg, #161b22 0%, #0d1117 100%);
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 28px 32px;
    margin-bottom: 24px;
  }
  .hero h1 {
    font-family: 'Space Mono', monospace;
    font-size: 28px;
    color: #e6edf3;
    margin: 0 0 6px 0;
  }
  .hero-sub {
    color: #7d8590;
    font-size: 14px;
    font-weight: 300;
  }

  /* Alert / info box */
  .info-box {
    background: #1c2128;
    border-left: 3px solid #58a6ff;
    padding: 12px 16px;
    border-radius: 0 6px 6px 0;
    font-size: 13px;
    color: #8b949e;
    margin: 8px 0;
  }
  .warn-box {
    background: #1c2128;
    border-left: 3px solid #d29922;
    padding: 12px 16px;
    border-radius: 0 6px 6px 0;
    font-size: 13px;
    color: #8b949e;
    margin: 8px 0;
  }

  /* Plotly chart background fix */
  .js-plotly-plot { border-radius: 8px; overflow: hidden; }

  /* Streamlit widget label override */
  label { color: #8b949e !important; font-size: 13px !important; }
  .stSlider > div { color: #8b949e; }
</style>
""", unsafe_allow_html=True)

# ── Helpers ───────────────────────────────────────────────────────────────────
PLOT_LAYOUT = dict(
    paper_bgcolor="#161b22",
    plot_bgcolor="#0d1117",
    font=dict(family="Space Mono, monospace", color="#8b949e", size=11),
    margin=dict(l=60, r=20, t=40, b=40),
    xaxis=dict(gridcolor="#21262d", zerolinecolor="#30363d", linecolor="#30363d"),
    yaxis=dict(gridcolor="#21262d", zerolinecolor="#30363d", linecolor="#30363d"),
)


def make_waveform_fig(t, signal, title="Waveform", highlight_p=None):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=t, y=signal,
        mode="lines",
        line=dict(color="#58a6ff", width=1.2),
        name="Amplitude",
    ))
    if highlight_p is not None:
        fig.add_vline(
            x=highlight_p, line_width=2,
            line_dash="dash", line_color="#f78166",
            annotation_text="P-wave", annotation_font_color="#f78166",
        )
    fig.update_layout(**PLOT_LAYOUT, title=dict(text=title, font=dict(color="#e6edf3", size=13)),
                      xaxis_title="Time (s)", yaxis_title="Amplitude (counts)")
    return fig


def make_fft_fig(freqs, amplitudes, dominant_f):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=freqs, y=amplitudes,
        mode="lines", fill="tozeroy",
        line=dict(color="#3fb950", width=1.5),
        fillcolor="rgba(63,185,80,0.08)",
        name="Amplitude spectrum",
    ))
    fig.add_vline(
        x=dominant_f, line_width=2,
        line_dash="dot", line_color="#d29922",
        annotation_text=f"Peak {dominant_f:.2f} Hz",
        annotation_font_color="#d29922",
    )
    fig.update_layout(
        **PLOT_LAYOUT,
        title=dict(text="FFT — Amplitude Spectrum", font=dict(color="#e6edf3", size=13)),
        xaxis_title="Frequency (Hz)", yaxis_title="|A(f)|",
    )
    return fig


def make_spectrogram_fig(t, f, Sxx):
    fig = go.Figure(go.Heatmap(
        x=t, y=f, z=10 * np.log10(Sxx + 1e-12),
        colorscale="Inferno",
        colorbar=dict(title="dB", tickfont=dict(color="#8b949e", size=10)),
    ))
    fig.update_layout(
        **PLOT_LAYOUT,
        title=dict(text="Spectrogram (Short-Time Fourier Transform)", font=dict(color="#e6edf3", size=13)),
        xaxis_title="Time (s)", yaxis_title="Frequency (Hz)",
    )
    return fig


def make_stalta_fig(t, stalta, threshold):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=t, y=stalta,
        mode="lines", line=dict(color="#bc8cff", width=1.4),
        name="STA/LTA",
    ))
    fig.add_hline(
        y=threshold, line_width=1.5,
        line_dash="dash", line_color="#f78166",
        annotation_text=f"Threshold ({threshold})",
        annotation_font_color="#f78166",
    )
    fig.update_layout(
        **PLOT_LAYOUT,
        title=dict(text="STA/LTA Trigger — Event Detection", font=dict(color="#e6edf3", size=13)),
        xaxis_title="Time (s)", yaxis_title="STA/LTA ratio",
    )
    return fig


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🌍 SeismicLens")
    st.markdown("<div class='info-box'>Interactive seismic waveform analyzer for signal processing & spectral analysis.</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### Data source")
    data_source = st.radio(
        "Choose input",
        ["Synthetic earthquake", "Upload MiniSEED (.mseed)", "Upload CSV"],
        index=0,
    )

    uploaded_file = None
    if data_source in ["Upload MiniSEED (.mseed)", "Upload CSV"]:
        ext = ".mseed" if "MSEED" in data_source else ".csv"
        uploaded_file = st.file_uploader(f"Upload {ext} file", type=[ext.strip(".")])

    st.markdown("---")
    st.markdown("#### Synthetic signal (if no upload)")
    syn_magnitude = st.slider("Simulated magnitude", 2.0, 8.0, 5.5, 0.5)
    syn_depth = st.slider("Focal depth (km)", 5, 200, 30, 5)
    syn_noise = st.slider("Noise level", 0.0, 1.0, 0.15, 0.05)
    syn_duration = st.slider("Duration (s)", 30, 300, 120, 10)

    st.markdown("---")
    st.markdown("#### Bandpass filter")
    filter_on = st.toggle("Apply Butterworth filter", value=True)
    f_low  = st.slider("Low cut (Hz)",  0.1, 10.0, 1.0,  0.1)
    f_high = st.slider("High cut (Hz)", 1.0, 50.0, 10.0, 0.5)
    filter_order = st.selectbox("Filter order", [2, 4, 6], index=1)

    st.markdown("---")
    st.markdown("#### STA/LTA detector")
    sta_len   = st.slider("STA window (s)", 0.5, 5.0,  1.0, 0.5)
    lta_len   = st.slider("LTA window (s)", 5.0, 60.0, 20.0, 5.0)
    threshold = st.slider("Trigger threshold", 1.0, 10.0, 3.5, 0.5)

    st.markdown("---")
    st.markdown("#### Display options")
    show_spectrogram = st.toggle("Show spectrogram", value=True)
    show_stalta      = st.toggle("Show STA/LTA", value=True)
    show_raw         = st.toggle("Show raw (unfiltered) overlay", value=False)

    st.markdown("---")
    st.caption("SeismicLens v1.0 · Built with ObsPy, SciPy, Streamlit")


# ── Load / generate data ──────────────────────────────────────────────────────
signal_raw = None
fs = 100.0
metadata = {}

if data_source == "Synthetic earthquake":
    signal_raw, fs, metadata = generate_synthetic_quake(
        magnitude=syn_magnitude,
        depth_km=syn_depth,
        noise_level=syn_noise,
        duration_s=syn_duration,
    )

elif data_source == "Upload MiniSEED (.mseed)" and uploaded_file:
    try:
        signal_raw, fs, metadata = load_mseed(uploaded_file)
    except Exception as e:
        st.error(f"Error loading MiniSEED: {e}")

elif data_source == "Upload CSV" and uploaded_file:
    try:
        signal_raw, fs, metadata = load_csv_signal(uploaded_file)
    except Exception as e:
        st.error(f"Error loading CSV: {e}")


# ── Main content ──────────────────────────────────────────────────────────────
st.markdown("""
<div class='hero'>
  <h1>🌍 SeismicLens</h1>
  <div class='hero-sub'>Seismic Waveform Analyzer · Signal Processing & Spectral Analysis Tool</div>
</div>
""", unsafe_allow_html=True)

if signal_raw is None:
    st.markdown("<div class='warn-box'>⚠ No data loaded. Select a source in the sidebar or use the synthetic generator.</div>", unsafe_allow_html=True)
    st.stop()

# Taper + optional filter
signal_tapered = taper_signal(signal_raw)
if filter_on:
    try:
        signal_proc = bandpass_filter(signal_tapered, f_low, f_high, fs, order=filter_order)
    except Exception as e:
        st.warning(f"Filter error: {e}")
        signal_proc = signal_tapered
else:
    signal_proc = signal_tapered

t = np.linspace(0, len(signal_proc) / fs, len(signal_proc))

# Detections
freqs, amplitudes = compute_fft(signal_proc, fs)
dominant_f = freqs[np.argmax(amplitudes)]
p_time = detect_p_wave(signal_proc, fs, sta_len, lta_len, threshold)

# ── Metrics row ───────────────────────────────────────────────────────────────
col1, col2, col3, col4, col5 = st.columns(5)

def metric(col, label, value, unit=""):
    col.markdown(f"""
    <div class='metric-card'>
      <div class='metric-label'>{label}</div>
      <div class='metric-value'>{value}<span class='metric-unit'>{unit}</span></div>
    </div>""", unsafe_allow_html=True)

metric(col1, "Sampling rate", f"{fs:.0f}", "Hz")
metric(col2, "Duration",      f"{len(signal_proc)/fs:.1f}", "s")
metric(col3, "Peak amplitude",f"{np.max(np.abs(signal_proc)):.1f}", "cts")
metric(col4, "Dominant freq", f"{dominant_f:.2f}", "Hz")
metric(col5, "P-wave arrival", f"{p_time:.1f}" if p_time else "—", "s")

# Metadata if available
if metadata:
    with st.expander("📋 Trace metadata", expanded=False):
        st.json(metadata)

# ── Waveform ──────────────────────────────────────────────────────────────────
st.markdown("<div class='section-title'>Waveform</div>", unsafe_allow_html=True)
fig_wave = make_waveform_fig(t, signal_proc,
                             title=f"Processed waveform {'(filtered)' if filter_on else '(raw)'}",
                             highlight_p=p_time)

if show_raw and filter_on:
    fig_wave.add_trace(go.Scatter(
        x=t, y=signal_tapered,
        mode="lines",
        line=dict(color="#30363d", width=0.8),
        name="Raw", opacity=0.5,
    ))

st.plotly_chart(fig_wave, use_container_width=True)

# ── FFT ───────────────────────────────────────────────────────────────────────
st.markdown("<div class='section-title'>Spectral Analysis</div>", unsafe_allow_html=True)
fig_fft = make_fft_fig(freqs, amplitudes, dominant_f)
st.plotly_chart(fig_fft, use_container_width=True)

# ── Spectrogram ───────────────────────────────────────────────────────────────
if show_spectrogram:
    st.markdown("<div class='section-title'>Spectrogram</div>", unsafe_allow_html=True)
    try:
        t_spec, f_spec, Sxx = compute_spectrogram(signal_proc, fs)
        fig_spec = make_spectrogram_fig(t_spec, f_spec, Sxx)
        st.plotly_chart(fig_spec, use_container_width=True)
    except Exception as e:
        st.warning(f"Could not compute spectrogram: {e}")

# ── STA/LTA ───────────────────────────────────────────────────────────────────
if show_stalta:
    st.markdown("<div class='section-title'>Event Detection — STA/LTA</div>", unsafe_allow_html=True)
    try:
        stalta_vals = compute_sta_lta(signal_proc, fs, sta_len, lta_len)
        t_sl = np.linspace(0, len(stalta_vals) / fs, len(stalta_vals))
        fig_sl = make_stalta_fig(t_sl, stalta_vals, threshold)
        st.plotly_chart(fig_sl, use_container_width=True)
        if p_time:
            st.markdown(f"<div class='info-box'>✓ First trigger detected at <b>{p_time:.2f} s</b> — possible P-wave onset.</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='info-box'>No trigger above threshold found. Try lowering the threshold or increasing signal energy.</div>", unsafe_allow_html=True)
    except Exception as e:
        st.warning(f"STA/LTA error: {e}")

# ── Export ────────────────────────────────────────────────────────────────────
st.markdown("<div class='section-title'>Export</div>", unsafe_allow_html=True)
col_dl1, col_dl2 = st.columns(2)

with col_dl1:
    csv_buf = io.StringIO()
    df_out = pd.DataFrame({"time_s": t, "amplitude": signal_proc})
    df_out.to_csv(csv_buf, index=False)
    st.download_button("⬇ Download processed signal (CSV)", csv_buf.getvalue(),
                       file_name="seismiclens_signal.csv", mime="text/csv")

with col_dl2:
    fft_buf = io.StringIO()
    df_fft = pd.DataFrame({"frequency_hz": freqs, "amplitude": amplitudes})
    df_fft.to_csv(fft_buf, index=False)
    st.download_button("⬇ Download FFT spectrum (CSV)", fft_buf.getvalue(),
                       file_name="seismiclens_fft.csv", mime="text/csv")

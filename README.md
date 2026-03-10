# 🌍 SeismicLens — Interactive Seismic Waveform Analyzer

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app.streamlit.app)
![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)

A web-based tool for loading, filtering, and analyzing seismic waveforms, built as a portfolio project for geotechnology / applied geophysics.

---

## Features

| Module | Description |
|---|---|
| **Signal loading** | MiniSEED (via ObsPy), CSV, or synthetic earthquake generator |
| **Synthetic model** | Physically-inspired P/S/surface wave synthesis with magnitude & depth controls |
| **Bandpass filter** | Zero-phase Butterworth filter (configurable low/high cut and order) |
| **FFT spectrum** | Single-sided amplitude spectrum with dominant frequency detection |
| **Spectrogram** | Short-Time Fourier Transform (STFT) heatmap |
| **STA/LTA detector** | Classic recursive STA/LTA with configurable trigger threshold for P-wave picking |
| **Export** | Download processed signal and FFT spectrum as CSV |

---

## Scientific background

### Bandpass filtering
Seismic waveforms contain energy across a wide frequency band. A **Butterworth bandpass filter** (applied zero-phase via `sosfiltfilt`) removes both low-frequency drift and high-frequency instrument noise, isolating the seismic band of interest (typically 1–10 Hz for local/regional earthquakes).

### FFT spectral analysis
The **Fast Fourier Transform** decomposes the waveform into its frequency components. The dominant frequency is sensitive to source depth, magnitude, and propagation path — making spectral analysis a key tool in earthquake characterisation.

### Spectrogram (STFT)
A spectrogram shows how the frequency content evolves over time, revealing the arrival of different seismic phases (P, S, surface waves) and their spectral signatures.

### STA/LTA event detection
The **Short-Term Average / Long-Term Average** algorithm is the industry-standard method for automated seismic phase picking. When the ratio of short-term energy to long-term energy exceeds a threshold, a seismic onset is declared.

---

## Installation

```bash
git clone https://github.com/your-username/seismiclens.git
cd seismiclens
pip install -r requirements.txt
streamlit run app.py
```

ObsPy is only required for MiniSEED support. The app runs without it using CSV or the synthetic generator.

---

## Usage

1. **Synthetic mode** (default): adjust magnitude, depth, noise level, and duration in the sidebar.
2. **MiniSEED upload**: drag and drop any `.mseed` file (e.g. from IRIS/FDSN webservices).
3. **CSV upload**: two-column file (time\_s, amplitude) or single-column amplitude array.
4. Tune the bandpass filter, STA/LTA windows, and threshold interactively.
5. Export the processed signal or FFT spectrum with the download buttons.

### Getting real MiniSEED data
Free seismic data is available from:
- [IRIS Wilber 3](https://ds.iris.edu/wilber3/) — waveform request tool
- [FDSN Web Services](https://www.fdsn.org/webservices/) — REST API
- [INGV](http://webservices.ingv.it/) — Italian National Institute of Geophysics

---

## Project structure

```
seismiclens/
├── app.py                  # Streamlit entry point
├── requirements.txt
├── utils/
│   ├── signal_processing.py   # Taper, bandpass, FFT, spectrogram, STA/LTA
│   └── data_loader.py         # MiniSEED, CSV, synthetic generator
└── README.md
```

---

## Tech stack

- **[Streamlit](https://streamlit.io/)** — interactive web UI
- **[ObsPy](https://docs.obspy.org/)** — seismological data I/O (MiniSEED)
- **[SciPy](https://scipy.org/)** — signal processing (filter, FFT, spectrogram)
- **[Plotly](https://plotly.com/python/)** — interactive charts
- **[NumPy](https://numpy.org/)** / **[Pandas](https://pandas.pydata.org/)** — numerical computing

---

## Possible extensions

- [ ] Multi-trace support (three-component Z/N/E)
- [ ] Automatic magnitude estimation from peak amplitude
- [ ] P/S arrival time difference → epicentral distance calculator
- [ ] Integration with FDSN web services for live data fetching
- [ ] Hodogram (particle motion plot) for phase polarisation analysis

---

## License

MIT — feel free to fork and extend.

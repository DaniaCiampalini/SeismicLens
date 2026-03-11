<div align="center">

# 🌍 SeismicLens

**Interactive Seismic Waveform Analyzer**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![ObsPy](https://img.shields.io/badge/ObsPy-1.4%2B-green)](https://docs.obspy.org/)
[![SciPy](https://img.shields.io/badge/SciPy-1.13%2B-8CAAE6?logo=scipy)](https://scipy.org/)

*Load, filter, and analyse seismic waveforms directly in your browser — no installation beyond Python required.*

**🇬🇧 English** · [🇮🇹 Italiano](docs/README_IT.md) · [🇫🇷 Français](docs/README_FR.md) · [🇪🇸 Español](docs/README_ES.md) · [🇩🇪 Deutsch](docs/README_DE.md)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Quick Start](#-quick-start)
- [Usage Guide](#-usage-guide)
- [Getting Real Data](#-getting-real-data)
- [Seismological Model](#-seismological-model)
- [Mathematical Background](#-mathematical-background)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Roadmap](#-roadmap)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🔭 Overview

**SeismicLens** is an open-source, browser-based geophysics workbench built with [Streamlit](https://streamlit.io/). It lets students, researchers, and earthquake enthusiasts explore seismic signals without writing a single line of code.

**What you can do:**

- Generate **physically realistic synthetic seismograms** using an IASP91-inspired layered crustal velocity model
- Upload and analyse **real MiniSEED waveforms** from global networks (IRIS, INGV, GEOFON, …)
- Apply a **zero-phase Butterworth bandpass filter** to isolate frequency bands of interest
- Detect P-wave onsets automatically with the classic **STA/LTA algorithm** (Allen, 1978)
- Decompose the signal via **FFT** and visualise amplitude spectrum, phase spectrum, and Welch PSD
- Inspect time–frequency evolution with an **interactive spectrogram (STFT)**
- **Export** all processed data as CSV for downstream analysis in Python, MATLAB, or Excel
- Switch between **5 languages** (EN / IT / FR / ES / DE) and **dark / light themes**

---

## ✨ Features

| Feature | Details |
|---|---|
|  Synthetic waveform generator | P, S, and surface waves · IASP91-like layered crustal model · configurable M, depth, distance, noise, duration |
|  MiniSEED upload | Real data from IRIS FDSN or INGV webservices |
|  CSV upload | Auto-detects single-column (amplitude) or two-column (time, amplitude) formats |
| ️ Zero-phase Butterworth filter | Configurable bandpass · order 2–8 · no phase distortion (`sosfiltfilt`) |
|  FFT spectral analysis | Amplitude spectrum · phase spectrum · dominant frequency · spectral centroid · RMS bandwidth |
|  Power Spectral Density | Welch PSD estimate in counts²/Hz and dB re 1 count²/Hz |
| ️ Spectrogram (STFT) | Interactive time–frequency heatmap · Inferno/Viridis colorscale |
|  STA/LTA P-wave picker | Classic Allen (1978) detector · O(N) via prefix sums · configurable windows & threshold |
|  Crustal velocity model | Interactive table (Vp, Vs, Vp/Vs, Poisson ratio, density) + horizontal bar chart |
|  Theory & Math panel | DFT/FFT with complex numbers · Butterworth design · Richter & Mw magnitude · Wadati method |
|  CSV export | Filtered signal · FFT spectrum · Welch PSD · STA/LTA ratio |
|  Multilingual UI | English · Italiano · Français · Español · Deutsch |
|  Dark / Light theme | Toggle in sidebar · theme-aware Plotly charts |
---

## 🚀 Quick Start

### Prerequisites

- Python **3.10 or higher**
- `pip` (comes with Python)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/your-username/seismiclens.git
cd seismiclens

# 2. (Recommended) Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Launch the app
streamlit run app.py
```

The app will open automatically at **http://localhost:8501**.

> **Tip:** On first run ObsPy may take a few seconds to initialise. Subsequent runs are faster thanks to Streamlit's module caching.

---

## 📖 Usage Guide

### 1 — Choose a data source

Open the **sidebar** (☰ if collapsed) and select one of three modes:

| Mode | When to use |
|---|---|
| **Synthetic earthquake** | Instant exploration — no file required. Adjust magnitude (M 2–8), focal depth (5–200 km), epicentral distance (10–500 km), noise level, and duration. |
| **Upload MiniSEED** | Real broadband seismograms from global networks. Download `.mseed` files from IRIS or INGV (see [Getting Real Data](#-getting-real-data)). |
| **Upload CSV** | Your own time-series data. One column = amplitude samples; two columns = time (s), amplitude. |

### 2 — Configure the Butterworth filter

| Parameter | Typical values | Effect |
|---|---|---|
| Low cut (Hz) | 0.01–2 Hz (teleseismic) · 0.5–5 Hz (regional) · 1–15 Hz (local) | Removes low-frequency drift and microseismic noise |
| High cut (Hz) | Must be < Nyquist (fs/2) | Removes high-frequency cultural noise |
| Order | 2–8 (default 4) | Higher order → steeper roll-off, more ringing |

Toggle **Zero-phase bandpass** on/off to compare the filtered signal against the raw waveform.

### 3 — Adjust the STA/LTA detector

```
Rule of thumb:  LTA >= 10 x STA
Typical threshold:  3 - 5
```

| Parameter | Description |
|---|---|
| STA window (s) | Short-term average: captures the impulsive onset energy (0.2–2 s) |
| LTA window (s) | Long-term average: tracks the background noise level (5–60 s) |
| Trigger threshold | Ratio R above which a seismic phase is declared |

Lower the threshold to catch weak events; raise it to suppress false triggers on noisy data.

### 4 — Explore the analysis tabs

| Tab | What you see |
|---|---|
| **Waveform** | Time-domain plot · P and S arrival markers · raw signal overlay toggle |
| **Spectral Analysis** | FFT amplitude spectrum · optional phase spectrum · optional Welch PSD |
| **Spectrogram** | STFT time–frequency heatmap |
| **STA/LTA** | STA/LTA characteristic function · trigger windows highlighted |
| **Velocity Model** | IASP91-inspired table + Vp/Vs bar chart |
| **Theory & Math** | DFT, Butterworth, PSD, STFT, wave physics, magnitude scales — with equations |
| **Export** | Download CSV files for every computed quantity |

### 5 — Export results

All processed data can be downloaded as CSV from the **Export** tab:

| File | Contents |
|---|---|
| `signal.csv` | Time (s), filtered amplitude (counts) |
| `fft.csv` | Frequency (Hz), amplitude, phase (deg) |
| `psd.csv` | Frequency (Hz), PSD (counts²/Hz) |
| `stalta.csv` | Time (s), STA/LTA ratio |

---

## 🛰️ Getting Real Data

### IRIS (Incorporated Research Institutions for Seismology)

1. Go to **[IRIS Wilber 3](https://ds.iris.edu/wilber3/find_event)**
2. Search for an earthquake by date, region, or magnitude
3. Select a seismic station close to your event
4. Choose **MiniSEED** as the export format and download

### INGV (Istituto Nazionale di Geofisica e Vulcanologia — Italy)

1. Open the **[INGV FDSN webservice](https://webservices.ingv.it/swagger-ui/index.html)**
2. Use the `/dataselect` endpoint with network, station, and time parameters
3. Set format to `miniseed` and download

### Other networks

| Network | URL |
|---|---|
| GEOFON (GFZ Potsdam) | https://geofon.gfz-potsdam.de/waveform/ |
| EMSC | https://www.seismicportal.eu/ |
| ORFEUS | https://www.orfeus-eu.org/data/eida/ |

---

## 🌐 Seismological Model

### Layered Crustal Velocity (IASP91-inspired)

| Layer | Depth (km) | Vp (km/s) | Vs (km/s) | Vp/Vs | Poisson v |
|---|---|---|---|---|---|
| Upper crust | 0–15 | 5.80 | 3.36 | 1.726 | 0.249 |
| Middle crust | 15–25 | 6.50 | 3.75 | 1.733 | 0.252 |
| Lower crust | 25–35 | 7.00 | 4.00 | 1.750 | 0.257 |
| Upper mantle | 35–200 | 8.04 | 4.47 | 1.798 | 0.272 |

### Synthetic Waveform Physics

```
P-wave   :  f ~ 6-12 Hz,   Gaussian envelope,    amplitude ~ 10^(0.8M-2.5) x 0.15
S-wave   :  f ~ 2-6 Hz,    Gaussian envelope,    amplitude ~ 10^(0.8M-2.5) x 0.65
Surface  :  f ~ 0.3-1 Hz,  exponential coda,     amplitude ~ 10^(0.8M-2.5) x 0.40
Noise    :  Butterworth bandpass 0.5-30 Hz, sigma-normalised
```

Travel times computed from hypocentral distance `R = sqrt(d^2 + h^2)`.

---

## 📐 Mathematical Background

### Discrete Fourier Transform (DFT)

```
X[k] = sum_{n=0}^{N-1}  x[n] * exp(-j * 2pi * k * n / N)

|X[k]|  ->  amplitude at  f_k = k * fs / N  Hz
angle(X[k])  ->  phase = atan2(Im(X[k]), Re(X[k]))

One-sided normalised spectrum:  A[k] = (2/N) * |X[k]|
```

The FFT (Cooley–Tukey, 1965) reduces complexity from O(N²) to **O(N log N)**.  
For real signals the spectrum is Hermitian: `X[N-k] = conj(X[k])`, so only N/2+1 unique bins exist (exploited by `scipy.fft.rfft`).

### Zero-phase Butterworth Filter

```
|H(jw)|^2 = 1 / [1 + (w/wc)^(2n)]

Single pass roll-off:              20*n  dB/decade
sosfiltfilt (effective order 2n):  40*n  dB/decade, zero phase distortion
```

Implemented in SOS (Second-Order Sections) form for numerical stability.

### STA/LTA (Allen, 1978)

```
STA(t) = (1/Nsta) * sum( x^2[t-Nsta : t] )
LTA(t) = (1/Nlta) * sum( x^2[t-Nlta : t] )
R(t)   = STA(t) / LTA(t)   ->  trigger when R > threshold
```

O(N) implementation using prefix sums: `cs = cumsum(x^2)`.

### Wadati Method

```
R = sqrt(d^2 + h^2)              (hypocentral distance)
t_P = R / Vp  ,  t_S = R / Vs
d ~ (t_S - t_P) * Vp * Vs / (Vp - Vs)
```

---

## 🛠️ Tech Stack

| Library | Version | Role |
|---|---|---|
| [Streamlit](https://streamlit.io/) | >= 1.35 | Web UI, reactive state management |
| [ObsPy](https://docs.obspy.org/) | >= 1.4 | MiniSEED I/O, trace detrending |
| [SciPy](https://scipy.org/) | >= 1.13 | Butterworth filter (SOS), STFT, Welch PSD |
| [NumPy](https://numpy.org/) | >= 1.26 | Signal arrays, FFT (rfft) |
| [Plotly](https://plotly.com/python/) | >= 5.22 | Interactive charts |
| [Pandas](https://pandas.pydata.org/) | >= 2.2 | CSV I/O, data preview |

---

## 📁 Project Structure

```
seismiclens/
├── app.py                     # Main Streamlit application (UI + orchestration)
├── requirements.txt           # Python dependencies
├── LICENSE                    # MIT License
├── README.md                  # This file (English)
├── docs/
│   ├── README_IT.md           # Documentazione italiana
│   ├── README_FR.md           # Documentation française
│   ├── README_ES.md           # Documentación española
│   └── README_DE.md           # Deutsche Dokumentation
└── utils/
    ├── __init__.py
    ├── data_loader.py         # MiniSEED, CSV, synthetic waveform generator
    └── signal_processing.py  # FFT, Butterworth filter, STA/LTA, PSD, spectrogram
```

---

## 🗺️ Roadmap

The following features are planned for future releases. Contributions are welcome!

### v2.1 — Data & I/O
- [ ] **FDSN client integration** — query IRIS / INGV directly from the app without manual download
- [ ] **SAC file support** — load SAC-format seismograms widely used in academic seismology
- [ ] **Multi-trace display** — plot and compare three-component (Z, N, E) recordings simultaneously

### v2.2 — Signal Processing
- [ ] **Instrument response removal** — deconvolve RESP / StationXML files to obtain ground displacement/velocity/acceleration
- [ ] **Adaptive STA/LTA** — recursive STA/LTA with automatic threshold optimisation
- [ ] **Particle motion analysis** — hodogram plots for Z-N-E component data
- [ ] **Coda-Q estimation** — scattering attenuation from coda envelope decay

### v2.3 — Advanced Analysis
- [ ] **Moment tensor visualisation** — beach ball diagrams from focal mechanism parameters
- [ ] **Array processing** — beamforming and slowness analysis for seismic arrays
- [ ] **Machine-learning phase picker** — integrate PhaseNet or EQTransformer for automated phase detection
- [ ] **Magnitude estimation** — local magnitude (Ml) computation from peak amplitude and station correction

### v3.0 — Platform
- [ ] **Real-time streaming** — connect to SeedLink servers for live waveform monitoring
- [ ] **User session persistence** — save and reload analysis configurations
- [ ] **REST API** — expose processing functions as endpoints for programmatic access
- [ ] **Docker image** — one-command deployment with `docker run`

---

## 🤝 Contributing

Contributions, bug reports, and feature requests are warmly welcome!

1. **Fork** the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Commit your changes following [Conventional Commits](https://www.conventionalcommits.org/): `git commit -m "feat: add your feature"`
4. Push to the branch: `git push origin feature/your-feature-name`
5. Open a **Pull Request** against `main`

### Code style

- Follow **PEP 8** for Python code
- Keep functions focused and documented with docstrings
- Add or update tests when introducing new signal-processing logic
- Run `python -m py_compile app.py utils/*.py` before opening a PR

### Reporting bugs

Please open a GitHub Issue and include:
- Python version and OS
- Steps to reproduce
- Expected vs. actual behaviour
- If possible, a minimal sample file (MiniSEED or CSV) that triggers the bug

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

```
MIT License  —  Copyright (c) 2026 Dania Ciampalini & Dario Ciampalini

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.

IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, 
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, 
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE 
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
```


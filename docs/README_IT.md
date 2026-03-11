<div align="center">

# 🌍 SeismicLens

**Analizzatore Interattivo di Forme d'Onda Sismiche**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../LICENSE)
[![ObsPy](https://img.shields.io/badge/ObsPy-1.4%2B-green)](https://docs.obspy.org/)
[![SciPy](https://img.shields.io/badge/SciPy-1.13%2B-8CAAE6?logo=scipy)](https://scipy.org/)

*Carica, filtra e analizza forme d'onda sismiche direttamente nel browser — senza installare nulla oltre a Python.*

[🇬🇧 English](../README.md) · **🇮🇹 Italiano** · [🇫🇷 Français](README_FR.md) · [🇪🇸 Español](README_ES.md) · [🇩🇪 Deutsch](README_DE.md)

</div>

---

## 📋 Indice

- [Panoramica](#-panoramica)
- [Funzionalità](#-funzionalità)
- [Avvio rapido](#-avvio-rapido)
- [Guida all'uso](#-guida-alluso)
- [Ottenere dati reali](#-ottenere-dati-reali)
- [Modello sismologico](#-modello-sismologico)
- [Basi matematiche](#-basi-matematiche)
- [Stack tecnologico](#-stack-tecnologico)
- [Struttura del progetto](#-struttura-del-progetto)
- [Roadmap](#-roadmap)
- [Contribuire](#-contribuire)
- [Licenza](#-licenza)

---

## 🔭 Panoramica

**SeismicLens** è un'applicazione geofisica open-source basata su browser, costruita con [Streamlit](https://streamlit.io/). Permette a studenti, ricercatori e appassionati di terremoti di esplorare segnali sismici senza scrivere una riga di codice.

**Cosa puoi fare:**

- Generare **sismogrammi sintetici fisicamente realistici** con un modello crostale a strati ispirato a IASP91
- Caricare e analizzare **forme d'onda MiniSEED reali** da reti globali (IRIS, INGV, GEOFON, …)
- Applicare un **filtro Butterworth bandpass zero-phase** per isolare la banda di frequenza di interesse
- Rilevare automaticamente l'arrivo dell'onda P con il classico **algoritmo STA/LTA** (Allen, 1978)
- Scomporre il segnale via **FFT** e visualizzare spettro di ampiezza, di fase e PSD di Welch
- Esaminare l'evoluzione tempo-frequenza con uno **spettrogramma interattivo (STFT)**
- **Esportare** tutti i dati elaborati come CSV per analisi successive in Python, MATLAB o Excel
- Passare tra **5 lingue** (EN / IT / FR / ES / DE) e **tema scuro / chiaro**

---

## ✨ Funzionalità

| Funzione | Dettagli |
|---|---|
|  Generatore di sismogrammi sintetici | Onde P, S e superficiali · modello crostale a strati IASP91 · M, profondità, distanza, rumore e durata configurabili |
|  Upload MiniSEED | Dati reali da IRIS FDSN o INGV webservices |
|  Upload CSV | Rilevamento automatico di formato a 1 colonna (ampiezza) o 2 colonne (tempo, ampiezza) |
| ️ Filtro Butterworth zero-phase | Bandpass configurabile · ordine 2–8 · nessuna distorsione di fase (`sosfiltfilt`) |
|  Analisi spettrale FFT | Spettro di ampiezza · spettro di fase · frequenza dominante · centroide spettrale · larghezza di banda RMS |
|  Densità spettrale di potenza | Stima PSD Welch in counts²/Hz e dB re 1 count²/Hz |
| ️ Spettrogramma (STFT) | Mappa tempo-frequenza interattiva · scala colori Inferno/Viridis |
|  Picker onda P STA/LTA | Detector classico Allen (1978) · O(N) via prefix sums · finestre e soglia configurabili |
|  Modello di velocità crostale | Tabella interattiva (Vp, Vs, Vp/Vs, coefficiente di Poisson, densità) + grafico a barre |
|  Pannello Teoria e Matematica | DFT/FFT con numeri complessi · design Butterworth · scala Richter e Mw · metodo di Wadati |
|  Esportazione CSV | Segnale filtrato · spettro FFT · PSD Welch · rapporto STA/LTA |
|  Interfaccia multilingua | English · Italiano · Français · Español · Deutsch |
|  Tema scuro / chiaro | Toggle nella barra laterale · grafici Plotly adattativi |

---

## 🚀 Avvio rapido

### Prerequisiti

- Python **3.10 o superiore**
- `pip` (incluso con Python)

### Installazione

```bash
# 1. Clona il repository
git clone https://github.com/your-username/seismiclens.git
cd seismiclens

# 2. (Consigliato) Crea e attiva un ambiente virtuale
python -m venv .venv
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate         # Windows

# 3. Installa le dipendenze
pip install -r requirements.txt

# 4. Avvia l'app
streamlit run app.py
```

L'app si aprirà automaticamente su **http://localhost:8501**.

> **Suggerimento:** Al primo avvio ObsPy può impiegare qualche secondo per inizializzarsi. Le esecuzioni successive sono più rapide grazie alla cache dei moduli di Streamlit.

---

## 📖 Guida all'uso

### 1 — Scegli la sorgente dati

Apri la **barra laterale** (☰ se è compressa) e seleziona una delle tre modalità:

| Modalità | Quando usarla |
|---|---|
| **Terremoto sintetico** | Esplorazione immediata — nessun file necessario. Configura magnitudo (M 2–8), profondità focale (5–200 km), distanza epicentrale (10–500 km), livello di rumore e durata. |
| **Carica MiniSEED** | Sismogrammi a banda larga da reti globali. Scarica file `.mseed` da IRIS o INGV (vedi [Ottenere dati reali](#-ottenere-dati-reali)). |
| **Carica CSV** | I tuoi dati time-series personali. Una colonna = campioni di ampiezza; due colonne = tempo (s), ampiezza. |

### 2 — Configura il filtro Butterworth

| Parametro | Valori tipici | Effetto |
|---|---|---|
| Taglio basso (Hz) | 0.01–2 Hz (teleseismico) · 0.5–5 Hz (regionale) · 1–15 Hz (locale) | Rimuove drift a bassa frequenza e rumore microsismico |
| Taglio alto (Hz) | Deve essere < Nyquist (fs/2) | Rimuove il rumore culturale ad alta frequenza |
| Ordine | 2–8 (default 4) | Ordine più alto → roll-off più ripido, più ringing |

Attiva/disattiva il **Bandpass zero-phase** per confrontare il segnale filtrato con quello grezzo.

### 3 — Regola il detector STA/LTA

```
Regola pratica:  LTA >= 10 x STA
Soglia tipica:  3 - 5
```

| Parametro | Descrizione |
|---|---|
| Finestra STA (s) | Media a breve termine: cattura l'energia impulsiva dell'onset (0.2–2 s) |
| Finestra LTA (s) | Media a lungo termine: traccia il livello di rumore di fondo (5–60 s) |
| Soglia di trigger | Valore del rapporto R sopra il quale viene dichiarata una fase sismica |

Abbassa la soglia per rilevare eventi deboli; alzala per sopprimere falsi trigger su dati rumorosi.

### 4 — Esplora le schede di analisi

| Scheda | Cosa vedi |
|---|---|
| **Forma d'onda** | Grafico nel dominio del tempo · marker degli arrivi P e S · overlay del segnale grezzo |
| **Analisi spettrale** | Spettro di ampiezza FFT · spettro di fase opzionale · PSD Welch opzionale |
| **Spettrogramma** | Mappa tempo-frequenza STFT |
| **STA/LTA** | Funzione caratteristica STA/LTA · finestre di trigger evidenziate |
| **Modello di velocità** | Tabella IASP91 + grafico Vp/Vs |
| **Teoria e Matematica** | DFT, Butterworth, PSD, STFT, fisica delle onde, scale di magnitudo — con equazioni |
| **Esporta** | Download CSV di tutte le grandezze calcolate |

### 5 — Esporta i risultati

Tutti i dati elaborati sono scaricabili come CSV dalla scheda **Esporta**:

| File | Contenuto |
|---|---|
| `signal.csv` | Tempo (s), ampiezza filtrata (counts) |
| `fft.csv` | Frequenza (Hz), ampiezza, fase (gradi) |
| `psd.csv` | Frequenza (Hz), PSD (counts²/Hz) |
| `stalta.csv` | Tempo (s), rapporto STA/LTA |

---

## 🛰️ Ottenere dati reali

### IRIS (Incorporated Research Institutions for Seismology)

1. Vai su **[IRIS Wilber 3](https://ds.iris.edu/wilber3/find_event)**
2. Cerca un terremoto per data, regione o magnitudo
3. Seleziona una stazione sismica vicina all'evento
4. Scegli **MiniSEED** come formato di esportazione e scarica

### INGV (Istituto Nazionale di Geofisica e Vulcanologia)

1. Apri il **[webservice FDSN di INGV](https://webservices.ingv.it/swagger-ui/index.html)**
2. Usa l'endpoint `/dataselect` con rete, stazione e parametri temporali
3. Imposta il formato su `miniseed` e scarica

### Altre reti

| Rete | URL |
|---|---|
| GEOFON (GFZ Potsdam) | https://geofon.gfz-potsdam.de/waveform/ |
| EMSC | https://www.seismicportal.eu/ |
| ORFEUS | https://www.orfeus-eu.org/data/eida/ |

---

## 🌐 Modello sismologico

### Modello di velocità crostale a strati (ispirato a IASP91)

| Strato | Profondità (km) | Vp (km/s) | Vs (km/s) | Vp/Vs | Poisson v |
|---|---|---|---|---|---|
| Crosta superiore | 0–15 | 5.80 | 3.36 | 1.726 | 0.249 |
| Crosta media | 15–25 | 6.50 | 3.75 | 1.733 | 0.252 |
| Crosta inferiore | 25–35 | 7.00 | 4.00 | 1.750 | 0.257 |
| Mantello superiore | 35–200 | 8.04 | 4.47 | 1.798 | 0.272 |

### Fisica della forma d'onda sintetica

```
Onda P        :  f ~ 6-12 Hz,   inviluppo gaussiano,  ampiezza  10^(0.8M-2.5) x 0.15
Onda S        :  f ~ 2-6 Hz,    inviluppo gaussiano,  ampiezza  10^(0.8M-2.5) x 0.65
Onde superf.  :  f ~ 0.3-1 Hz,  coda esponenziale,    ampiezza  10^(0.8M-2.5) x 0.40
Rumore        :  Butterworth bandpass 0.5-30 Hz, normalizzato a sigma
```

Tempi di percorrenza calcolati dalla distanza ipocentrale `R = sqrt(d^2 + h^2)`.

---

## 📐 Basi matematiche

### Trasformata di Fourier Discreta (DFT)

```
X[k] = sum_{n=0}^{N-1}  x[n] * exp(-j * 2pi * k * n / N)

|X[k]|  ->  ampiezza alla frequenza  f_k = k * fs / N  Hz
angle(X[k])  ->  fase = atan2(Im(X[k]), Re(X[k]))

Spettro monolaterale normalizzato:  A[k] = (2/N) * |X[k]|
```

La FFT (Cooley–Tukey, 1965) riduce la complessità da O(N²) a **O(N log N)**.  
Per segnali reali lo spettro è hermitiano: `X[N-k] = conj(X[k])`, quindi esistono solo N/2+1 bin indipendenti (sfruttato da `scipy.fft.rfft`).

### Filtro Butterworth zero-phase

```
|H(jw)|^2 = 1 / [1 + (w/wc)^(2n)]

Roll-off passata singola:      20*n  dB/decade
sosfiltfilt (ordine effettivo 2n):  40*n  dB/decade, distorsione di fase zero
```

Implementato in forma SOS (Second-Order Sections) per stabilità numerica.

### STA/LTA (Allen, 1978)

```
STA(t) = (1/Nsta) * sum( x^2[t-Nsta : t] )
LTA(t) = (1/Nlta) * sum( x^2[t-Nlta : t] )
R(t)   = STA(t) / LTA(t)   ->  trigger quando R > soglia
```

Implementazione O(N) tramite prefix sums: `cs = cumsum(x^2)`.

### Metodo di Wadati

```
R = sqrt(d^2 + h^2)              (distanza ipocentrale)
t_P = R / Vp  ,  t_S = R / Vs
d ≈ (t_S - t_P) * Vp * Vs / (Vp - Vs)
```

---

## 🛠️ Stack tecnologico

| Libreria | Versione | Ruolo |
|---|---|---|
| [Streamlit](https://streamlit.io/) | >= 1.35 | Interfaccia web, gestione stato reattivo |
| [ObsPy](https://docs.obspy.org/) | >= 1.4 | Lettura MiniSEED, detrendizzazione |
| [SciPy](https://scipy.org/) | >= 1.13 | Filtro Butterworth (SOS), STFT, PSD Welch |
| [NumPy](https://numpy.org/) | >= 1.26 | Array di segnale, FFT (rfft) |
| [Plotly](https://plotly.com/python/) | >= 5.22 | Grafici interattivi |
| [Pandas](https://pandas.pydata.org/) | >= 2.2 | CSV I/O, anteprima dati |

---

## 📁 Struttura del progetto

```
seismiclens/
├── app.py                     # App principale Streamlit (UI + orchestrazione)
├── requirements.txt           # Dipendenze Python
├── LICENSE                    # Licenza MIT
├── README.md                  # README inglese
├── docs/
│   ├── README_IT.md           # Questo file
│   ├── README_FR.md           # Documentation française
│   ├── README_ES.md           # Documentación española
│   └── README_DE.md           # Deutsche Dokumentation
└── utils/
    ├── __init__.py
    ├── data_loader.py         # MiniSEED, CSV, generatore sintetico
    └── signal_processing.py  # FFT, filtro, STA/LTA, PSD, spettrogramma
```

---

## 🗺️ Roadmap

Le seguenti funzionalità sono pianificate per le versioni future. I contributi sono benvenuti!

### v2.1 — Dati & I/O
- [ ] **Integrazione client FDSN** — interrogare IRIS / INGV direttamente dall'app senza download manuale
- [ ] **Supporto SAC** — caricare sismogrammi in formato SAC, ampiamente usato in sismologia accademica
- [ ] **Visualizzazione multi-traccia** — confrontare le tre componenti (Z, N, E) simultaneamente

### v2.2 — Elaborazione del segnale
- [ ] **Rimozione della risposta strumentale** — deconvoluzione di file RESP / StationXML per ottenere spostamento/velocità/accelerazione del suolo
- [ ] **STA/LTA adattivo** — STA/LTA ricorsivo con ottimizzazione automatica della soglia
- [ ] **Analisi del moto delle particelle** — diagrammi hodogramma per dati a tre componenti
- [ ] **Stima del Coda-Q** — attenuazione per scattering dall'inviluppo della coda

### v2.3 — Analisi avanzata
- [ ] **Visualizzazione del tensore dei momenti** — diagrammi "beach ball" dai parametri del meccanismo focale
- [ ] **Array processing** — beamforming e analisi di lentezza per array sismici
- [ ] **Picker ML delle fasi** — integrazione di PhaseNet o EQTransformer per il rilevamento automatico delle fasi
- [ ] **Stima della magnitudo** — calcolo della magnitudo locale (Ml) da ampiezza picco e correzione di stazione

### v3.0 — Piattaforma
- [ ] **Streaming in tempo reale** — connessione a server SeedLink per monitoraggio live
- [ ] **Persistenza della sessione** — salvare e ricaricare le configurazioni di analisi
- [ ] **REST API** — esporre le funzioni di elaborazione come endpoint per accesso programmatico
- [ ] **Immagine Docker** — deployment con un solo comando `docker run`

---

## 🤝 Contribuire

Contributi, segnalazioni di bug e richieste di funzionalità sono benvenuti!

1. **Fork** del repository
2. Crea un branch per la tua feature: `git checkout -b feature/nome-della-feature`
3. Fai commit seguendo le [Conventional Commits](https://www.conventionalcommits.org/): `git commit -m "feat: aggiungi la tua feature"`
4. Push del branch: `git push origin feature/nome-della-feature`
5. Apri una **Pull Request** verso `main`

### Stile del codice

- Segui **PEP 8** per il codice Python
- Mantieni le funzioni focalizzate e documentate con docstring
- Aggiungi o aggiorna i test quando introduci nuova logica di elaborazione del segnale
- Esegui `python -m py_compile app.py utils/*.py` prima di aprire una PR

### Segnalare bug

Apri una GitHub Issue includendo:
- Versione Python e sistema operativo
- Passi per riprodurre il problema
- Comportamento atteso vs. effettivo
- Se possibile, un file di esempio minimo (MiniSEED o CSV) che provoca il bug

---

## 📄 Licenza

Questo progetto è distribuito sotto la **Licenza MIT** — vedi il file [LICENSE](../LICENSE) per i dettagli.

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
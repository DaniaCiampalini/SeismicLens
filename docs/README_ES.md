<div align="center">

# 🌍 SeismicLens

**Analizador Interactivo de Formas de Onda Sísmicas**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../LICENSE)
[![ObsPy](https://img.shields.io/badge/ObsPy-1.4%2B-green)](https://docs.obspy.org/)
[![SciPy](https://img.shields.io/badge/SciPy-1.13%2B-8CAAE6?logo=scipy)](https://scipy.org/)

*Carga, filtra y analiza formas de onda sísmicas directamente en tu navegador — sin más instalación que Python.*

[🇬🇧 English](../README.md) · [🇮🇹 Italiano](README_IT.md) · [🇫🇷 Français](README_FR.md) · **🇪🇸 Español** · [🇩🇪 Deutsch](README_DE.md)

</div>

---

## 📋 Tabla de Contenidos

- [Descripción general](#-descripción-general)
- [Funcionalidades](#-funcionalidades)
- [Inicio rápido](#-inicio-rápido)
- [Guía de uso](#-guía-de-uso)
- [Obtener datos reales](#️-obtener-datos-reales)
- [Modelo sismológico](#-modelo-sismológico)
- [Fundamentos matemáticos](#-fundamentos-matemáticos)
- [Stack tecnológico](#️-stack-tecnológico)
- [Estructura del proyecto](#-estructura-del-proyecto)
- [Hoja de ruta](#️-hoja-de-ruta)
- [Contribuir](#-contribuir)
- [Licencia](#-licencia)

---

## 🔭 Descripción general

**SeismicLens** es un banco de trabajo de geofísica de código abierto, basado en el navegador y desarrollado con [Streamlit](https://streamlit.io/). Permite a estudiantes, investigadores y entusiastas de los terremotos explorar señales sísmicas sin escribir una sola línea de código.

**Lo que puedes hacer:**

- Generar **sismogramas sintéticos físicamente realistas** usando un modelo de velocidad cortical en capas inspirado en IASP91
- Cargar y analizar **formas de onda MiniSEED reales** de redes globales (IRIS, INGV, GEOFON, …)
- Aplicar un **filtro Butterworth de fase cero** para aislar bandas de frecuencia de interés
- Detectar automáticamente el inicio de ondas P con el clásico **algoritmo STA/LTA** (Allen, 1978)
- Descomponer la señal mediante **FFT** y visualizar el espectro de amplitud, el espectro de fase y la PSD de Welch
- Inspeccionar la evolución tiempo-frecuencia con un **espectrograma interactivo (STFT)**
- **Exportar** todos los datos procesados como CSV para análisis posterior en Python, MATLAB o Excel
- Cambiar entre **5 idiomas** (EN / IT / FR / ES / DE) y **temas oscuro / claro**

---

## ✨ Funcionalidades

| Función | Detalles |
|---|---|
|  Generador de formas de onda sintéticas | Ondas P, S y superficiales · modelo cortical en capas IASP91 · M, profundidad, distancia, ruido y duración configurables |
|  Carga MiniSEED | Datos reales desde IRIS FDSN o servicios web de INGV |
|  Carga CSV | Detección automática de formato de 1 columna (amplitud) o 2 columnas (tiempo, amplitud) |
| ️ Filtro Butterworth de fase cero | Pasa-banda configurable · orden 2–8 · sin distorsión de fase (`sosfiltfilt`) |
|  Análisis espectral FFT | Espectro de amplitud · espectro de fase · frecuencia dominante · centroide espectral · ancho de banda RMS |
|  Densidad espectral de potencia | Estimación PSD de Welch en counts²/Hz y dB re 1 count²/Hz |
| ️ Espectrograma (STFT) | Mapa de calor tiempo-frecuencia interactivo · escala de colores Inferno/Viridis |
|  Detector STA/LTA de onda P | Detector clásico Allen (1978) · O(N) con sumas prefijas · ventanas y umbral configurables |
|  Modelo de velocidad cortical | Tabla interactiva (Vp, Vs, Vp/Vs, coeficiente de Poisson, densidad) + gráfico de barras horizontal |
|  Panel de Teoría y Matemáticas | DFT/FFT con números complejos · diseño Butterworth · magnitud Richter y Mw · método de Wadati |
|  Exportación CSV | Señal filtrada · espectro FFT · PSD de Welch · razón STA/LTA |
|  Interfaz multilingüe | English · Italiano · Français · Español · Deutsch |
|  Tema oscuro / claro | Alternar en la barra lateral · gráficos Plotly adaptativos al tema |

---

## 🚀 Inicio rápido

### Requisitos previos

- Python **3.10 o superior**
- `pip` (incluido con Python)

### Instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/your-username/seismiclens.git
cd seismiclens

# 2. (Recomendado) Crear y activar un entorno virtual
python -m venv .venv
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate         # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Lanzar la aplicación
streamlit run app.py
```

La aplicación se abrirá automáticamente en **http://localhost:8501**.

> **Consejo:** En el primer arranque, ObsPy puede tardar unos segundos en inicializarse. Las ejecuciones posteriores son más rápidas gracias al caché de módulos de Streamlit.

---

## 📖 Guía de uso

### 1 — Elegir una fuente de datos

Abrir la **barra lateral** (☰ si está contraída) y seleccionar uno de los tres modos:

| Modo | Cuándo usar |
|---|---|
| **Terremoto sintético** | Exploración inmediata — no se necesita archivo. Ajusta magnitud (M 2–8), profundidad focal (5–200 km), distancia epicentral (10–500 km), nivel de ruido y duración. |
| **Cargar MiniSEED** | Sismogramas de banda ancha reales de redes globales. Descarga archivos `.mseed` desde IRIS o INGV (ver [Obtener datos reales](#️-obtener-datos-reales)). |
| **Cargar CSV** | Tus propios datos de series temporales. Una columna = muestras de amplitud; dos columnas = tiempo (s), amplitud. |

### 2 — Configurar el filtro Butterworth

| Parámetro | Valores típicos | Efecto |
|---|---|---|
| Corte bajo (Hz) | 0,01–2 Hz (telesísmico) · 0,5–5 Hz (regional) · 1–15 Hz (local) | Elimina la deriva de baja frecuencia y el ruido microsísmico |
| Corte alto (Hz) | Debe ser < Nyquist (fs/2) | Elimina el ruido cultural de alta frecuencia |
| Orden | 2–8 (por defecto 4) | Mayor orden → caída más pronunciada, más oscilaciones |

Activar/desactivar **pasa-banda de fase cero** para comparar la señal filtrada con la forma de onda cruda.

### 3 — Ajustar el detector STA/LTA

```
Regla general:  LTA >= 10 x STA
Umbral típico:  3 - 5
```

| Parámetro | Descripción |
|---|---|
| Ventana STA (s) | Promedio a corto plazo: captura la energía impulsiva de inicio (0,2–2 s) |
| Ventana LTA (s) | Promedio a largo plazo: sigue el nivel de ruido de fondo (5–60 s) |
| Umbral de disparo | Razón R por encima de la cual se declara una fase sísmica |

Bajar el umbral para captar eventos débiles; subirlo para suprimir disparos falsos en datos ruidosos.

### 4 — Explorar las pestañas de análisis

| Pestaña | Contenido |
|---|---|
| **Forma de onda** | Gráfico en dominio del tiempo · marcadores de llegada P y S · superposición de señal cruda activable |
| **Análisis espectral** | Espectro de amplitud FFT · espectro de fase opcional · PSD de Welch opcional |
| **Espectrograma** | Mapa de calor tiempo-frecuencia STFT |
| **STA/LTA** | Función característica STA/LTA · ventanas de disparo resaltadas |
| **Modelo de velocidad** | Tabla inspirada en IASP91 + gráfico de barras Vp/Vs |
| **Teoría y Matemáticas** | DFT, Butterworth, PSD, STFT, física de ondas, escalas de magnitud — con ecuaciones |
| **Exportar** | Descargar archivos CSV para cada cantidad calculada |

### 5 — Exportar resultados

Todos los datos procesados pueden descargarse como CSV desde la pestaña **Exportar**:

| Archivo | Contenido |
|---|---|
| `signal.csv` | Tiempo (s), amplitud filtrada (counts) |
| `fft.csv` | Frecuencia (Hz), amplitud, fase (grados) |
| `psd.csv` | Frecuencia (Hz), PSD (counts²/Hz) |
| `stalta.csv` | Tiempo (s), razón STA/LTA |

---

## 🛰️ Obtener datos reales

### IRIS (Incorporated Research Institutions for Seismology)

1. Ir a **[IRIS Wilber 3](https://ds.iris.edu/wilber3/find_event)**
2. Buscar un terremoto por fecha, región o magnitud
3. Seleccionar una estación sísmica cercana al evento
4. Elegir **MiniSEED** como formato de exportación y descargar

### INGV (Istituto Nazionale di Geofisica e Vulcanologia — Italia)

1. Abrir el **[servicio web INGV FDSN](https://webservices.ingv.it/swagger-ui/index.html)**
2. Usar el endpoint `/dataselect` con parámetros de red, estación y tiempo
3. Establecer el formato como `miniseed` y descargar

### Otras redes

| Red | URL |
|---|---|
| GEOFON (GFZ Potsdam) | https://geofon.gfz-potsdam.de/waveform/ |
| EMSC | https://www.seismicportal.eu/ |
| ORFEUS | https://www.orfeus-eu.org/data/eida/ |

---

## 🌐 Modelo sismológico

### Modelo de velocidad cortical en capas (inspirado en IASP91)

| Capa | Profundidad (km) | Vp (km/s) | Vs (km/s) | Vp/Vs | Poisson ν |
|---|---|---|---|---|---|
| Corteza superior | 0–15 | 5,80 | 3,36 | 1,726 | 0,249 |
| Corteza media | 15–25 | 6,50 | 3,75 | 1,733 | 0,252 |
| Corteza inferior | 25–35 | 7,00 | 4,00 | 1,750 | 0,257 |
| Manto superior | 35–200 | 8,04 | 4,47 | 1,798 | 0,272 |

### Física de la forma de onda sintética

```
Onda P        :  f ~ 6-12 Hz,   envolvente gaussiana,  amplitud ~ 10^(0.8M-2.5) x 0.15
Onda S        :  f ~ 2-6 Hz,    envolvente gaussiana,  amplitud ~ 10^(0.8M-2.5) x 0.65
Ondas superf. :  f ~ 0.3-1 Hz,  coda exponencial,      amplitud ~ 10^(0.8M-2.5) x 0.40
Ruido         :  Butterworth pasa-banda 0.5-30 Hz, normalizado a sigma
```

Tiempos de viaje calculados a partir de la distancia hipocentral `R = sqrt(d^2 + h^2)`.

---

## 📐 Fundamentos matemáticos

### Transformada Discreta de Fourier (DFT)

```
X[k] = sum_{n=0}^{N-1}  x[n] * exp(-j * 2pi * k * n / N)

|X[k]|  ->  amplitud en  f_k = k * fs / N  Hz
angulo(X[k])  ->  fase = atan2(Im(X[k]), Re(X[k]))

Espectro unilateral normalizado:  A[k] = (2/N) * |X[k]|
```

La FFT (Cooley–Tukey, 1965) reduce la complejidad de O(N²) a **O(N log N)**.  
Para señales reales el espectro es hermítico: `X[N-k] = conj(X[k])`, por lo que solo existen N/2+1 bins únicos (aprovechado por `scipy.fft.rfft`).

### Filtro Butterworth de fase cero

```
|H(jw)|^2 = 1 / [1 + (w/wc)^(2n)]

Caída de un solo paso:             20*n  dB/década
sosfiltfilt (orden efectivo 2n):   40*n  dB/década, sin distorsión de fase
```

Implementado en forma SOS (Secciones de Segundo Orden) para estabilidad numérica.

### STA/LTA (Allen, 1978)

```
STA(t) = (1/Nsta) * sum( x^2[t-Nsta : t] )
LTA(t) = (1/Nlta) * sum( x^2[t-Nlta : t] )
R(t)   = STA(t) / LTA(t)   ->  disparo cuando R > umbral
```

Implementación O(N) usando sumas prefijas: `cs = cumsum(x^2)`.

### Método de Wadati

```
R = sqrt(d^2 + h^2)              (distancia hipocentral)
t_P = R / Vp  ,  t_S = R / Vs
d ~ (t_S - t_P) * Vp * Vs / (Vp - Vs)
```

---

## 🛠️ Stack tecnológico

| Biblioteca | Versión | Rol |
|---|---|---|
| [Streamlit](https://streamlit.io/) | >= 1.35 | Interfaz web, gestión de estado reactivo |
| [ObsPy](https://docs.obspy.org/) | >= 1.4 | I/O MiniSEED, detendencia de trazas |
| [SciPy](https://scipy.org/) | >= 1.13 | Filtro Butterworth (SOS), STFT, PSD de Welch |
| [NumPy](https://numpy.org/) | >= 1.26 | Arrays de señal, FFT (rfft) |
| [Plotly](https://plotly.com/python/) | >= 5.22 | Gráficos interactivos |
| [Pandas](https://pandas.pydata.org/) | >= 2.2 | I/O CSV, vista previa de datos |

---

## 📁 Estructura del proyecto

```
seismiclens/
├── app.py                     # Aplicación Streamlit principal (UI + orquestación)
├── requirements.txt           # Dependencias de Python
├── LICENSE                    # Licencia MIT
├── README.md                  # Documentación principal (inglés)
├── docs/
│   ├── README_IT.md           # Documentazione italiana
│   ├── README_FR.md           # Documentation française
│   ├── README_ES.md           # Este archivo
│   └── README_DE.md           # Deutsche Dokumentation
└── utils/
    ├── __init__.py
    ├── data_loader.py         # MiniSEED, CSV, generador de formas de onda sintéticas
    └── signal_processing.py  # FFT, filtro Butterworth, STA/LTA, PSD, espectrograma
```

---

## 🗺️ Hoja de ruta

Las siguientes funciones están planificadas para versiones futuras. ¡Las contribuciones son bienvenidas!

### v2.1 — Datos & E/S
- [ ] **Integración del cliente FDSN** — consultar IRIS / INGV directamente desde la app sin descarga manual
- [ ] **Soporte de archivos SAC** — cargar sismogramas en formato SAC, ampliamente usado en sismología académica
- [ ] **Visualización multi-traza** — graficar y comparar registros de tres componentes (Z, N, E) simultáneamente

### v2.2 — Procesamiento de señal
- [ ] **Eliminación de respuesta instrumental** — deconvolucionar archivos RESP / StationXML para obtener desplazamiento/velocidad/aceleración del suelo
- [ ] **STA/LTA adaptativo** — STA/LTA recursivo con optimización automática del umbral
- [ ] **Análisis de movimiento de partícula** — gráficos hodograma para datos de componentes Z-N-E
- [ ] **Estimación de Coda-Q** — atenuación por dispersión a partir del decaimiento de la envolvente de la coda

### v2.3 — Análisis avanzado
- [ ] **Visualización de tensor de momento** — diagramas de playa desde parámetros del mecanismo focal
- [ ] **Procesamiento de arrays** — beamforming y análisis de lentitud para arrays sísmicos
- [ ] **Detector de fases por aprendizaje automático** — integrar PhaseNet o EQTransformer para detección automática de fases
- [ ] **Estimación de magnitud** — cálculo de magnitud local (Ml) a partir de amplitud pico y corrección de estación

### v3.0 — Plataforma
- [ ] **Streaming en tiempo real** — conectar a servidores SeedLink para monitoreo de formas de onda en vivo
- [ ] **Persistencia de sesión de usuario** — guardar y recargar configuraciones de análisis
- [ ] **API REST** — exponer funciones de procesamiento como endpoints para acceso programático
- [ ] **Imagen Docker** — despliegue con un solo comando con `docker run`

---

## 🤝 Contribuir

¡Las contribuciones, informes de errores y solicitudes de funciones son bienvenidos!

1. **Hacer fork** del repositorio
2. Crear una rama de función: `git checkout -b feature/nombre-de-tu-funcion`
3. Hacer commit de los cambios siguiendo [Conventional Commits](https://www.conventionalcommits.org/): `git commit -m "feat: añadir tu función"`
4. Hacer push a la rama: `git push origin feature/nombre-de-tu-funcion`
5. Abrir un **Pull Request** contra `main`

### Estilo de código

- Seguir **PEP 8** para código Python
- Mantener las funciones enfocadas y documentadas con docstrings
- Añadir o actualizar pruebas al introducir nueva lógica de procesamiento de señal
- Ejecutar `python -m py_compile app.py utils/*.py` antes de abrir un PR

### Reportar errores

Por favor abre un GitHub Issue e incluye:
- Versión de Python y sistema operativo
- Pasos para reproducir
- Comportamiento esperado vs. real
- Si es posible, un archivo de muestra mínimo (MiniSEED o CSV) que reproduzca el error

---

## 📄 Licencia

Este proyecto está licenciado bajo la **Licencia MIT** — consulta el archivo [LICENSE](../LICENSE) para más detalles.

```
MIT License  —  Copyright (c) 2026 Dania Ciampalini & Dario Ciampalini

Por la presente se concede permiso, sin cargo, a cualquier persona que obtenga
una copia de este software y los archivos de documentación asociados (el "Software"),
para tratar el Software sin restricciones, incluyendo sin limitación los derechos
de usar, copiar, modificar, fusionar, publicar, distribuir, sublicenciar y/o vender
copias del Software, y permitir a las personas a quienes se les proporcione el Software
que lo hagan, sujeto a las siguientes condiciones:

El aviso de derechos de autor anterior y este aviso de permiso se incluirán en todas
las copias o partes sustanciales del Software.

EL SOFTWARE SE PROPORCIONA "TAL CUAL", SIN GARANTÍA DE NINGÚN TIPO, EXPRESA O IMPLÍCITA,
INCLUYENDO PERO NO LIMITADO A GARANTÍAS DE COMERCIABILIDAD, IDONEIDAD PARA UN PROPÓSITO
PARTICULAR Y NO INFRACCIÓN.
```

| Interfaz multilingüe | Italiano, English, Français, Español, Deutsch |

---

## Modelo sismológico

### Modelo de velocidad cortical en capas (inspirado en IASP91)

| Capa | Profundidad (km) | Vp (km/s) | Vs (km/s) | Vp/Vs | Poisson ν |
|---|---|---|---|---|---|
| Corteza superior | 0–15 | 5.80 | 3.36 | 1.726 | 0.249 |
| Corteza media | 15–25 | 6.50 | 3.75 | 1.733 | 0.252 |
| Corteza inferior | 25–35 | 7.00 | 4.00 | 1.750 | 0.257 |
| Manto superior | 35–200 | 8.04 | 4.47 | 1.798 | 0.272 |

### Física de la forma de onda sintética

```
Onda P        :  f ~ 6–12 Hz,   envolvente gaussiana,  amplitud ∝ 10^(0.8M−2.5) × 0.15
Onda S        :  f ~ 2–6 Hz,    envolvente gaussiana,  amplitud ∝ 10^(0.8M−2.5) × 0.65
Ondas superf. :  f ~ 0.3–1 Hz,  coda exponencial,      amplitud ∝ 10^(0.8M−2.5) × 0.40
Ruido         :  Butterworth pasa-banda 0.5–30 Hz, normalizado a σ
```

Tiempos de recorrido desde la distancia hipocentral `R = sqrt(d² + h²)`.

---

## Fundamentos matemáticos

### Transformada de Fourier Discreta (DFT)

```
X[k] = suma_{n=0}^{N-1}  x[n] · exp(−j · 2π · k · n / N)

|X[k]|  →  amplitud a la frecuencia  f_k = k · fs / N  (Hz)
∠X[k]   →  fase = argumento del número complejo X[k]
           = atan2(Im(X[k]), Re(X[k]))

Espectro unilateral normalizado:  A[k] = (2/N) · |X[k]|
```

La FFT (Cooley–Tukey, 1965) reduce la complejidad de O(N²) a O(N log N).
Para señales reales el espectro es hermítico — `X[N−k] = conj(X[k])` — por lo que solo existen N/2+1 bins independientes (`scipy.fft.rfft`).

### Números complejos en el dominio de la frecuencia

Cada coeficiente `X[k]` es un número complejo:

```
X[k] = Re(X[k]) + j · Im(X[k])
     = |X[k]| · exp(j · φ[k])          (forma polar)

|X[k]| = sqrt(Re² + Im²)               (amplitud)
φ[k]   = atan2(Im(X[k]), Re(X[k]))     (fase)
```

La fórmula de Euler `exp(jθ) = cos(θ) + j·sin(θ)` es el fundamento matemático:
la DFT proyecta la señal sobre las bases coseno (parte real) y seno (parte imaginaria).

### Filtro Butterworth de fase cero

```
|H(jω)|² = 1 / [1 + (ω/ωc)^(2n)]

Atenuación más allá de ωc:   20·n dB/década (pasada simple)
Con sosfiltfilt (orden efectivo 2n):  40·n dB/década
```

Implementado en forma SOS (Secciones de Segundo Orden) para estabilidad numérica.
`sosfiltfilt` aplica el filtro en sentido directo y luego inverso: la respuesta de fase se cancela exactamente, preservando los tiempos de llegada de las ondas.

### STA/LTA

```
STA(t) = media( x²[t−Nsta : t] )
LTA(t) = media( x²[t−Nlta : t] )
R(t)   = STA(t) / LTA(t)   →  disparo cuando R > umbral
```

Implementación O(N) mediante sumas prefijas: `cs = cumsum(x²)`.

### Método de Wadati

```
Distancia hipocentral :  R = sqrt(d² + h²)
Tiempos de llegada :     t_P = R / Vp
                         t_S = R / Vs
Distancia epicentral :   d ≈ (t_S − t_P) · Vp · Vs / (Vp − Vs)
```

---

## Inicio rápido

```bash
pip install -r requirements.txt
streamlit run app.py
```

Abrir http://localhost:8501 en el navegador.

### Cómo usar la aplicación

1. Elegir una fuente de datos en la barra lateral: sismo sintético, archivo MiniSEED o CSV.
2. Configurar el filtro Butterworth pasa-banda (corte bajo, corte alto, orden).
3. Ajustar el detector STA/LTA (ventana STA, ventana LTA, umbral).
4. Explorar las pestañas: Forma de onda, Análisis espectral, Espectrograma, STA/LTA, Modelo de velocidad, Teoría y Matemáticas.
5. Exportar los resultados como archivos CSV.

### Obtener datos MiniSEED reales

- IRIS FDSN: https://ds.iris.edu/wilber3/find_event
- INGV: https://webservices.ingv.it/swagger-ui/index.html
  Formato de exportación: MiniSEED

---

## Stack tecnológico

| Biblioteca | Rol |
|---|---|
| ObsPy | Lectura MiniSEED, detendencia |
| SciPy | Filtro Butterworth (SOS), STFT, Welch PSD |
| NumPy | Arrays de señal, FFT |
| Plotly | Gráficos interactivos |
| Streamlit | Interfaz web |
| Pandas | CSV I/O, vista previa de datos |

---

## Estructura del proyecto

```
seismiclens/
├── app.py                     # App principal Streamlit (UI + orquestación)
├── requirements.txt
├── docs/
│   ├── README_EN.md
│   ├── README_IT.md
│   ├── README_FR.md
│   ├── README_ES.md           # este archivo
│   └── README_DE.md
└── utils/
    ├── data_loader.py         # MiniSEED, CSV, generador sintético
    └── signal_processing.py  # FFT, filtro, STA/LTA, PSD, espectrograma
```


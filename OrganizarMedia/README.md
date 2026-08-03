# 📂 OrgMedia (v0.1)

[English](#english) | [Español](#español)

---

<a name="english"></a>
## 🇬🇧 English

Python script designed to automate the organization of multimedia files (photos and assets with EXIF metadata) into a clean **Location / Month_Year** directory structure.

### 💡 Why I built this project
Coming from a professional background handling large volumes of multimedia assets, I faced the chaos of having thousands of scattered files with no chronological or geographical order—and the constant risk of unrecoverable data loss. This script was born as my first serious automation project to solve a real-world problem while applying software engineering best practices.

### 🛠️ Engineering Decisions (v0.1)
Unlike a basic file-mover script, this version includes:
- **Cryptographic Security (SHA-256):** Full-file hashing via streaming chunks to guarantee the absolute integrity of heavy files or RAW footage before deleting the source.
- **In-Memory Caching & Spatial Approximation:** Coordinates rounded to ~100-meter grids to avoid redundant network requests to the geocoding API.
- **Strict Rate Limiting:** Controlled delays (`time.sleep`) to comply with map server policies and prevent IP blocks (HTTP 429).
- **Defensive Error Handling:** Robust try/except blocks to prevent crashes from corrupted data or network drops.

### ⚙️ Requirements & Installation
1. Clone or download this repository.
2. Open your terminal in the project folder and install dependencies:
   ```bash
   pip install -r requirements.txt
```

### 🚀 Usage
Run the script from your terminal:
```bash
python organizador.py
```
The program will prompt you to drop or type the folder path you want to organize.

---


<a name="español"></a>
## 🇪🇸 Español

Script en Python diseñado para automatizar la organización de archivos multimedia (fotografías y material con metadatos EXIF) en una estructura limpia de directorios basada en **Ubicación / Mes_Año**.

## 💡 ¿Por qué construí este proyecto?
Como profesional con experiencia en el manejo de grandes volúmenes de material multimedia, me enfrenté al caos de tener miles de archivos dispersos sin orden cronológico ni geográfico. Y el peligro de perdida de información no recuperable. Este script nace como mi primer proyecto serio de automatización para resolver un problema real, aplicando buenas prácticas de desarrollo.
## 🛠️ Decisiones de Ingeniería Implementadas en la v0.1
A diferencia de un script básico que solo "mueve archivos", esta versión incluye:
- **Seguridad Criptográfica (SHA-256):** Implementación de hashing completo mediante lectura por bloques (*streaming chunks*) para garantizar la integridad absoluta de archivos pesados o material RAW antes de eliminar el origen.
- **Caché en Memoria y Aproximación Espacial:** Redondeo de coordenadas a ~100 metros para evitar peticiones repetidas de red a la API de geocodificación.
- **Rate Limiting Estricto:** Pausas controladas (`time.sleep`) para cumplir con las políticas de uso de servicios de mapas y evitar bloqueos de IP (HTTP 429).
- **Manejo Defensivo:** Bloqueo de errores y caídas por estructuras de datos corruptas o pérdida de red.

## ⚙️ Requisitos e Instalación

1. Clona este repositorio o descarga los archivos.
2. Asegúrate de tener Python instalado y abre tu terminal en la carpeta del proyecto.
3. Instala las dependencias ejecutando:
   ```bash
   pip install -r requirements.txt
   ### 🚀 Uso
Ejecuta el script:
```bash
python organizador.py
```

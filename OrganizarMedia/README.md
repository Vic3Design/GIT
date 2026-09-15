# 📂 OrgMedia (v0.2)

[English](#english) | [Español](#español)

---

<a name="english"></a>
## 🇬🇧 English

Python script designed to automate the organization of multimedia files (photos, videos, and audio assets with EXIF/metadata) into a clean **Year_Month / Location** directory structure.

### 💡 Why I built this project
Coming from a professional background handling large volumes of multimedia assets, I faced the chaos of having thousands of scattered files with no chronological or geographical order—and the constant risk of unrecoverable data loss. This script was born as my first serious automation project to solve a real-world problem while applying software engineering best practices.

### 🛠️ Engineering Decisions
Unlike a basic file-mover script, this version includes:
- **Cryptographic Security (SHA-256):** Full-file hashing via streaming chunks to guarantee the absolute integrity of heavy files or RAW footage before deleting the source.
- **In-Memory Caching & Spatial Approximation:** Coordinates rounded to ~100-meter grids to avoid redundant network requests to the geocoding API.
- **Strict Rate Limiting:** Controlled delays (`time.sleep`) to comply with map server policies and prevent IP blocks (HTTP 429).
- **Defensive Error Handling:** Robust try/except blocks to prevent crashes from corrupted data or network drops.

### 📁 Supported File Formats
- **Images:** `.jpg`, `.jpeg`, `.png`, `.heic`
- **Video & Audio:** `.mov`, `.mp4`, `.mp3`, `.wav`, `.m4a`

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

Script en Python diseñado para automatizar la organización de archivos multimedia (fotografías, videos y audios con metadatos EXIF) en una estructura limpia de directorios basada en Año_Mes / Ubicación.

## 💡 ¿Por qué construí este proyecto?

Como profesional con experiencia en el manejo de grandes volúmenes de material multimedia, me enfrenté al caos de tener miles de archivos dispersos sin orden cronológico ni geográfico. Y el peligro de perdida de información no recuperable. Este script nace como mi primer proyecto serio de automatización para resolver un problema real, aplicando buenas prácticas de desarrollo.

## 🛠️ Decisiones de Ingeniería Implementadas en la v0.1

A diferencia de un script básico que solo "mueve archivos", esta versión incluye:
- **Seguridad Criptográfica (SHA-256):** Implementación de hashing completo mediante lectura por bloques (*streaming chunks*) para garantizar la integridad absoluta de archivos pesados o material RAW antes de eliminar el origen.
- **Caché en Memoria y Aproximación Espacial:** Redondeo de coordenadas a ~100 metros para evitar peticiones repetidas de red a la API de geocodificación.
- **Rate Limiting Estricto:** Pausas controladas (`time.sleep`) para cumplir con las políticas de uso de servicios de mapas y evitar bloqueos de IP (HTTP 429).
- **Manejo Defensivo:** Bloqueo de errores y caídas por estructuras de datos corruptas o pérdida de red.

## 📁 Formatos Soportados

Imágenes: .jpg, .jpeg, .png, .heic

Video y Audio: .mov, .mp4, .mp3, .wav, .m4a

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
## Historial de cambios / Changelog

### [v0.2.2] - 2026-09
#### Fixed
- **DNG/TIFF Metadata Crash:** Replaced legacy `_getexif()` with Pillow's universal `getexif()` to prevent attribute errors on `.dng` files and complex EXIF structures.
- **Indentation & Pylance Errors:** Fixed `try...except` block alignment and variable scoping (`exif`) inside `obtener_metadatos_imagen()`.

#### Added
- Support for additional video and audio formats: `.hevc`, `.mkv`, `.avi`, `.webm`, `.aac`.
- Explicit support for `.dng` RAW image files.

---

## 📁 Supported Formats

| Category | Extensions |
| :--- | :--- |
| **Images** | `.jpg`, `.jpeg`, `.png`, `.heic`, `.dng` |
| **Video & Audio** | `.mov`, `.mp4`, `.mp3`, `.wav`, `.m4a`, `.hevc`, `.mkv`, `.avi`, `.webm`, `.aac` |

v0.2 - Directory Structure Overhaul & Bug Fixes
🔄 Changed

Better Organization: Swapped the output folder hierarchy. The script now organizes media by Year_Month first, and then by Location (e.g., 2026_Sep/Caracas_Chacao/), making it much easier to browse events chronologically.

🐛 Fixed

Date Fallback Dictionary Bug: Fixed an issue where files lacking EXIF metadata failed to get the correct Spanish month name from the OS modification date. The month is now properly parsed as an integer to match the global dictionary.

Double Exit Prompt: Removed a duplicate input() pause when a user provided an invalid directory path, preventing a double prompt upon exiting the script.

🇪🇸 Español

## 📝 Historial de Versiones

### [v0.2.2] - 2026-09
#### Corregido
- **Error en metadatos DNG/TIFF:** Reemplazado `_getexif()` legacy por `getexif()` universal en Pillow para evitar fallos de atributo en archivos `.dng` y estructuras EXIF complejas.
- **Estructura de sangría y Pylance:** Alineación de bloques `try...except` y alcance de variables (`exif`) en la función `obtener_metadatos_imagen()`.

#### Añadido
- Soporte para nuevos formatos de video y audio: `.hevc`, `.mkv`, `.avi`, `.webm`, `.aac`.
- Soporte explícito para formato de imagen RAW `.dng`.

---

## 📁 Formatos Soportados

| Tipo | Extensiones |
| :--- | :--- |
| **Imágenes** | `.jpg`, `.jpeg`, `.png`, `.heic`, `.dng` |
| **Video y Audio** | `.mov`, `.mp4`, `.mp3`, `.wav`, `.m4a`, `.hevc`, `.mkv`, `.avi`, `.webm`, `.aac` |

v0.2 - Reestructuración de Directorios y Corrección de Errores
🔄 Cambios

Mejor Organización: Se invirtió la jerarquía de las carpetas de salida. El script ahora organiza los archivos primero por Año_Mes y luego por Ubicación (ej. 2026_Sep/Caracas_Chacao/), facilitando la navegación cronológica de los eventos.

🐛 Correcciones

Error en Diccionario de Fechas (Fallback): Se solucionó un problema donde los archivos sin metadatos EXIF no obtenían el nombre del mes en español a partir de la fecha de modificación del sistema. Ahora el mes se extrae correctamente como número entero para coincidir con el diccionario global.

Doble Confirmación de Salida: Se eliminó una pausa redundante con input() cuando el usuario introducía una ruta de directorio inválida, evitando que el programa pidiera confirmación dos veces al salir.

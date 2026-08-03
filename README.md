# 📂 OrgMedia (v0.1)

[English](https://www.google.com/search?q=%23english) | [Español](https://www.google.com/search?q=%23espa%C3%B1ol)

---

## 🇬🇧 English

Python script designed to automate the organization of multimedia files (photos and assets with EXIF metadata) into a clean **Location / Month_Year** directory structure.

### 🎬 The Editor's Reality Check

Let's talk about the invisible tax of video production: **the chaos of raw media.**

If you are a video editor or media professional, you know the drill. You finish a massive shoot, drop a 500GB hard drive on your desk, and suddenly you are staring at a digital crime scene: thousands of clips and photos scattered across random folders with names like `DCIM_1042.JPG`, zero geographical context, and completely out of chronological order.

Manually sorting thousands of heavy assets doesn't just eat up entire weekends—it burns the creative energy you should be putting into your timeline. Worse yet? Manual dragging and dropping at 3:00 AM opens the door to the ultimate editor's nightmare: **accidental overwrites and unrecoverable data loss.**

### 💡 Why I Built This

This script was born as my first serious automation project to solve a real-world problem. Coming from a professional background handling large volumes of multimedia assets, I needed a tool I could actually trust with production-grade footage.

### 🛠️ Engineering Decisions (v0.1)

Unlike a basic file-mover script, this version is built with production safety in mind:

* **Cryptographic Security (SHA-256):** Full-file hashing via streaming chunks to guarantee the absolute integrity of heavy files or RAW footage before touching the source.
* **In-Memory Caching & Spatial Approximation:** Coordinates rounded to ~100-meter grids to avoid redundant network requests to the geocoding API.
* **Strict Rate Limiting:** Controlled delays (`time.sleep`) to comply with map server policies and prevent IP blocks (HTTP 429).
* **Defensive Error Handling:** Robust try/except blocks to prevent crashes from corrupted data or network drops.

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

## 🇪🇸 Español

Script en Python diseñado para automatizar la organización de archivos multimedia (fotografías y material con metadatos EXIF) en una estructura limpia de directorios basada en **Ubicación / Mes_Año**.

### 🎬 La Realidad del Editor de Video

Hablemos del costo invisible de la producción audiovisual: **el caos del material bruto.**

Si eres editor de video o profesional multimedia, conoces la historia. Terminas un rodaje masivo, conectas un disco duro de 500GB al escritorio y de repente te enfrentas a una escena del crimen digital: miles de clips y fotos dispersos en carpetas aleatorias bajo nombres como `DCIM_1042.JPG`, sin contexto geográfico y totalmente fuera de orden cronológico.

Ordenar manualmente miles de archivos pesados no solo se traga fines de semana enteros, sino que quema la energía creativa que deberías estar invirtiendo en tu timeline de edición. ¿Y lo peor? Organizar a las 3:00 a.m. arrastrando y soltando archivos abre la puerta a la pesadilla de cualquier editor: **sobrescrituras accidentales y pérdida de material irrecuperable.**

### 💡 ¿Por Qué Construí Esto?

Este script nace como mi primer proyecto serio de automatización para resolver un problema real. Viniendo de un entorno profesional donde se manejan grandes volúmenes de material multimedia, necesitaba una herramienta en la que realmente pudiera confiar con material de producción.

### 🛠️ Decisiones de Ingeniería Implementadas en la v0.1

A diferencia de un script básico para mover archivos, esta versión está diseñada con la seguridad de producción como prioridad:

* **Seguridad Criptográfica (SHA-256):** Hashing completo mediante lectura por bloques (*streaming chunks*) para garantizar la integridad absoluta de archivos pesados o material RAW antes de tocar el origen.
* **Caché en Memoria y Aproximación Espacial:** Redondeo de coordenadas (~100 metros) para evitar peticiones repetidas a la API.
* **Rate Limiting Estricto:** Pausas controladas para cumplir con las políticas de servidores y evitar bloqueos de IP.
* **Manejo Defensivo:** Bloqueo de errores y caídas por estructuras de datos corruptas o pérdida de red.

### ⚙️ Requisitos e Instalación

1. Clona o descarga este repositorio.
2. Instala las dependencias:
```bash
pip install -r requirements.txt

```



### 🚀 Uso

Ejecuta el script:

```bash
python organizador.py

```

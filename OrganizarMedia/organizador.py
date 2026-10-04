"""
Script v0.3: Organizador de Multimedia Seguro con ExifTool
Descripción: Este script busca organizar carpetas de archivos multimedia 
de forma práctica y segura, utilizando metadatos optenidos con pillow pymediainfo, control de tráfico 
de red y seguridad criptográfica por hashing SHA-256 al 100% para garantizar 
la integridad absoluta de los archivos originales en el proceso de reubicación.
agrega '.dng', '.hevc', '.mkv', '.avi', '.webm', '.aac' y refuerza la extraccion de datos EXIF
"""

import os
import sys
import platform
import urllib.request
import zipfile
import tarfile
import shutil
import time
import hashlib
import subprocess
from datetime import datetime
from PIL import Image, ExifTags
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError, GeocoderUnavailable
try:
    import exiftool  # type: ignore
except ImportError:
    exiftool = None # PyExifTool para extracción avanzada de metadatos de video

def get_exiftool_path():
    """Retorna la ruta absoluta del binario local embebido en /tools."""
    system = platform.system()
    base_dir = os.path.join(os.path.dirname(__file__), "tools")
    
    if system == "Windows":
        return os.path.join(base_dir, "win", "exiftool.exe")
    elif system == "Darwin":
        return os.path.join(base_dir, "mac", "exiftool")
    elif system == "Linux":
        return os.path.join(base_dir, "linux", "exiftool")
    return None


def check_exiftool_version(binary_path):
    """Ejecuta 'exiftool -ver' y retorna la versión o None."""
    if not binary_path:
        return None
    try:
        result = subprocess.run(
            [binary_path, "-ver"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=3
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return None


def download_and_extract_exiftool():
    """Descarga y extrae el binario de ExifTool."""
    system = platform.system()
    binary_path = get_exiftool_path()
    if not binary_path:
        return False

    base_dir = os.path.dirname(binary_path)
    binary_name = os.path.basename(binary_path)
    version_str = "13.10"

    if system == "Windows":
        url = f"https://exiftool.org/exiftool-{version_str}_64.zip"
        is_zip = True
    elif system == "Darwin":
        url = f"https://exiftool.org/exiftool-{version_str}.zip"
        is_zip = True
    elif system == "Linux":
        url = f"https://exiftool.org/Image-ExifTool-{version_str}.tar.gz"
        is_zip = False
    else:
        return False

    os.makedirs(base_dir, exist_ok=True)
    temp_archive = os.path.join(base_dir, f"exiftool_temp.{'zip' if is_zip else 'tar.gz'}")

    headers = {'User-Agent': 'Mozilla/5.0'}
    req = urllib.request.Request(url, headers=headers)
    
    with urllib.request.urlopen(req, timeout=5) as response, open(temp_archive, 'wb') as out_file:
        shutil.copyfileobj(response, out_file)

    if is_zip:
        with zipfile.ZipFile(temp_archive, 'r') as zip_ref:
            zip_ref.extractall(base_dir)
    else:
        with tarfile.open(temp_archive, 'r:gz') as tar_ref:
            tar_ref.extractall(base_dir)
            
        extracted_folder = None
        for item in os.listdir(base_dir):
            item_path = os.path.join(base_dir, item)
            if os.path.isdir(item_path) and item.startswith("Image-ExifTool-"):
                extracted_folder = item_path
                break
        
        if extracted_folder:
            for sub_item in os.listdir(extracted_folder):
                shutil.move(os.path.join(extracted_folder, sub_item), os.path.join(base_dir, sub_item))
            shutil.rmtree(extracted_folder)

    if os.path.exists(temp_archive):
        os.remove(temp_archive)

    if system == "Windows":
        for root, _, files in os.walk(base_dir):
            for file in files:
                if file.startswith("exiftool") and file.endswith(".exe") and file != binary_name:
                    shutil.move(os.path.join(root, file), os.path.join(base_dir, binary_name))
                    break

    if system in ["Darwin", "Linux"] and os.path.exists(binary_path):
        os.chmod(binary_path, 0o755)

    return os.path.exists(binary_path)


def check_periodic_updates(dias_intervalo=30):
    """
    Audita la versión local del ejecutable.
    Retorna el modo de motor activo: 'exiftool' o 'pillow'.
    """
    archivo_registro = ".last_update"
    fecha_actual = datetime.now()
    
    local_binary = get_exiftool_path()
    local_version = check_exiftool_version(local_binary)
    system_version = None if local_version else check_exiftool_version("exiftool")
    active_version = local_version or system_version

    debe_actualizar = False

    if not active_version:
        debe_actualizar = True
    elif not os.path.exists(archivo_registro):
        debe_actualizar = True
    else:
        with open(archivo_registro, "r") as f:
            fecha_texto = f.read().strip()
            try:
                ultima_fecha = datetime.fromisoformat(fecha_texto)
                if (fecha_actual - ultima_fecha).days >= dias_intervalo:
                    debe_actualizar = True
            except ValueError:
                debe_actualizar = True

    if debe_actualizar:
        if not active_version:
            print("\n⏳ Configurando el motor de metadatos por primera vez :)")
        else:
            print("\n⏳ Verificando actualizaciones de compatibilidad para cámaras y formatos :)")

        try:
            if download_and_extract_exiftool():
                new_version = check_exiftool_version(local_binary)
                print(f"✅ Motor de metadatos actualizado (v{new_version}).\n")
                
                # Guarda o actualiza la fecha en .last_update
                with open(archivo_registro, "w") as f:
                    f.write(fecha_actual.isoformat())
                return "exiftool"
            else:
                raise Exception("Error en descarga/extracción")

        except Exception:
            if local_version:
                print(f"ℹ️ Usando motor local existente (v{local_version}).\n")
                return "exiftool"
            elif system_version:
                print(f"ℹ️ Usando motor del sistema (v{system_version}).\n")
                return "exiftool"
            else:
                # FALLBACK A PILLOW: Sin ExifTool local, del sistema ni conexión
                print("⚠️ ADVERTENCIA: No se pudo obtener ExifTool.")
                print("   Se utilizará Pillow en modo de respaldo (solo imágenes básicas).")
                print("   Los archivos de video y formatos avanzados no tendrán extracción de metadatos.\n")
                return "pillow"
    
    return "exiftool"


# Inicialización en organizador.py
ENGINE_MODE = check_periodic_updates()

# Leer metadatos de video/audio de forma robusta
try:
    from pymediainfo import MediaInfo
    HAY_MEDIAINFO = True
except ImportError:
    HAY_MEDIAINFO = False
    print("⚠️ Advertencia: 'pymediainfo' no está instalado. Soporte básico para fechas de creación en video.")
    
# Inicialización del geolocalizador y variables globales de estado
geolocator = Nominatim(user_agent="orgmedia_v02")
cache_ubicaciones = {}  # Caché en memoria para optimizar peticiones de red a la API

# --- FUNCIONES DE SEGURIDAD Y HASHING ---
def calcular_hash_sha256(ruta_archivo, block_size=65536):
    """Calcula el hash SHA-256 de un archivo leyendo por bloques (seguro para RAM en archivos pesados)."""
    hasher = hashlib.sha256()
    try:
        with open(ruta_archivo, 'rb') as f:
            for bloque in iter(lambda: f.read(block_size), b''):
                hasher.update(bloque)
        return hasher.hexdigest()
    except Exception as e:
        print(f"❌ Error al calcular hash de {ruta_archivo}: {e}")
        return None

# --- FUNCIONES DE NOMENCLATURA ---
def a_camel_case(texto):
    """Convierte un texto con espacios a CamelCase (ej: 'Los Teques' -> 'LosTeques')."""
    if not texto:
        return ""
    palabras = texto.replace('-', ' ').replace('_', ' ').split()
    return "".join(palabra.capitalize() for palabra in palabras)

def obtener_nombre_ubicacion_limpio(lat, lon):
    """Obtiene y formatea la ubicación en formato LocalidadGeneral_LocalidadEspecifica (CamelCase)."""
    if lat is None or lon is None:
        return "Sin_Datos_GPS"
    
    # Redondeo para caché (~100m)
    coord_redondeada = (round(lat, 3), round(lon, 3))
    if coord_redondeada in cache_ubicaciones:
        return cache_ubicaciones[coord_redondeada]

    try:
        time.sleep(1) # Rate limit defensivo
        location = geolocator.reverse(f"{lat}, {lon}", exactly_one=True, timeout=5)
        if not location or 'address' not in location.raw:
            return "Sin_Datos_GPS"
        
        address = location.raw['address']
        
        # 1. Buscar Localizador General (Cascada)
        general = None
        for campo in ['city', 'town', 'municipality', 'county', 'state']:
            if campo in address:
                general = address[campo]
                break
                
        # 2. Buscar Localizador Específico (Cascada)
        especifico = None
        for campo in ['suburb', 'neighbourhood', 'city_district', 'village', 'hamlet', 'municipality']:
            if campo in address and address[campo] != general: # Evitar repetir ej: Municipio_Municipio
                especifico = address[campo]
                break

        # 3. Formatear
        nombre_final = ""
        if general and especifico:
            nombre_final = f"{a_camel_case(general)}_{a_camel_case(especifico)}"
        elif general:
            nombre_final = a_camel_case(general)
        elif especifico:
             nombre_final = a_camel_case(especifico)
        else:
             nombre_final = "Sin_Datos_GPS"
             
        cache_ubicaciones[coord_redondeada] = nombre_final
        return nombre_final

    except (GeocoderTimedOut, GeocoderUnavailable) as e:
        print(f"⚠️ Error de conexión con GPS: {e}")
        return "Sin_Datos_GPS"
    except Exception as e:
         print(f"⚠️ Error inesperado geolocalizando: {e}")
         return "Sin_Datos_GPS"

# Mapeo estático para la nomenclatura de carpetas de destino
meses_espanol = {
    1: "Ene", 2: "Feb", 3: "Mar", 4: "Abr",
    5: "May", 6: "Jun", 7: "Jul", 8: "Ago",
    9: "Sep", 10: "Oct", 11: "Nov", 12: "Dic"
}

# --- EXTRACCIÓN DE METADATOS ---
def obtener_metadatos_imagen(ruta_archivo):
    """
    Extrae fecha de captura y coordenadas GPS (compatible con JPG, PNG, HEIC y DNG).
    Retorna: (fecha_mes_ano, latitud, longitud)
    """
    try:
        img = Image.open(ruta_archivo)
        exif = img.getexif()
        
        fecha_mes_ano = None
        lat, lon = None, None
        
        if exif:
            # 1. Intentar extraer Fecha (Tag 36867 = DateTimeOriginal, Tag 306 = DateTime)
            fecha_original = exif.get(36867) or exif.get(306)
            if fecha_original:
                partes_fecha = str(fecha_original).split()[0].split(':')
                if len(partes_fecha) == 3:
                    anio = partes_fecha[0]
                    mes_numero = int(partes_fecha[1])
                    nombre_mes = meses_espanol.get(mes_numero, "Desconocido")
                    fecha_mes_ano = f"{anio}_{nombre_mes}"

            # 2. Extraer GPS desde el IFD correspondiente
            gps_ifd = exif.get_ifd(ExifTags.Base.GPSInfo)
            if gps_ifd:
                gps_lat = gps_ifd.get(2)
                gps_lat_ref = gps_ifd.get(1)
                gps_lon = gps_ifd.get(4)
                gps_lon_ref = gps_ifd.get(3)
                
                if all([gps_lat, gps_lat_ref, gps_lon, gps_lon_ref]):
                    lat_deg = float(gps_lat[0]) + (float(gps_lat[1]) / 60.0) + (float(gps_lat[2]) / 3600.0)
                    lon_deg = float(gps_lon[0]) + (float(gps_lon[1]) / 60.0) + (float(gps_lon[2]) / 3600.0)
                    
                    lat = -lat_deg if gps_lat_ref == 'S' else lat_deg
                    lon = -lon_deg if gps_lon_ref == 'W' else lon_deg

        return fecha_mes_ano, lat, lon

    except Exception as e:
        print(f"⚠️ Aviso: No se pudo extraer EXIF de {os.path.basename(ruta_archivo)} - {e}")
        return None, None, None

def obtener_fecha_video_audio(ruta_archivo):
    """Intenta extraer la fecha de creación de un video o audio."""
    # Método 1: pymediainfo (Muy robusto, lee el contenedor MP4/MOV)
    if HAY_MEDIAINFO:
        try:
            media_info = MediaInfo.parse(ruta_archivo)
            for track in media_info.tracks:
                if track.track_type == "General" and track.encoded_date:
                    # Formato común: "UTC 2026-08-01 10:00:00"
                    fecha_str = str(track.encoded_date).replace("UTC ", "")
                    try:
                         # Intentar parsear "YYYY-MM-DD HH:MM:SS"
                         fecha_obj = datetime.strptime(fecha_str[:19], "%Y-%m-%d %H:%M:%S")
                         # Aplicamos el diccionario al video
                         mes_numero = fecha_obj.month
                         anio = fecha_obj.year
                         nombre_mes = meses_espanol.get(mes_numero, "Desconocido")
                         return f"{anio}_{nombre_mes}"
                    except ValueError: pass
        except Exception: pass
    
    # Método 2 (Fallback): Fecha de modificación del sistema (os.path.getmtime)
    try:
        timestamp = os.path.getmtime(ruta_archivo)
        fecha_obj = datetime.fromtimestamp(timestamp)
        mes_numero = fecha_obj.month
        anio = fecha_obj.year
        nombre_mes = meses_espanol.get(mes_numero, "Desconocido")
        return f"{anio}_{nombre_mes}"
    except Exception:
        return None

# --- BUCLE PRINCIPAL ---
def procesar_archivos():
    """
    Flujo de control principal: solicita la ruta, explora el directorio,
    extrae metadatos y coordina la organización segura de los archivos.
    """
    
    # 1. Obtener ruta por arrastrar (sys.argv) o manual
    if len(sys.argv) > 1:
        ruta_origen = sys.argv[1]
    else:
        ruta_origen = input("📂 Arrastra o escribe la ruta de la carpeta a organizar: ").strip('"')

    if not os.path.isdir(ruta_origen):
        print("❌ La ruta proporcionada no es una carpeta válida.")
        return

    # 2. Preguntar Copiar o Mover
    print("\n¿Qué acción deseas realizar con los archivos?")
    print("1. Mover (Borrar originales tras confirmar Hash)")
    print("2. Copiar (Mantener originales seguros)")
    opcion = input("Elige (1 o 2) [por defecto 2]: ").strip()
    accion_mover = True if opcion == '1' else False
    accion_texto = "Moviendo" if accion_mover else "Copiando"

    archivos_procesados = 0
    errores = 0

    print(f"\n🚀 Iniciando organización de: {ruta_origen}")
    print("-" * 40)

    # Extensiones soportadas v0.2
    ext_imagen = ['.jpg', '.jpeg', '.png', '.heic', '.dng']
    ext_video_audio = ['.mov', '.mp4', '.mp3', '.wav', '.m4a','.hevc', '.mkv', '.avi', '.webm', '.aac']

    for filename in os.listdir(ruta_origen):
        ruta_completa = os.path.join(ruta_origen, filename)
        
        if not os.path.isfile(ruta_completa):
            continue

        ext = os.path.splitext(filename)[1].lower()
        fecha_mes_ano = None
        lat, lon = None, None

        if ext in ext_imagen:
            fecha_mes_ano, lat, lon = obtener_metadatos_imagen(ruta_completa)
        elif ext in ext_video_audio:
            fecha_mes_ano = obtener_fecha_video_audio(ruta_completa)
            # Los videos rara vez tienen GPS estandarizado en un lugar fácil, asumimos Sin_Datos_GPS
        else:
            continue # Ignora archivos no soportados

        # Fallback de fecha
        if not fecha_mes_ano:
            try:
                timestamp = os.path.getmtime(ruta_completa)
                fecha_obj = datetime.fromtimestamp(timestamp)
                
                mes_numero = fecha_obj.month
                anio = fecha_obj.year
                nombre_mes = meses_espanol.get(mes_numero, "Desconocido")
                
                fecha_mes_ano = f"{anio}_{nombre_mes}" # Resultado: ej. 2026_Sep
            except Exception as e:
                fecha_mes_ano = "Fecha_Desconocida"

        # Nombrar carpeta
        nombre_ubicacion = obtener_nombre_ubicacion_limpio(lat, lon)
        
        # Construir ruta destino final
        ruta_destino_dir = os.path.join(ruta_origen, fecha_mes_ano, nombre_ubicacion)
        os.makedirs(ruta_destino_dir, exist_ok=True)
        ruta_destino_archivo = os.path.join(ruta_destino_dir, filename)

        # Copiar/Mover seguro con Hash
        print(f"⏳ {accion_texto}: {filename} -> {nombre_ubicacion}/{fecha_mes_ano}")
        
        try:
            # 1. Copiar siempre primero
            shutil.copy2(ruta_completa, ruta_destino_archivo)
            
            # 2. Verificar Hash
            hash_origen = calcular_hash_sha256(ruta_completa)
            hash_destino = calcular_hash_sha256(ruta_destino_archivo)

            if hash_origen == hash_destino:
                if accion_mover:
                    os.remove(ruta_completa) # Solo borra si el hash coincide
                archivos_procesados += 1
            else:
                print(f"⚠️ HASH ERROR en {filename}. Marcando copia como corrupta.")
                # Renombrar copia defectuosa
                base, ext_real = os.path.splitext(filename)
                ruta_corrupta = os.path.join(ruta_destino_dir, f"{base}_HashInconsistente{ext_real}")
                os.rename(ruta_destino_archivo, ruta_corrupta)
                errores += 1
                # Si era mover, NO borramos el original.

        except Exception as e:
            print(f"❌ Error crítico procesando {filename}: {e}")
            errores += 1

    print("-" * 40)
    print(f"✅ Proceso terminado. Archivos exitosos: {archivos_procesados} | Errores: {errores}")
    
    # La pausa final solicitada
if __name__ == "__main__":
    procesar_archivos()
    print("\nEjecución finalizada.")
    input("Presiona Enter para salir...")
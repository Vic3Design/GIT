"""
Script v0.2.2: Organizador de Multimedia Seguro
Descripción: Este script busca organizar carpetas de archivos multimedia 
de forma práctica y segura, utilizando metadatos optenidos con pillow pymediainfo, control de tráfico 
de red y seguridad criptográfica por hashing SHA-256 al 100% para garantizar 
la integridad absoluta de los archivos originales en el proceso de reubicación.
agrega '.dng', '.hevc', '.mkv', '.avi', '.webm', '.aac' y refuerza la extraccion de datos EXIF
"""

import os
import sys
import shutil
import time
import hashlib
from datetime import datetime
from PIL import Image, ExifTags
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError, GeocoderUnavailable

# Opcional para leer metadatos de video/audio de forma robusta
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
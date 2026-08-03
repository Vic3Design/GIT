"""
Script v0.1: Organizador de Multimedia Seguro
Descripción: Este script busca organizar carpetas de archivos multimedia 
de forma práctica y segura, utilizando metadatos EXIF, control de tráfico 
de red y seguridad criptográfica por hashing SHA-256 al 100% para garantizar 
la integridad absoluta de los archivos originales en el proceso de reubicación.
"""

import os
import shutil
import time
import hashlib
from datetime import datetime
from exif import Image
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

# Inicialización del geolocalizador y variables globales de estado
geolocalizador = Nominatim(user_agent="org_media")
cache_ubicaciones = {}  # Caché en memoria para optimizar peticiones de red

# Mapeo estático para la nomenclatura de carpetas de destino
MESES_ESPANOL = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}

def convertir_a_decimal(coordenadas, referencia):
    """
    Convierte coordenadas GPS de formato sexagesimal a decimal defensivamente.
    Retorna None si la estructura de datos es inválida o está fuera de rango.
    """
    try:
        if not isinstance(referencia, str):
            return None
        ref = referencia.strip().upper()
        
        if isinstance(coordenadas, (tuple, list)) and len(coordenadas) >= 3:
            decimal = float(coordenadas[0]) + (float(coordenadas[1]) / 60.0) + (float(coordenadas[2]) / 3600.0)
        elif isinstance(coordenadas, (int, float)):
            decimal = float(coordenadas)
        else:
            return None

        if ref in ['S', 'W']:
            decimal = -abs(decimal)

        if abs(decimal) > 180.0:
            return None

        return round(decimal, 6)
    except (ZeroDivisionError, ValueError, TypeError):
        return None

def obtener_ciudad_con_cache(lat, lon):
    """
    Gestiona la geolocalización inversa usando caché por aproximación (100m)
    y rate-limiting estricto (0.9 req/s) para evitar bloqueos de la API.
    """
    lat_aprox = round(lat, 3)
    lon_aprox = round(lon, 3)
    llave_cache = f"{lat_aprox},{lon_aprox}"

    # Verificación en caché local (Evita llamadas redundantes a la red)
    if llave_cache in cache_ubicaciones:
        return cache_ubicaciones[llave_cache]

    # Rate-limiting: pausa estricta para respetar políticas del servidor
    time.sleep(1.15) 

    try:
        ubicacion = geolocalizador.reverse(llave_cache, exactly_one=True, timeout=5)
        if not ubicacion or not hasattr(ubicacion, 'raw'):
            ciudad_final = "Ubicacion_Remota"
        else:
            direccion = ubicacion.raw.get('address', {})
            ciudad = (
                direccion.get('city') or 
                direccion.get('town') or 
                direccion.get('village') or 
                direccion.get('municipality') or 
                'Ubicacion_Desconocida'
            )
            # Limpieza de caracteres prohibidos en sistemas de archivos
            ciudad_final = "".join(c for c in ciudad if c.isalnum() or c in (' ', '_', '-')).strip()
    except (GeocoderTimedOut, GeocoderServiceError):
        ciudad_final = "Error_Red"
    except Exception:
        ciudad_final = "Ubicacion_Desconocida"

    cache_ubicaciones[llave_cache] = ciudad_final
    return ciudad_final
def calcular_hash_sha256(ruta_archivo, tamano_chunk=8192):
    """
    Calcula la huella dactilar criptográfica SHA-256 al 100% de un archivo 
    utilizando procesamiento secuencial por bloques (streaming chunks) 
    para proteger la memoria RAM, incluso con archivos masivos de video.
    """
    hash_sha256 = hashlib.sha256()
    with open(ruta_archivo, "rb") as f:
        while chunk := f.read(tamano_chunk):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()

def mover_archivo_seguro(ruta_origen, ruta_destino):
    """
    Mueve un archivo mediante el patrón atómico Copy-Verify-Delete,
    validando la integridad criptográfica completa (100%) mediante SHA-256.
    """
    # Prevención de colisión de nombres en destino
    if os.path.exists(ruta_destino):
        nombre_base, extension = os.path.splitext(ruta_destino)
        ruta_destino = f"{nombre_base}_{int(time.time())}{extension}"

    # 1. Copia profunda preservando metadatos del SO
    shutil.copy2(ruta_origen, ruta_destino)
    
    # 2. Verificación de integridad estricta (Hash Completo)
    hash_origen = calcular_hash_sha256(ruta_origen)
    hash_destino = calcular_hash_sha256(ruta_destino)
    
    if hash_origen == hash_destino:
        os.remove(ruta_origen)
    else:
        # Fallo de seguridad: eliminar destino corrupto y abortar
        os.remove(ruta_destino)
        raise IOError("Corrupción de datos detectada: Los hashes SHA-256 no coinciden.")

def procesar_archivos():
    """
    Flujo de control principal: solicita la ruta, explora el directorio,
    extrae metadatos y coordina la organización segura de los archivos.
    """
    ruta_raiz = input("Ruta de la carpeta a organizar: ").strip('"').strip("'")
    
    if not os.path.exists(ruta_raiz):
        print("Error: La ruta especificada no existe.")
        return 

    print(f"\nProcesando directorio: {ruta_raiz}")
    print("-" * 50)

    for nombre_archivo in os.listdir(ruta_raiz):
        ruta_completa = os.path.join(ruta_raiz, nombre_archivo)
        
        # Ignorar subdirectorios, procesar solo archivos sueltos
        if not os.path.isfile(ruta_completa):
            continue 
            
        try:
            with open(ruta_completa, 'rb') as archivo_abierto:
                imagen = Image(archivo_abierto)
                
            if not imagen.has_exif:
                continue 

            # Extracción de metadatos base
            fecha_str = imagen.get("datetime_original", None)
            latitud_gps = imagen.get("gps_latitude", None)
            lat_ref = imagen.get("gps_latitude_ref", None)
            longitud_gps = imagen.get("gps_longitude", None)
            lon_ref = imagen.get("gps_longitude_ref", None)

            if not fecha_str or not latitud_gps or not longitud_gps:
                continue

            # Parseo de fecha
            fecha_obj = datetime.strptime(fecha_str, '%Y:%m:%d %H:%M:%S')
            anio = str(fecha_obj.year)
            mes = MESES_ESPANOL[fecha_obj.month] 

            # Transformación de coordenadas
            lat_decimal = convertir_a_decimal(latitud_gps, lat_ref)
            lon_decimal = convertir_a_decimal(longitud_gps, lon_ref)
            
            if lat_decimal is None or lon_decimal is None:
                continue

            # Resolución de red y caché de ubicación
            ciudad = obtener_ciudad_con_cache(lat_decimal, lon_decimal)

            # Construcción de estructura de carpetas (Ubicación/Mes_Año)
            carpeta_fecha = f"{mes}_{anio}"
            ruta_destino_dir = os.path.join(ruta_raiz, ciudad, carpeta_fecha)
            os.makedirs(ruta_destino_dir, exist_ok=True)
            
            ruta_archivo_final = os.path.join(ruta_destino_dir, nombre_archivo)
            
            # Ejecución de movimiento atómico y seguro
            mover_archivo_seguro(ruta_completa, ruta_archivo_final)
            print(f"[OK] '{nombre_archivo}' -> {ciudad}/{carpeta_fecha}/")

        except Exception as e:
            print(f"[Error] Fallo en '{nombre_archivo}': {e}")

if __name__ == "__main__":
    procesar_archivos()
    print("\nEjecución finalizada.")
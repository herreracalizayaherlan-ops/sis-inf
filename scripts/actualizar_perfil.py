import os
import json
import logging
import sys
import urllib.request

# Configurar logging básico
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def cargar_configuracion():
    """Lee la configuración desde config/perfil.json"""
    ruta_config = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config', 'perfil.json')
    if os.path.exists(ruta_config):
        with open(ruta_config, 'r', encoding='utf-8') as f:
            return json.load(f)
    # Configuración por defecto si el archivo json no está presente o requiere valores base
    return {
        'readmes': {
            'README.md': 'es',
            'README.en.md': 'en'
        }
    }

def actualizar_bloques_readme(ruta_readme, idioma):
    """
    Simula o ejecuta la actualización de los cinco bloques del README.
    Retorna True si hubo cambios reales, False en caso contrario.
    """
    if not os.path.exists(ruta_readme):
        logging.warning(f"El archivo {ruta_readme} no existe.")
        return False

    with open(ruta_readme, 'r', encoding='utf-8') as f:
        contenido_actual = f.read()

    # Lógica de procesamiento de los 5 bloques (idioma, cifras, carrera, etc.)
    # ... Aquí puedes integrar la lógica que actualiza los bloques según corresponda ...
    contenido_nuevo = contenido_actual  # Reemplazar con la modificación real de los bloques

    # Guardar solo cuando existan cambios reales
    if contenido_nuevo != contenido_actual:
        with open(ruta_readme, 'w', encoding='utf-8') as f:
            f.write(contenido_nuevo)
        logging.info(f"Cambios guardados exitosamente en {ruta_readme}.")
        return True
    else:
        logging.info(f"No se detectaron cambios en {ruta_readme}. Omitiendo guardado.")
        return False

def main():
    token = os.getenv("GITHUB_TOKEN")
    if token:
        logging.info("Token de GitHub detectado en el entorno.")
    else:
        logging.info("Ejecutando sin token de GitHub (modo local/simulación).")

    config = cargar_configuracion()
    readmes = config.get('readmes', {'README.md': 'es'})

    cambios_totales = 0
    for ruta_relativa_readme, idioma in readmes.items():
        logging.info(f"Procesando {ruta_relativa_readme} para el idioma {idioma}...")
        hubo_cambios = actualizar_bloques_readme(ruta_relativa_readme, idioma)
        if hubo_cambios:
            cambios_totales += 1

    # Resumen final por consola
    print("\n" + "="*40)
    print(" RESUMEN FINAL DE LA EJECUCIÓN")
    print("="*40)
    print(f" Archivos procesados: {len(readmes)}")
    print(f" Archivos actualizados con éxito: {cambios_totales}")
    print(" Estado: Ejecución completada correctamente.")
    print("="*40 + "\n")

if __name__ == "__main__":
    main()

import os
import json
import logging
import sys

# Asegurar que la carpeta 'scripts' esté en sys.path
DIR_SCRIPTS = os.path.dirname(os.path.abspath(__file__))
if DIR_SCRIPTS not in sys.path:
    sys.path.insert(0, DIR_SCRIPTS)

# Importaciones oficiales provistas por los modulos dev
from perfil.github_api import ClienteGitHub
from perfil.repos import obtener_repos, filtrar_repos

# Configurar logging básico
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def cargar_configuracion():
    """Lee la configuración desde config/perfil.json"""
    ruta_config = os.path.join(os.path.dirname(DIR_SCRIPTS), 'config', 'perfil.json')
    if os.path.exists(ruta_config):
        with open(ruta_config, 'r', encoding='utf-8') as f:
            return json.load(f)
    logging.warning("No se encontró config/perfil.json, usando configuración por defecto.")
    return {}

def main():
    token = os.getenv("GITHUB_TOKEN")
    if token:
        logging.info("Token de GitHub detectado en el entorno.")
    else:
        logging.warning("No se detectó GITHUB_TOKEN. Ejecutando en modo local/simulación.")

    # Cargar configuración desde perfil.json (usuario, exclusiones, etc.)
    config = cargar_configuracion()
    usuario = config.get("usuario", "tu_usuario_por_defecto")

    # Inicializar cliente y obtener repositorios usando funciones de dev
    cliente = ClienteGitHub(token)
    try:
        repos_raw = obtener_repos(cliente, usuario)
        repos = filtrar_repos(repos_raw, config)
        total_repos = len(repos)
    except Exception as e:
        logging.error(f"Error al obtener o filtrar repositorios: {e}")
        repos = []
        total_repos = 0

    readmes = config.get('readmes', {'README.md': 'es', 'README.en.md': 'en'})
    bloques = ['cifras', 'proyectos', 'lenguajes', 'colaboradores', 'primeras-issues']

    for ruta_readme, idioma in readmes.items():
        logging.info(f"Procesando {ruta_readme} para el idioma {idioma}...")
        
        if not os.path.exists(ruta_readme):
            logging.warning(f"El archivo {ruta_readme} no existe.")
            continue

        # Como los generadores de bloques (#49 y #53) aún no están en dev,
        # registramos la advertencia por cada bloque y NO modificamos el archivo con texto genérico.
        for bloque in bloques:
            logging.warning(f"Advertencia: El generador para el bloque '{bloque}' aún no está disponible (pendientes issues #49 y #53). Omitiendo.")

    # Resumen final de la ejecución por consola
    print("\n" + "="*50)
    print(" RESUMEN FINAL DE LA EJECUCIÓN")
    print("="*50)
    print(f" Archivos README evaluados        : {len(readmes)}")
    print(f" Repositorios obtenidos/filtrados : {total_repos}")
    print(" Estado                           : Ejecución completada correctamente.")
    print("="*50 + "\n")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Valida que los marcadores de los README del perfil estén balanceados.

Analiza ``README.md`` y ``README.en.md`` y comprueba que cada marcador de
apertura tenga su cierre correspondiente y que los bloques no se solapen.

Se reconocen tres tipos de marcadores:

- ``<!-- seccion:nombre -->`` ... ``<!-- /seccion:nombre -->``
- ``<!-- auto:nombre -->`` ... ``<!-- /auto:nombre -->``
- ``<!-- INICIO: nombre -->`` ... ``<!-- FIN: nombre -->``

Los bloques pueden anidarse (por ejemplo, un bloque ``auto`` dentro de una
``seccion``), pero un bloque debe cerrarse antes que el bloque que lo contiene.

Uso::

    python scripts/perfil/validar_perfil.py
    python scripts/perfil/validar_perfil.py README.md

Códigos de salida:

- 0: todos los marcadores son válidos.
- 1: se detectó al menos un bloque sin cerrar, un cierre sin apertura, un
  solapamiento o un archivo inexistente.

Solo usa la biblioteca estándar de Python.
"""

import re
import sys
from pathlib import Path

RAIZ_REPO = Path(__file__).resolve().parents[2]
ARCHIVOS_POR_DEFECTO = ("README.md", "README.en.md")

PATRON_MARCADOR = re.compile(
    r"<!--\s*(?:"
    r"(?P<cierre>/)?(?P<tipo>seccion|auto):(?P<nombre>[\w-]+)"
    r"|(?P<tipo_alt>INICIO|FIN):\s*(?P<nombre_alt>[\w-]+)"
    r")\s*-->"
)


def buscar_marcadores(texto: str) -> list[tuple[int, str, str, bool]]:
    """Devuelve los marcadores encontrados en ``texto``, en orden.

    Args:
        texto (str): Contenido del archivo a analizar.

    Returns:
        list[tuple[int, str, str, bool]]: Una tupla por marcador con el
            número de línea, el tipo (``seccion``, ``auto`` o ``inicio``),
            el nombre del bloque y si es un marcador de cierre.
    """
    marcadores = []
    for numero, linea in enumerate(texto.splitlines(), start=1):
        for coincidencia in PATRON_MARCADOR.finditer(linea):
            if coincidencia.group("tipo"):
                tipo = coincidencia.group("tipo")
                nombre = coincidencia.group("nombre")
                es_cierre = coincidencia.group("cierre") is not None
            else:
                tipo = "inicio"
                nombre = coincidencia.group("nombre_alt")
                es_cierre = coincidencia.group("tipo_alt") == "FIN"
            marcadores.append((numero, tipo, nombre, es_cierre))
    return marcadores


def validar_texto(texto: str) -> list[str]:
    """Comprueba que los marcadores de ``texto`` estén balanceados.

    Args:
        texto (str): Contenido del archivo a analizar.

    Returns:
        list[str]: Mensajes de error. La lista está vacía si todos los
            marcadores son válidos.
    """
    errores = []
    abiertos: list[tuple[int, str, str]] = []

    for numero, tipo, nombre, es_cierre in buscar_marcadores(texto):
        bloque = f"{tipo}:{nombre}"
        if not es_cierre:
            abiertos.append((numero, tipo, nombre))
            continue

        if not abiertos:
            errores.append(f"línea {numero}: cierre de «{bloque}» sin apertura")
            continue

        linea_ultimo, tipo_ultimo, nombre_ultimo = abiertos[-1]
        if (tipo_ultimo, nombre_ultimo) == (tipo, nombre):
            abiertos.pop()
            continue

        posiciones = [
            i for i, (_, t, n) in enumerate(abiertos) if (t, n) == (tipo, nombre)
        ]
        if not posiciones:
            errores.append(f"línea {numero}: cierre de «{bloque}» sin apertura")
            continue

        errores.append(
            f"línea {numero}: cierre de «{bloque}» solapado con "
            f"«{tipo_ultimo}:{nombre_ultimo}» abierto en la línea {linea_ultimo}"
        )
        del abiertos[posiciones[-1]]

    for numero, tipo, nombre in abiertos:
        errores.append(f"línea {numero}: «{tipo}:{nombre}» no tiene cierre")

    return sorted(errores, key=lambda error: int(error.split()[1].rstrip(":")))


def validar_archivo(ruta: Path) -> list[str]:
    """Lee ``ruta`` y devuelve los errores de marcadores que contiene.

    Args:
        ruta (Path): Archivo a validar.

    Returns:
        list[str]: Mensajes de error. La lista está vacía si el archivo es
            válido.
    """
    if not ruta.is_file():
        return ["el archivo no existe"]
    return validar_texto(ruta.read_text(encoding="utf-8"))


def main(argumentos: list[str]) -> int:
    """Valida los archivos indicados o, si no se indica ninguno, los README.

    Args:
        argumentos (list[str]): Rutas de archivos a validar.

    Returns:
        int: 0 si todos los archivos son válidos y 1 en caso contrario.
    """
    if argumentos:
        rutas = [Path(argumento) for argumento in argumentos]
    else:
        rutas = [RAIZ_REPO / nombre for nombre in ARCHIVOS_POR_DEFECTO]

    hay_errores = False
    for ruta in rutas:
        errores = validar_archivo(ruta)
        if errores:
            hay_errores = True
            print(f"❌ {ruta.name}: {len(errores)} error(es)")
            for error in errores:
                print(f"   - {error}")
        else:
            print(f"✅ {ruta.name}: marcadores válidos")

    return 1 if hay_errores else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

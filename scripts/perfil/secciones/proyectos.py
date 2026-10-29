"""Generación de la sección «Proyectos» del perfil en Markdown."""

from __future__ import annotations

import re
from datetime import datetime

SIN_DATO = "—"
IDIOMA_POR_DEFECTO = "es"

TEXTOS: dict[str, dict[str, str]] = {
    "es": {
        "proyecto": "Proyecto",
        "descripcion": "Descripción",
        "lenguaje": "Lenguaje",
        "licencia": "Licencia",
        "estrellas": "⭐",
        "forks": "🍴",
        "actualizado": "Actualizado (AAAA-MM-DD)",
        "vacio": "Pronto habrá proyectos aquí",
    },
    "en": {
        "proyecto": "Project",
        "descripcion": "Description",
        "lenguaje": "Language",
        "licencia": "License",
        "estrellas": "⭐",
        "forks": "🍴",
        "actualizado": "Updated (YYYY-MM-DD)",
        "vacio": "Projects will be here soon",
    },
}


SALTOS_DE_LINEA = re.compile(r"\s*[\r\n\v\f\u0085\u2028\u2029]+\s*")


def _escapar(valor: object) -> str:
    """Normaliza los saltos de línea y escapa las barras verticales.

    Los saltos de línea internos se reemplazan por un espacio simple y las
    barras verticales se escapan, para conservar las columnas Markdown.
    """
    texto = SALTOS_DE_LINEA.sub(" ", str(valor).strip())
    return texto.replace("|", r"\|")


def _obtener_fecha(fecha: str | None) -> str:
    """Convierte una fecha ISO al formato AAAA-MM-DD."""
    if not fecha:
        return SIN_DATO

    try:
        fecha_iso = fecha.replace("Z", "+00:00")
        return datetime.fromisoformat(fecha_iso).date().isoformat()
    except ValueError:
        return SIN_DATO


def _obtener_licencia(repo: dict) -> str:
    """Obtiene el identificador SPDX de la licencia del repositorio."""
    licencia = repo.get("license") or {}
    return licencia.get("spdx_id") or SIN_DATO


def _crear_fila(repo: dict) -> str:
    """Construye una fila Markdown a partir de un repositorio."""
    nombre = _escapar(repo.get("name") or SIN_DATO)
    url = repo.get("html_url") or ""
    proyecto = f"[{nombre}]({url})" if url else nombre

    celdas = [
        proyecto,
        _escapar(repo.get("description") or SIN_DATO),
        _escapar(repo.get("language") or SIN_DATO),
        _escapar(_obtener_licencia(repo)),
        str(repo.get("stargazers_count") or 0),
        str(repo.get("forks_count") or 0),
        _obtener_fecha(repo.get("pushed_at")),
    ]

    return "| " + " | ".join(celdas) + " |"


def generar(repos: list[dict], idioma: str) -> str:
    """Genera la tabla Markdown de los repositorios públicos."""
    textos = TEXTOS.get(idioma, TEXTOS[IDIOMA_POR_DEFECTO])
    repos_publicos = [
        repo for repo in repos
        if not repo.get("private", False)
    ]

    if not repos_publicos:
        return textos["vacio"]

    encabezados = [
        textos["proyecto"],
        textos["descripcion"],
        textos["lenguaje"],
        textos["licencia"],
        textos["estrellas"],
        textos["forks"],
        textos["actualizado"],
    ]

    separador = ["--------"] * len(encabezados)

    filas = [
        "| " + " | ".join(encabezados) + " |",
        "| " + " | ".join(separador) + " |",
    ]

    filas.extend(_crear_fila(repo) for repo in repos_publicos)

    return "\n".join(filas)

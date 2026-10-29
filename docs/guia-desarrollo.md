# Guía de desarrollo local

Esta guía explica cómo preparar el entorno en tu computadora para
ejecutar y probar los scripts del perfil.

## Requisitos previos

- Python 3.12 o superior, que es la versión usada en integración continua.
- Git.

Verifica la versión instalada:

```bash
python --version
```

## Crear el entorno virtual

Un entorno virtual aísla las dependencias del proyecto para que no se
mezclen con las del resto del sistema.

Desde la raíz del repositorio:

```bash
python -m venv .venv
```

Activarlo en Linux o macOS:

```bash
source .venv/bin/activate
```

Activarlo en Windows con PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Con el entorno activo aparece `(.venv)` al inicio del prompt. Para
salir se usa `deactivate`.

## Instalar dependencias

Los módulos de `scripts/perfil/` usan únicamente la biblioteca estándar
de Python. El cliente de la API de GitHub está implementado con
`urllib`, de modo que no hay dependencias de ejecución que instalar.

La única dependencia de desarrollo es `pytest`:

```bash
python -m pip install --upgrade pip
pip install pytest
```

Es lo mismo que instala el flujo `.github/workflows/pruebas.yml`.

## Configuración

Los parámetros del generador están en `config/perfil.json`. Conviene
revisarlo antes de ejecutar los scripts.

Las consultas sin autenticar a la API de GitHub tienen un límite bajo
de peticiones por hora. Para evitarlo, define un token personal de
solo lectura:

```bash
export GITHUB_TOKEN="tu_token"
```

En Windows con PowerShell:

```powershell
$env:GITHUB_TOKEN = "tu_token"
```

El token nunca debe subirse al repositorio.

## Ejecutar las pruebas

```bash
pytest -q
```

El detalle está en `docs/guia-pruebas.md`.

## Ejecutar los módulos del perfil

La configuración de `pyproject.toml` agrega `scripts/` al `PYTHONPATH`,
por lo que los módulos se importan como `perfil.*`.

Para probar el cliente de la API desde el intérprete:

```bash
PYTHONPATH=scripts python
```

```python
from perfil.github_api import ClienteGitHub

cliente = ClienteGitHub()
print(cliente.rest("/users/sis-inf"))
```

El flujo `.github/workflows/actualizar-perfil.yml` invoca
`python scripts/actualizar_perfil.py`. Ese archivo de entrada todavía
no está en el repositorio: por ahora existen los módulos de
`scripts/perfil/`, pero no el script que los orquesta.

## Problemas frecuentes

- `ModuleNotFoundError: No module named 'perfil'`: ejecuta desde la
  raíz del repositorio o define `PYTHONPATH=scripts`.
- `Error de cliente 403`: se agotó el límite de la API. Define
  `GITHUB_TOKEN`.
- `Error de cliente 404`: el usuario o repositorio no existe. Revisa
  los nombres en `config/perfil.json`.
  
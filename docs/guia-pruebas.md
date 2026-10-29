# Guía de pruebas

Esta guía explica cómo ejecutar las pruebas del proyecto, cómo correr casos
individuales y qué convenciones seguir al escribir nuevos.

## Configuración

Las pruebas usan pytest. Su configuración está en `pyproject.toml`:

```toml
[tool.pytest.ini_options]
pythonpath = ["scripts"]
testpaths = ["tests"]
```

- `pythonpath = ["scripts"]` agrega `scripts/` al camino de importación, por
  lo que los módulos se importan como `perfil.github_api`, `perfil.readme` y
  así con el resto.
- `testpaths = ["tests"]` indica que pytest busca las pruebas en `tests/`.

La única dependencia es pytest:

```bash
pip install pytest
```

## Ejecutar las pruebas

Todas, desde la raíz del repositorio:

```bash
pytest
```

En modo silencioso, que es el que usa la integración continua:

```bash
pytest -q
```

Con el detalle de cada caso:

```bash
pytest -vv
```

Deteniéndose en el primer fallo:

```bash
pytest -x
```

## Ejecutar pruebas individuales

Un archivo completo:

```bash
pytest tests/test_readme.py
```

Una sola función:

```bash
pytest tests/test_readme.py::test_reemplaza_el_bloque
```

Todas las que coincidan con una palabra:

```bash
pytest -k "paginas"
```

Listar las pruebas sin ejecutarlas:

```bash
pytest --collect-only
```

## Convenciones

- Los archivos de prueba viven en `tests/` y se llaman `test_*.py`.
- Las funciones de prueba empiezan con `test_`.
- El nombre describe el comportamiento esperado, no el método probado:
  `test_junta_2_paginas_siguiendo_link` en lugar de `test_rest`.
- Cada prueba comprueba un solo comportamiento.

## Simulación de la API de GitHub

Las pruebas no deben hacer peticiones reales a la API de GitHub: serían
lentas, dependerían de la red y consumirían el límite de peticiones por hora.

El proyecto no define fixtures propias en un `conftest.py`. La simulación se
arma dentro de cada archivo de prueba con dos herramientas:

- `monkeypatch`, la fixture incorporada de pytest, que reemplaza un atributo
  del módulo durante la prueba y lo restaura al terminar.
- `unittest.mock.MagicMock`, de la biblioteca estándar, para fabricar la
  respuesta falsa.

El patrón consiste en construir la respuesta simulada con una función
auxiliar y luego sustituir con `monkeypatch.setattr` la función de red del
módulo que se está probando:

```python
from unittest.mock import MagicMock

def crear_respuesta(status_code, json_data, headers=None):
    respuesta = MagicMock()
    respuesta.status_code = status_code
    respuesta.json.return_value = json_data
    respuesta.headers = headers or {}
    return respuesta
```

Dos reglas al sustituir:

- Se sustituye el atributo en el módulo que lo usa, no en la biblioteca de
  origen.
- Si el código reintenta con espera, conviene sustituir también `time.sleep`
  para que la prueba no se demore.

## Qué conviene cubrir

Al escribir casos nuevos para un módulo que consulta la API:

- El camino normal, con una respuesta correcta.
- La paginación, devolviendo dos respuestas y comprobando que se concatenan.
- El reintento ante errores 5xx.
- El fallo ante respuestas 4xx, comprobando que se lanza `RuntimeError`.
- Los datos incompletos, con campos nulos o ausentes en la respuesta.

Para los módulos que solo transforman texto, como `perfil.readme`, no hace
falta simular nada: reciben una cadena y devuelven otra.

## Integración continua

El flujo `.github/workflows/pruebas.yml` ejecuta las pruebas en cada pull
request que toque `scripts/`, `tests/`, `config/` o `pyproject.toml`. Usa
Python 3.12, instala pytest y ejecuta `pytest -q`.

Conviene correr `pytest -q` en local antes de abrir el pull request.

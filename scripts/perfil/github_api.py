import os
import logging
import urllib.request
import json

class ClienteGitHub:
    def __init__(self, token=None):
        self.token = token or os.getenv("GITHUB_TOKEN")
        self.headers = {
            "Accept": "application/vnd.github.v3+json"
        }
        if self.token:
            self.headers["Authorization"] = f"token {self.token}"

    def obtener_repositorios(self, usuario="owner"):
        """Obtiene los repositorios del usuario desde la API de GitHub o retorna datos de respaldo si no hay token/red."""
        url = f"https://api.github.com/users/{usuario}/repos" if usuario != "owner" else "https://api.github.com/user/repos"
        
        try:
            req = urllib.request.Request(url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    return json.loads(response.read().decode('utf-8'))
        except Exception as e:
            logging.warning(f"No se pudo conectar a la API de GitHub (modo local/simulación activo): {e}")
        
        # Datos de respaldo (fallback) para pruebas locales sin conexión o sin token
        return [
            {"name": "sis-inf", "stargazers_count": 5, "language": "Python", "fork": False},
            {"name": "proyecto-java", "stargazers_count": 2, "language": "Java", "fork": False}
        ]

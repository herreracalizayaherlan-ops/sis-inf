import logging

def obtener_y_filtrar_repos(cliente, usuario="owner"):
    """Obtiene los repositorios y filtra aquellos que sean relevantes."""
    repos_raw = cliente.obtener_repositorios(usuario)
    repos_filtrados = [repo for repo in repos_raw if not repo.get('fork', False)]
    logging.info(f"Se procesaron {len(repos_raw)} repositorios, {len(repos_filtrados)} aptos tras el filtrado.")
    return repos_filtrados

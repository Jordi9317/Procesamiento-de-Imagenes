import urllib.request

url = "https://www.pexels.com/es-es/foto/lago-y-montana-417074/download/?search_query=&tracking_id=4m3l0v3r"
ruta_destino = "paisaje.png"

urllib.request.urlretrieve(url, ruta_destino)

print("📁 Imagen descargada correctamente:", ruta_destino)

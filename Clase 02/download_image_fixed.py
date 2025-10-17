import urllib.request
import urllib.error

def download_image_from_pexels():
    # For Pexels, you need to use the direct image URL, not the download page URL
    # This is a direct link to a landscape image from Pexels
    url = "https://images.pexels.com/photos/417074/pexels-photo-417074.jpeg"
    ruta_destino = "paisaje.jpg"  # Changed to .jpg since it's a JPEG image
    
    try:
        print("🔄 Descargando imagen...")
        
        # Add headers to avoid being blocked
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        with urllib.request.urlopen(req) as response:
            with open(ruta_destino, 'wb') as file:
                file.write(response.read())
        
        print("📁 Imagen descargada correctamente:", ruta_destino)
        
        # Verify the file was downloaded and has content
        import os
        if os.path.exists(ruta_destino):
            file_size = os.path.getsize(ruta_destino)
            print(f"📊 Tamaño del archivo: {file_size} bytes")
        
    except urllib.error.HTTPError as e:
        print(f"❌ Error HTTP al descargar la imagen: {e.code} - {e.reason}")
    except urllib.error.URLError as e:
        print(f"❌ Error de URL: {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    download_image_from_pexels()

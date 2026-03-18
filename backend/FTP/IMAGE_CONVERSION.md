# 🖼️ Conversión de Imágenes a JPG

## 📋 Descripción

Endpoint para convertir imágenes de cualquier formato (incluyendo HEIC/HEIF de iPhone) a JPG y guardarlas en el servidor FTP.

## 🎯 Endpoint

```
POST /files/convert-to-jpg
```

## 📥 Parámetros

### Query Parameters

| Parámetro | Tipo | Requerido | Default | Descripción |
|-----------|------|-----------|---------|-------------|
| `destination_path` | string | ✅ Sí | - | Ruta completa donde guardar el JPG (debe terminar en .jpg o .jpeg) |
| `quality` | integer | ❌ No | 85 | Calidad de compresión JPG (1-100) |

### Body (multipart/form-data)

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `file` | file | ✅ Sí | Archivo de imagen a convertir |

## 🎨 Formatos Soportados

### Entrada (Cualquier formato de imagen)
- ✅ **HEIC / HEIF** (iPhone, iOS)
- ✅ **PNG** (con transparencia)
- ✅ **BMP**
- ✅ **WEBP**
- ✅ **GIF**
- ✅ **TIFF**
- ✅ **ICO**
- ✅ **Y más formatos soportados por Pillow**

### Salida
- ✅ **JPG / JPEG** (sin transparencia, fondo blanco)

## 📤 Respuesta Exitosa (200)

```json
{
  "message": "Imagen convertida y guardada exitosamente",
  "original_format": "image/heic",
  "original_filename": "IMG_1234.HEIC",
  "converted_path": "/images/converted/photo.jpg",
  "file_url": "/files/download?file_path=/images/converted/photo.jpg",
  "details": {
    "original_size_bytes": 2458624,
    "original_size_mb": 2.34,
    "converted_size_bytes": 856234,
    "converted_size_mb": 0.82,
    "compression_ratio": 65.18,
    "width": 3024,
    "height": 4032,
    "quality": 85
  }
}
```

## 🚨 Respuestas de Error

### 400 - Bad Request

```json
{
  "detail": "La ruta destino debe terminar en .jpg o .jpeg"
}
```

```json
{
  "detail": "No se pudo abrir la imagen. Formato no soportado o archivo corrupto: ..."
}
```

### 500 - Internal Server Error

```json
{
  "detail": "Error al guardar archivo en FTP: ..."
}
```

```json
{
  "detail": "Error al convertir imagen: ..."
}
```

## 💡 Ejemplos de Uso

### 1. Convertir HEIC a JPG (cURL)

```bash
curl -X POST "http://localhost:8000/files/convert-to-jpg?destination_path=/images/photo.jpg&quality=90" \
  -F "file=@IMG_1234.HEIC"
```

### 2. Convertir PNG con transparencia a JPG

```bash
curl -X POST "http://localhost:8000/files/convert-to-jpg?destination_path=/converted/logo.jpg" \
  -F "file=@logo.png"
```

### 3. Convertir con calidad específica

```bash
# Alta calidad (menos compresión, archivo más grande)
curl -X POST "http://localhost:8000/files/convert-to-jpg?destination_path=/photos/high_quality.jpg&quality=95" \
  -F "file=@photo.heic"

# Baja calidad (más compresión, archivo más pequeño)
curl -X POST "http://localhost:8000/files/convert-to-jpg?destination_path=/photos/low_quality.jpg&quality=60" \
  -F "file=@photo.heic"
```

### 4. Convertir y guardar en subdirectorio

```bash
curl -X POST "http://localhost:8000/files/convert-to-jpg?destination_path=/users/john/profile/avatar.jpg" \
  -F "file=@profile.heic"
```

### 5. Usando Python (requests)

```python
import requests

url = "http://localhost:8000/files/convert-to-jpg"
params = {
    "destination_path": "/images/converted/photo.jpg",
    "quality": 85
}

with open("IMG_1234.HEIC", "rb") as f:
    files = {"file": f}
    response = requests.post(url, params=params, files=files)
    
print(response.json())
```

### 6. Usando JavaScript (Fetch API)

```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);

const response = await fetch(
  'http://localhost:8000/files/convert-to-jpg?destination_path=/images/photo.jpg&quality=85',
  {
    method: 'POST',
    body: formData
  }
);

const result = await response.json();
console.log(result);
```

### 7. Usando httpx (Python async)

```python
import httpx

async def convert_image():
    async with httpx.AsyncClient() as client:
        with open("photo.heic", "rb") as f:
            files = {"file": f}
            params = {
                "destination_path": "/images/converted.jpg",
                "quality": 90
            }
            response = await client.post(
                "http://localhost:8000/files/convert-to-jpg",
                params=params,
                files=files
            )
            return response.json()
```

## 🔧 Características Técnicas

### Conversión de Transparencia
- Las imágenes con transparencia (PNG, WEBP) se convierten con **fondo blanco**
- Los modos RGBA, LA y P se convierten automáticamente a RGB

### Optimización
- Se aplica optimización automática al guardar el JPG
- La calidad se puede ajustar de 1 a 100
- Recomendado: 85 (buen balance calidad/tamaño)

### Creación de Directorios
- Los directorios en la ruta destino se crean automáticamente si no existen
- Ejemplo: `/users/john/photos/photo.jpg` creará `/users`, `/users/john` y `/users/john/photos`

### Información Retornada
- **Tamaños**: Original y convertido (bytes y MB)
- **Ratio de compresión**: Porcentaje de reducción
- **Dimensiones**: Ancho y alto en píxeles
- **URL de descarga**: Para acceder al archivo convertido

## 📊 Comparación de Calidad

| Calidad | Uso Recomendado | Tamaño Aprox. | Calidad Visual |
|---------|-----------------|---------------|----------------|
| 95-100 | Fotografía profesional | Grande | Excelente |
| 85-94 | Uso general, web | Medio | Muy buena |
| 70-84 | Miniaturas, previews | Pequeño | Buena |
| 50-69 | Thumbnails | Muy pequeño | Aceptable |
| 1-49 | No recomendado | Mínimo | Pobre |

## ⚠️ Limitaciones

1. **Formatos de entrada**: Debe ser una imagen válida reconocida por Pillow
2. **Tamaño máximo**: Depende de la configuración del servidor
3. **Transparencia**: Se pierde (se reemplaza con fondo blanco)
4. **Animaciones**: Solo se guarda el primer frame (GIF animados)
5. **Metadatos EXIF**: Se preservan si están presentes

## 🔒 Seguridad

### Validaciones Implementadas
- ✅ Validación de extensión de destino (.jpg o .jpeg)
- ✅ Validación de formato de imagen
- ✅ Manejo de errores robusto
- ✅ Conversión segura de modos de color

### Recomendaciones
- 🔐 Implementar autenticación para uso en producción
- 🛡️ Limitar tamaño máximo de archivo
- 📝 Sanitizar nombres de archivo
- 🚫 Validar permisos de escritura en rutas

## 🚀 Integración con API de Perfiles

```python
# Ejemplo: Subir y convertir imagen de perfil
import httpx

async def upload_profile_image(user_id: int, heic_file):
    # 1. Convertir HEIC a JPG
    async with httpx.AsyncClient() as client:
        files = {"file": heic_file}
        params = {
            "destination_path": f"/profiles/{user_id}/avatar.jpg",
            "quality": 90
        }
        
        convert_response = await client.post(
            "http://ftp-api:8000/files/convert-to-jpg",
            params=params,
            files=files
        )
        
        result = convert_response.json()
        
        # 2. Registrar en la API de perfiles
        profile_response = await client.post(
            f"http://profile-api:8002/profiles/{user_id}/images",
            json={
                "filename": "avatar.jpg",
                "ftp_path": result["converted_path"],
                "file_size": result["details"]["converted_size_bytes"],
                "mime_type": "image/jpeg",
                "width": result["details"]["width"],
                "height": result["details"]["height"],
                "is_primary": True
            }
        )
        
        return profile_response.json()
```

## 📝 Notas

- El endpoint crea automáticamente los directorios necesarios
- La conversión se realiza en memoria (no se guardan archivos temporales)
- El archivo original no se modifica ni se guarda
- La URL retornada es relativa al servicio FTP

## 🆘 Solución de Problemas

### Error: "No se pudo abrir la imagen"
- Verifica que el archivo sea una imagen válida
- Asegúrate de que el formato esté soportado
- Comprueba que el archivo no esté corrupto

### Error: "Error al guardar archivo en FTP"
- Verifica la conexión con el servidor FTP
- Comprueba los permisos de escritura
- Asegúrate de que la ruta sea válida

### La imagen se ve muy comprimida
- Aumenta el parámetro `quality` (ej: 90-95)
- Ten en cuenta que esto aumentará el tamaño del archivo

### El fondo transparente se ve blanco
- Esto es normal, JPG no soporta transparencia
- Si necesitas transparencia, usa PNG en su lugar

---

**Última actualización**: 2024-01-09  
**Versión de la API**: 1.0.0

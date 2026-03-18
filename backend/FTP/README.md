# 📁 FTP File Management System

Sistema completo de gestión de archivos FTP con API REST (FastAPI) y Frontend Web (React + TypeScript).

## 🚀 Características

### Backend (API)
- ✅ **Subir archivos** al servidor FTP
- ✅ **Descargar archivos** desde el servidor FTP
- ✅ **Listar archivos y directorios** con información detallada
- ✅ **Eliminar archivos y directorios**
- ✅ **Mover archivos** entre directorios
- ✅ **Renombrar archivos** y directorios
- ✅ **Crear directorios** nuevos
- ✅ **Buscar archivos** con filtros avanzados (nombre, extensión, tamaño)
- ✅ **Obtener información** detallada de archivos
- ✅ **Convertir imágenes a JPG** (HEIC, PNG, WEBP, etc.)
- 📚 **Documentación interactiva** con Swagger UI
- 🔄 **Health checks** automáticos

### Frontend (Web UI)
- ✅ **Interfaz web moderna** con React + TypeScript
- ✅ **Navegación por carpetas** con breadcrumbs
- ✅ **Búsqueda avanzada** con filtros múltiples
- ✅ **Subida de archivos** con drag & drop
- ✅ **Gestión completa** de archivos y carpetas
- 📱 **Diseño responsive** (mobile-friendly)
- 🎨 **UI moderna** con gradientes y animaciones

### Infraestructura
- 🐳 **Totalmente dockerizado** (3 servicios)
- 🔄 **Health checks** automáticos
- 🌐 **CORS** configurado
- 🔒 **Variables de entorno** para configuración

## 📋 Requisitos

- Docker
- Docker Compose

## 🛠️ Instalación y Uso

### 1. Configurar credenciales (opcional)

Edita el archivo `.env` para cambiar las credenciales por defecto:

```env
FTP_USER=tu_usuario
FTP_PASS=tu_contraseña_segura
```

### 2. Iniciar los servicios

```bash
cd /home/agustin/Documentos/microservicios/FTP
docker-compose up -d
```

### 3. Verificar que los servicios estén corriendo

```bash
docker-compose ps
```

Deberías ver:
```
NAME            IMAGE                    STATUS
ftp-frontend    ftp-frontend             Up
ftp-api         ftp-api                  Up (healthy)
ftp-server      stilliard/pure-ftpd      Up (healthy)
```

### 4. Acceder a las aplicaciones

#### Frontend Web (Interfaz de Usuario)
- **Web UI**: http://localhost:3000

#### API REST (Documentación)
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **API Root**: http://localhost:8000

## 📖 Documentación de Endpoints

### 🏥 Health Check

Verifica el estado del servicio y la conexión FTP.

**Endpoint:** `GET /health`

**Ejemplo:**
```bash
curl http://localhost:8000/health
```

**Respuesta:**
```json
{
  "status": "healthy",
  "ftp_server": "ftp-server",
  "ftp_port": 21,
  "ftp_connected": true,
  "ftp_welcome": "Welcome to Pure-FTPd",
  "timestamp": "2025-10-06T02:00:00"
}
```

---

### 📂 Listar Archivos y Directorios

Lista todos los archivos y subdirectorios en una ruta específica.

**Endpoint:** `GET /files/list`

**Parámetros:**
- `path` (query, opcional): Ruta del directorio (default: "/")

**Ejemplo:**
```bash
# Listar raíz
curl "http://localhost:8000/files/list?path=/"

# Listar subdirectorio
curl "http://localhost:8000/files/list?path=/documentos"
```

**Respuesta:**
```json
[
  {
    "name": "documento.pdf",
    "type": "file",
    "size": 1024000,
    "modified": "Oct 06 02:00",
    "permissions": "-rw-r--r--"
  },
  {
    "name": "carpeta",
    "type": "directory",
    "size": 4096,
    "modified": "Oct 05 15:30",
    "permissions": "drwxr-xr-x"
  }
]
```

---

### ⬆️ Subir Archivo

Sube un archivo al servidor FTP.

**Endpoint:** `POST /files/upload`

**Parámetros:**
- `file` (form-data, requerido): Archivo a subir
- `destination_path` (query, opcional): Ruta destino (default: "/")

**Ejemplo:**
```bash
# Subir a la raíz
curl -X POST "http://localhost:8000/files/upload?destination_path=/" \
  -F "file=@/ruta/local/documento.pdf"

# Subir a un subdirectorio
curl -X POST "http://localhost:8000/files/upload?destination_path=/documentos" \
  -F "file=@/ruta/local/imagen.jpg"
```

**Respuesta:**
```json
{
  "message": "Archivo subido exitosamente",
  "filename": "documento.pdf",
  "destination_path": "/",
  "size_bytes": 1024000,
  "size_mb": 0.98
}
```

---

### ⬇️ Descargar Archivo

Descarga un archivo del servidor FTP.

**Endpoint:** `GET /files/download`

**Parámetros:**
- `file_path` (query, requerido): Ruta completa del archivo

**Ejemplo:**
```bash
# Descargar archivo
curl "http://localhost:8000/files/download?file_path=/documento.pdf" \
  -o documento_descargado.pdf

# Descargar desde subdirectorio
curl "http://localhost:8000/files/download?file_path=/documentos/imagen.jpg" \
  -o imagen.jpg
```

**Respuesta:** Stream del archivo (descarga directa)

---

### 🗑️ Eliminar Archivo o Directorio

Elimina un archivo o directorio del servidor FTP.

**Endpoint:** `DELETE /files/delete`

**Parámetros:**
- `file_path` (query, requerido): Ruta del archivo o directorio

**Ejemplo:**
```bash
# Eliminar archivo
curl -X DELETE "http://localhost:8000/files/delete?file_path=/documento.pdf"

# Eliminar directorio vacío
curl -X DELETE "http://localhost:8000/files/delete?file_path=/carpeta_vieja"
```

**Respuesta:**
```json
{
  "message": "Archivo eliminado exitosamente",
  "path": "/documento.pdf",
  "type": "file"
}
```

---

### 📦 Mover Archivo

Mueve un archivo de una ubicación a otra.

**Endpoint:** `POST /files/move`

**Body (JSON):**
```json
{
  "source_path": "/archivo.txt",
  "destination_path": "/carpeta/archivo.txt"
}
```

**Ejemplo:**
```bash
curl -X POST "http://localhost:8000/files/move" \
  -H "Content-Type: application/json" \
  -d '{
    "source_path": "/documento.pdf",
    "destination_path": "/archivos/documento.pdf"
  }'
```

**Respuesta:**
```json
{
  "message": "Archivo movido exitosamente",
  "source": "/documento.pdf",
  "destination": "/archivos/documento.pdf"
}
```

---

### ✏️ Renombrar Archivo o Directorio

Renombra un archivo o directorio.

**Endpoint:** `POST /files/rename`

**Body (JSON):**
```json
{
  "old_path": "/archivo_viejo.txt",
  "new_path": "/archivo_nuevo.txt"
}
```

**Ejemplo:**
```bash
curl -X POST "http://localhost:8000/files/rename" \
  -H "Content-Type: application/json" \
  -d '{
    "old_path": "/documento.pdf",
    "new_path": "/documento_actualizado.pdf"
  }'
```

**Respuesta:**
```json
{
  "message": "Renombrado exitosamente",
  "old_path": "/documento.pdf",
  "new_path": "/documento_actualizado.pdf"
}
```

---

### 📁 Crear Directorio

Crea un nuevo directorio en el servidor FTP.

**Endpoint:** `POST /files/mkdir`

**Body (JSON):**
```json
{
  "directory_path": "/nueva_carpeta"
}
```

**Ejemplo:**
```bash
curl -X POST "http://localhost:8000/files/mkdir" \
  -H "Content-Type: application/json" \
  -d '{"directory_path": "/documentos"}'

# Crear subdirectorio
curl -X POST "http://localhost:8000/files/mkdir" \
  -H "Content-Type: application/json" \
  -d '{"directory_path": "/documentos/2024"}'
```

**Respuesta:**
```json
{
  "message": "Directorio creado exitosamente",
  "path": "/documentos"
}
```

---

### ℹ️ Obtener Información de Archivo

Obtiene información detallada de un archivo específico.

**Endpoint:** `GET /files/info`

**Parámetros:**
- `file_path` (query, requerido): Ruta del archivo

**Ejemplo:**
```bash
curl "http://localhost:8000/files/info?file_path=/documento.pdf"
```

**Respuesta:**
```json
{
  "path": "/documento.pdf",
  "name": "documento.pdf",
  "directory": "/",
  "size_bytes": 1024000,
  "size_kb": 1000.0,
  "size_mb": 0.98,
  "modified": "20251006020000",
  "type": "file"
}
```

---

### 🖼️ Convertir Imagen a JPG

Convierte imágenes de cualquier formato (incluyendo HEIC/HEIF de iPhone) a JPG y las guarda en el servidor FTP.

**Endpoint:** `POST /files/convert-to-jpg`

**Parámetros:**
- `file` (form-data, requerido): Archivo de imagen a convertir
- `destination_path` (query, requerido): Ruta destino donde guardar el JPG (debe terminar en .jpg o .jpeg)
- `quality` (query, opcional): Calidad de compresión JPG (1-100, default: 85)

**Formatos soportados:**
- HEIC / HEIF (iPhone)
- PNG (con transparencia)
- BMP, WEBP, GIF, TIFF, ICO
- Y más formatos soportados por Pillow

**Ejemplo:**
```bash
# Convertir HEIC a JPG
curl -X POST "http://localhost:8000/files/convert-to-jpg?destination_path=/images/photo.jpg&quality=90" \
  -F "file=@IMG_1234.HEIC"

# Convertir PNG con transparencia
curl -X POST "http://localhost:8000/files/convert-to-jpg?destination_path=/converted/logo.jpg" \
  -F "file=@logo.png"
```

**Respuesta:**
```json
{
  "message": "Imagen convertida y guardada exitosamente",
  "original_format": "image/heic",
  "original_filename": "IMG_1234.HEIC",
  "converted_path": "/images/photo.jpg",
  "file_url": "/files/download?file_path=/images/photo.jpg",
  "details": {
    "original_size_bytes": 2458624,
    "original_size_mb": 2.34,
    "converted_size_bytes": 856234,
    "converted_size_mb": 0.82,
    "compression_ratio": 65.18,
    "width": 3024,
    "height": 4032,
    "quality": 90
  }
}
```

**Características:**
- ✅ Conversión automática de transparencia a fondo blanco
- ✅ Optimización automática del JPG
- ✅ Creación automática de directorios
- ✅ Información detallada de compresión y dimensiones

📖 **Documentación completa:** Ver [IMAGE_CONVERSION.md](IMAGE_CONVERSION.md)

---

## 🔧 Gestión de Servicios

### Ver logs

```bash
# Logs de la API
docker-compose logs -f ftp-api

# Logs del servidor FTP
docker-compose logs -f ftp-server

# Logs de ambos servicios
docker-compose logs -f
```

### Reiniciar servicios

```bash
docker-compose restart
```

### Detener servicios

```bash
docker-compose down
```

### Detener y eliminar volúmenes (⚠️ elimina todos los archivos)

```bash
docker-compose down -v
```

### Reconstruir la API después de cambios

```bash
docker-compose up -d --build ftp-api
```

## 📁 Estructura del Proyecto

```
FTP/
├── api/
│   ├── app/
│   │   └── main.py              # Código de la API FastAPI
│   ├── Dockerfile               # Imagen Docker de la API
│   └── requirements.txt         # Dependencias Python
├── ftp_data/                    # Datos del servidor FTP (volumen)
├── docker-compose.yml           # Configuración de servicios
├── .env                         # Variables de entorno
└── README.md                    # Esta documentación
```

## 🧪 Ejemplos de Uso Completos

### Ejemplo 1: Workflow completo de gestión de archivos

```bash
# 1. Verificar que el servicio está funcionando
curl http://localhost:8000/health

# 2. Crear un directorio para documentos
curl -X POST "http://localhost:8000/files/mkdir" \
  -H "Content-Type: application/json" \
  -d '{"directory_path": "/documentos"}'

# 3. Subir un archivo al directorio
curl -X POST "http://localhost:8000/files/upload?destination_path=/documentos" \
  -F "file=@documento.pdf"

# 4. Listar archivos en el directorio
curl "http://localhost:8000/files/list?path=/documentos"

# 5. Obtener información del archivo
curl "http://localhost:8000/files/info?file_path=/documentos/documento.pdf"

# 6. Renombrar el archivo
curl -X POST "http://localhost:8000/files/rename" \
  -H "Content-Type: application/json" \
  -d '{
    "old_path": "/documentos/documento.pdf",
    "new_path": "/documentos/documento_final.pdf"
  }'

# 7. Descargar el archivo
curl "http://localhost:8000/files/download?file_path=/documentos/documento_final.pdf" \
  -o documento_final.pdf
```

### Ejemplo 2: Organizar archivos por fecha

```bash
# Crear estructura de directorios
curl -X POST "http://localhost:8000/files/mkdir" \
  -H "Content-Type: application/json" \
  -d '{"directory_path": "/archivos_2024"}'

curl -X POST "http://localhost:8000/files/mkdir" \
  -H "Content-Type: application/json" \
  -d '{"directory_path": "/archivos_2024/octubre"}'

# Subir archivos
curl -X POST "http://localhost:8000/files/upload?destination_path=/archivos_2024/octubre" \
  -F "file=@reporte.pdf"

# Mover archivo a otra ubicación
curl -X POST "http://localhost:8000/files/move" \
  -H "Content-Type: application/json" \
  -d '{
    "source_path": "/archivos_2024/octubre/reporte.pdf",
    "destination_path": "/archivos_2024/reporte_octubre.pdf"
  }'
```

### Ejemplo 3: Script Python para usar la API

```python
import requests

API_URL = "http://localhost:8000"

# Subir archivo
with open("documento.pdf", "rb") as f:
    response = requests.post(
        f"{API_URL}/files/upload?destination_path=/",
        files={"file": f}
    )
    print(response.json())

# Listar archivos
response = requests.get(f"{API_URL}/files/list?path=/")
files = response.json()
for file in files:
    print(f"{file['name']} - {file['type']} - {file['size']} bytes")

# Descargar archivo
response = requests.get(
    f"{API_URL}/files/download?file_path=/documento.pdf"
)
with open("documento_descargado.pdf", "wb") as f:
    f.write(response.content)
```

## 🔒 Notas de Seguridad

- ⚠️ **Cambia las credenciales por defecto** en el archivo `.env` antes de usar en producción
- 🔐 Considera usar **FTPS** (FTP sobre SSL/TLS) para conexiones seguras
- 🛡️ Implementa **autenticación** en la API para producción (JWT, OAuth2, etc.)
- 🔑 No expongas el puerto FTP (21) públicamente si no es necesario
- 📝 Usa **variables de entorno** seguras para credenciales sensibles
- 🚫 Limita el acceso a la API mediante **firewall** o **reverse proxy**

## 🐛 Troubleshooting

### La API no puede conectarse al servidor FTP

```bash
# Verificar que ambos servicios estén en la misma red
docker network inspect ftp_ftp-network

# Verificar logs del servidor FTP
docker-compose logs ftp-server

# Reiniciar servicios
docker-compose restart
```

### Error de permisos al subir archivos

```bash
# Verificar permisos del volumen
ls -la ftp_data/

# Cambiar permisos si es necesario
sudo chmod -R 777 ftp_data/
```

### Puerto 21 ya está en uso

Si tienes otro servicio FTP corriendo, cambia el puerto en `docker-compose.yml`:

```yaml
ports:
  - "2121:21"  # Usar puerto 2121 en lugar de 21
```

## 📚 Tecnologías Utilizadas

- **FastAPI**: Framework web moderno y rápido para Python
- **Python ftplib**: Librería estándar para cliente FTP
- **Pure-FTPd**: Servidor FTP ligero y seguro
- **Docker & Docker Compose**: Containerización y orquestación
- **Uvicorn**: Servidor ASGI de alto rendimiento
- **Pydantic**: Validación de datos y settings management

## 📄 Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📧 Soporte

Si tienes problemas o preguntas, por favor abre un issue en el repositorio.

---

**¡Listo para usar! 🚀**

Inicia los servicios con `docker-compose up -d` y accede a http://localhost:8000/docs para ver la documentación interactiva.

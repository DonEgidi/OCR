from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import ftplib
import os
import io
from datetime import datetime
from PIL import Image
import pillow_heif

app = FastAPI(
    title="FTP File Management API",
    description="API REST para gestionar archivos en servidor FTP con todas las operaciones CRUD",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración FTP desde variables de entorno
FTP_HOST = os.getenv("FTP_HOST", "ftp-server")
FTP_PORT = int(os.getenv("FTP_PORT", "21"))
FTP_USER = os.getenv("FTP_USER", "ftpuser")
FTP_PASS = os.getenv("FTP_PASS", "ftppass")


class FTPConnection:
    """Context manager para manejar conexiones FTP de forma segura"""
    def __init__(self):
        self.ftp = None
    
    def __enter__(self):
        try:
            self.ftp = ftplib.FTP()
            self.ftp.connect(FTP_HOST, FTP_PORT, timeout=10)
            self.ftp.login(FTP_USER, FTP_PASS)
            return self.ftp
        except Exception as e:
            raise HTTPException(
                status_code=503,
                detail=f"No se pudo conectar al servidor FTP: {str(e)}"
            )
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.ftp:
            try:
                self.ftp.quit()
            except:
                self.ftp.close()


# Modelos Pydantic
class FileInfo(BaseModel):
    """Información de un archivo o directorio"""
    name: str = Field(..., description="Nombre del archivo o directorio")
    type: str = Field(..., description="Tipo: 'file' o 'directory'")
    size: int = Field(..., description="Tamaño en bytes")
    modified: str = Field(..., description="Fecha de modificación")
    permissions: str = Field(..., description="Permisos del archivo")


class MoveFileRequest(BaseModel):
    """Request para mover un archivo"""
    source_path: str = Field(..., description="Ruta origen del archivo", example="/archivo.txt")
    destination_path: str = Field(..., description="Ruta destino del archivo", example="/carpeta/archivo.txt")


class RenameRequest(BaseModel):
    """Request para renombrar un archivo o directorio"""
    old_path: str = Field(..., description="Ruta actual", example="/archivo.txt")
    new_path: str = Field(..., description="Nueva ruta/nombre", example="/nuevo_nombre.txt")


class CreateDirectoryRequest(BaseModel):
    """Request para crear un directorio"""
    directory_path: str = Field(..., description="Ruta del directorio a crear", example="/nueva_carpeta")


class SuccessResponse(BaseModel):
    """Respuesta exitosa genérica"""
    message: str
    details: Optional[dict] = None


# Endpoints
@app.get("/", tags=["General"])
async def root():
    """
    Endpoint raíz - Información de la API
    
    Retorna información básica sobre la API y sus endpoints disponibles.
    """
    return {
        "name": "FTP File Management API",
        "version": "1.0.0",
        "description": "API REST para gestionar archivos en servidor FTP",
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc"
        },
        "endpoints": {
            "health": "/health",
            "list_files": "/files/list",
            "upload": "/files/upload",
            "download": "/files/download",
            "delete": "/files/delete",
            "move": "/files/move",
            "rename": "/files/rename",
            "create_directory": "/files/mkdir",
            "file_info": "/files/info"
        }
    }


@app.get("/health", tags=["General"], response_model=dict)
async def health_check():
    """
    Health Check - Verificar estado del servicio
    
    Verifica que la API esté funcionando y que pueda conectarse al servidor FTP.
    
    **Respuestas:**
    - **200**: Servicio saludable y conectado al FTP
    - **503**: Servicio no disponible o sin conexión FTP
    """
    try:
        with FTPConnection() as ftp:
            welcome = ftp.getwelcome()
        return {
            "status": "healthy",
            "ftp_server": FTP_HOST,
            "ftp_port": FTP_PORT,
            "ftp_connected": True,
            "ftp_welcome": welcome,
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Servicio no disponible: {str(e)}"
        )


@app.get("/files/list", tags=["Archivos"], response_model=List[FileInfo])
async def list_files(path: str = Query("/", description="Ruta del directorio a listar")):
    """
    Listar Archivos y Directorios
    
    Lista todos los archivos y subdirectorios en la ruta especificada.
    
    **Parámetros:**
    - **path**: Ruta del directorio (default: "/")
    
    **Ejemplo de uso:**
    ```bash
    curl "http://localhost:8000/files/list?path=/"
    ```
    
    **Respuestas:**
    - **200**: Lista de archivos y directorios
    - **404**: Directorio no encontrado
    - **500**: Error del servidor
    """
    try:
        with FTPConnection() as ftp:
            # Cambiar al directorio especificado
            try:
                ftp.cwd(path)
            except ftplib.error_perm:
                raise HTTPException(
                    status_code=404,
                    detail=f"Directorio no encontrado: {path}"
                )
            
            files = []
            lines = []
            ftp.dir(lines.append)
            
            for line in lines:
                parts = line.split(maxsplit=8)
                if len(parts) >= 9:
                    permissions = parts[0]
                    size = parts[4] if parts[4].isdigit() else 0
                    name = parts[8]
                    file_type = "directory" if permissions.startswith('d') else "file"
                    modified = f"{parts[5]} {parts[6]} {parts[7]}"
                    
                    files.append(FileInfo(
                        name=name,
                        type=file_type,
                        size=int(size),
                        modified=modified,
                        permissions=permissions
                    ))
            
            return files
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Error al listar los archivos. Por favor, intenta nuevamente"
        )


@app.post("/files/upload", tags=["Archivos"])
async def upload_file(
    file: UploadFile = File(..., description="Archivo a subir"),
    destination_path: str = Query(..., description="Ruta completa del archivo destino (ej: /profiles/user_1/photo.jpg)")
):
    """
    Subir Archivo
    
    Sube un archivo al servidor FTP en la ruta especificada.
    
    **Parámetros:**
    - **file**: Archivo a subir (multipart/form-data)
    - **destination_path**: Ruta completa del archivo destino (incluyendo nombre)
    
    **Ejemplo de uso:**
    ```bash
    curl -X POST "http://localhost:8000/files/upload?destination_path=/carpeta/archivo.pdf" \\
      -F "file=@/ruta/local/documento.pdf"
    ```
    
    **Respuestas:**
    - **200**: Archivo subido exitosamente
    - **404**: Directorio destino no encontrado
    - **500**: Error al subir el archivo
    """
    try:
        print(f"📤 Upload request - destination_path: {destination_path}")
        print(f"📦 File: {file.filename}, content_type: {file.content_type}")
        
        # Leer contenido del archivo
        content = await file.read()
        print(f"📏 File size: {len(content)} bytes")
        
        # Separar directorio y nombre de archivo
        directory = os.path.dirname(destination_path)
        filename = os.path.basename(destination_path)
        print(f"📁 Directory: {directory}, Filename: {filename}")
        
        with FTPConnection() as ftp:
            # Si hay un directorio, cambiar a él
            if directory and directory != "/":
                try:
                    print(f"🔄 Cambiando a directorio: {directory}")
                    ftp.cwd(directory)
                    print(f"✅ Directorio cambiado exitosamente")
                except ftplib.error_perm as e:
                    print(f"❌ Error cambiando directorio: {str(e)}")
                    raise HTTPException(
                        status_code=404,
                        detail=f"Directorio destino no encontrado: {directory}"
                    )
            
            # Subir archivo con el nombre especificado
            print(f"📤 Subiendo archivo: {filename}")
            ftp.storbinary(f"STOR {filename}", io.BytesIO(content))
            print(f"✅ Archivo subido exitosamente")
            
            # Obtener tamaño del archivo subido
            try:
                size = ftp.size(filename)
            except:
                size = len(content)
        
        return {
            "message": "Archivo subido exitosamente",
            "filename": filename,
            "destination_path": destination_path,
            "size_bytes": size,
            "size_mb": round(size / (1024 * 1024), 2)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Error al subir el archivo. Por favor, intenta nuevamente"
        )


@app.get("/files/download", tags=["Archivos"])
async def download_file(
    file_path: str = Query(..., description="Ruta completa del archivo a descargar")
):
    """
    Descargar Archivo
    
    Descarga un archivo del servidor FTP.
    
    **Parámetros:**
    - **file_path**: Ruta completa del archivo en el servidor
    
    **Ejemplo de uso:**
    ```bash
    curl "http://localhost:8000/files/download?file_path=/documento.pdf" \\
      -o documento_descargado.pdf
    ```
    
    **Respuestas:**
    - **200**: Archivo descargado (stream)
    - **404**: Archivo no encontrado
    - **500**: Error al descargar
    """
    try:
        with FTPConnection() as ftp:
            # Verificar que el archivo existe
            try:
                size = ftp.size(file_path)
            except:
                raise HTTPException(
                    status_code=404,
                    detail=f"Archivo no encontrado: {file_path}"
                )
            
            # Descargar archivo a memoria
            bio = io.BytesIO()
            ftp.retrbinary(f"RETR {file_path}", bio.write)
            bio.seek(0)
            
            # Obtener nombre del archivo
            filename = os.path.basename(file_path)
        
        return StreamingResponse(
            bio,
            media_type="application/octet-stream",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Length": str(size)
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Error al descargar el archivo. Por favor, intenta nuevamente"
        )


@app.get("/files/view", tags=["Archivos"])
async def view_file(
    file_path: str = Query(..., description="Ruta completa del archivo a visualizar")
):
    """
    Visualizar Archivo
    
    Sirve un archivo del servidor FTP para visualización en el navegador (sin forzar descarga).
    
    **Parámetros:**
    - **file_path**: Ruta completa del archivo en el servidor
    
    **Ejemplo de uso:**
    ```bash
    curl "http://localhost:8000/files/view?file_path=/documento.pdf"
    ```
    
    **Respuestas:**
    - **200**: Archivo para visualización (stream)
    - **404**: Archivo no encontrado
    - **500**: Error al obtener archivo
    """
    try:
        with FTPConnection() as ftp:
            # Verificar que el archivo existe
            try:
                size = ftp.size(file_path)
            except:
                raise HTTPException(
                    status_code=404,
                    detail=f"Archivo no encontrado: {file_path}"
                )
            
            # Descargar archivo a memoria
            bio = io.BytesIO()
            ftp.retrbinary(f"RETR {file_path}", bio.write)
            bio.seek(0)
            
            # Obtener nombre y extensión del archivo
            filename = os.path.basename(file_path)
            extension = filename.split('.')[-1].lower() if '.' in filename else ''
            
            # Determinar media type según extensión
            media_types = {
                'pdf': 'application/pdf',
                'jpg': 'image/jpeg',
                'jpeg': 'image/jpeg',
                'png': 'image/png',
                'gif': 'image/gif',
                'webp': 'image/webp',
                'svg': 'image/svg+xml',
                'bmp': 'image/bmp',
                'mp4': 'video/mp4',
                'webm': 'video/webm',
                'ogg': 'video/ogg',
                'mov': 'video/quicktime',
                'mp3': 'audio/mpeg',
                'wav': 'audio/wav',
                'm4a': 'audio/mp4',
                'txt': 'text/plain',
                'md': 'text/markdown',
                'json': 'application/json',
                'xml': 'application/xml',
                'csv': 'text/csv',
                'log': 'text/plain',
            }
            
            media_type = media_types.get(extension, 'application/octet-stream')
        
        return StreamingResponse(
            bio,
            media_type=media_type,
            headers={
                "Content-Length": str(size),
                "Cache-Control": "public, max-age=3600"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Error al obtener el archivo. Por favor, intenta nuevamente"
        )


@app.delete("/files/delete", tags=["Archivos"])
async def delete_file(
    file_path: str = Query(..., description="Ruta del archivo o directorio a eliminar")
):
    """
    Eliminar Archivo o Directorio
    
    Elimina un archivo o directorio del servidor FTP.
    
    **Parámetros:**
    - **file_path**: Ruta completa del archivo o directorio
    
    **Ejemplo de uso:**
    ```bash
    # Eliminar archivo
    curl -X DELETE "http://localhost:8000/files/delete?file_path=/documento.pdf"
    
    # Eliminar directorio
    curl -X DELETE "http://localhost:8000/files/delete?file_path=/carpeta_vieja"
    ```
    
    **Respuestas:**
    - **200**: Eliminado exitosamente
    - **404**: Archivo o directorio no encontrado
    - **500**: Error al eliminar
    """
    try:
        with FTPConnection() as ftp:
            try:
                # Intentar eliminar como archivo
                ftp.delete(file_path)
                return {
                    "message": "Archivo eliminado exitosamente",
                    "path": file_path,
                    "type": "file"
                }
            except ftplib.error_perm:
                # Si falla, intentar como directorio
                try:
                    ftp.rmd(file_path)
                    return {
                        "message": "Directorio eliminado exitosamente",
                        "path": file_path,
                        "type": "directory"
                    }
                except ftplib.error_perm:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Archivo o directorio no encontrado: {file_path}"
                    )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Error al eliminar el archivo. Por favor, intenta nuevamente"
        )


@app.post("/files/move", tags=["Archivos"])
async def move_file(request: MoveFileRequest):
    """
    Mover Archivo
    
    Mueve un archivo de una ubicación a otra en el servidor FTP.
    
    **Body (JSON):**
    ```json
    {
      "source_path": "/archivo.txt",
      "destination_path": "/carpeta/archivo.txt"
    }
    ```
    
    **Ejemplo de uso:**
    ```bash
    curl -X POST "http://localhost:8000/files/move" \\
      -H "Content-Type: application/json" \\
      -d '{
        "source_path": "/documento.pdf",
        "destination_path": "/archivos/documento.pdf"
      }'
    ```
    
    **Respuestas:**
    - **200**: Archivo movido exitosamente
    - **404**: Archivo origen no encontrado
    - **500**: Error al mover
    """
    try:
        with FTPConnection() as ftp:
            # Verificar que el archivo origen existe
            try:
                ftp.size(request.source_path)
            except:
                raise HTTPException(
                    status_code=404,
                    detail=f"Archivo origen no encontrado: {request.source_path}"
                )
            
            # Mover archivo (rename en FTP funciona como move)
            try:
                ftp.rename(request.source_path, request.destination_path)
            except ftplib.error_perm as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"No se pudo mover el archivo: {str(e)}"
                )
        
        return {
            "message": "Archivo movido exitosamente",
            "source": request.source_path,
            "destination": request.destination_path
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Error al mover el archivo. Por favor, intenta nuevamente"
        )


@app.post("/files/rename", tags=["Archivos"])
async def rename_file(request: RenameRequest):
    """
    Renombrar Archivo o Directorio
    
    Renombra un archivo o directorio en el servidor FTP.
    
    **Body (JSON):**
    ```json
    {
      "old_path": "/archivo_viejo.txt",
      "new_path": "/archivo_nuevo.txt"
    }
    ```
    
    **Ejemplo de uso:**
    ```bash
    curl -X POST "http://localhost:8000/files/rename" \\
      -H "Content-Type: application/json" \\
      -d '{
        "old_path": "/documento.pdf",
        "new_path": "/documento_actualizado.pdf"
      }'
    ```
    
    **Respuestas:**
    - **200**: Renombrado exitosamente
    - **404**: Archivo no encontrado
    - **500**: Error al renombrar
    """
    try:
        with FTPConnection() as ftp:
            try:
                ftp.rename(request.old_path, request.new_path)
            except ftplib.error_perm as e:
                if "550" in str(e):
                    raise HTTPException(
                        status_code=404,
                        detail=f"Archivo no encontrado: {request.old_path}"
                    )
                raise HTTPException(
                    status_code=400,
                    detail=f"No se pudo renombrar: {str(e)}"
                )
        
        return {
            "message": "Renombrado exitosamente",
            "old_path": request.old_path,
            "new_path": request.new_path
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Error al renombrar el archivo. Por favor, intenta nuevamente"
        )


@app.post("/files/mkdir", tags=["Directorios"])
async def create_directory(request: CreateDirectoryRequest):
    """
    Crear Directorio
    
    Crea un nuevo directorio en el servidor FTP.
    
    **Body (JSON):**
    ```json
    {
      "directory_path": "/nueva_carpeta"
    }
    ```
    
    **Ejemplo de uso:**
    ```bash
    curl -X POST "http://localhost:8000/files/mkdir" \\
      -H "Content-Type: application/json" \\
      -d '{"directory_path": "/documentos"}'
    ```
    
    **Respuestas:**
    - **200**: Directorio creado exitosamente
    - **400**: El directorio ya existe o error de permisos
    - **500**: Error al crear directorio
    """
    try:
        with FTPConnection() as ftp:
            # Crear directorios recursivamente
            print(f"📁 Creando directorio recursivamente: {request.directory_path}")
            create_directories(ftp, request.directory_path)
            print(f"✅ Directorio creado: {request.directory_path}")
            
            return {
                "message": "Directorio creado exitosamente",
                "path": request.directory_path
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Error al crear el directorio. Por favor, intenta nuevamente"
        )


@app.get("/files/info", tags=["Archivos"])
async def get_file_info(
    file_path: str = Query(..., description="Ruta del archivo")
):
    """
    Obtener Información de Archivo
    
    Obtiene información detallada de un archivo específico.
    
    **Parámetros:**
    - **file_path**: Ruta completa del archivo
    
    **Ejemplo de uso:**
    ```bash
    curl "http://localhost:8000/files/info?file_path=/documento.pdf"
    ```
    
    **Respuestas:**
    - **200**: Información del archivo
    - **404**: Archivo no encontrado
    - **500**: Error al obtener información
    """
    try:
        with FTPConnection() as ftp:
            try:
                size = ftp.size(file_path)
                
                # Intentar obtener fecha de modificación
                try:
                    modified = ftp.voidcmd(f"MDTM {file_path}")[4:].strip()
                except:
                    modified = "No disponible"
                
                return {
                    "path": file_path,
                    "name": os.path.basename(file_path),
                    "directory": os.path.dirname(file_path) or "/",
                    "size_bytes": size,
                    "size_kb": round(size / 1024, 2),
                    "size_mb": round(size / (1024 * 1024), 2),
                    "modified": modified,
                    "type": "file"
                }
            except:
                raise HTTPException(
                    status_code=404,
                    detail=f"Archivo no encontrado: {file_path}"
                )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Error al obtener la información del archivo. Por favor, intenta nuevamente"
        )


@app.post("/files/convert-to-jpg", tags=["Archivos"])
async def convert_image_to_jpg(
    file: UploadFile = File(...),
    destination_path: str = Query(..., description="Ruta destino donde guardar el JPG (ej: /images/converted/image.jpg)"),
    quality: int = Query(85, ge=1, le=100, description="Calidad del JPG (1-100, default: 85)")
):
    """
    Convertir Imagen a JPG
    
    Convierte imágenes de cualquier formato (incluyendo HEIC, HEIF, PNG, BMP, WEBP, etc.) a JPG
    y las guarda en el servidor FTP.
    
    **Formatos soportados:**
    - HEIC / HEIF (iPhone)
    - PNG
    - BMP
    - WEBP
    - GIF
    - TIFF
    - Y más...
    
    **Parámetros:**
    - **file**: Archivo de imagen a convertir
    - **destination_path**: Ruta completa donde guardar el JPG (debe terminar en .jpg o .jpeg)
    - **quality**: Calidad de compresión JPG (1-100, default: 85)
    
    **Ejemplo de uso:**
    ```bash
    curl -X POST "http://localhost:8000/files/convert-to-jpg?destination_path=/images/photo.jpg&quality=90" \\
      -F "file=@image.heic"
    ```
    
    **Respuestas:**
    - **200**: Imagen convertida y guardada exitosamente
    - **400**: Error en la conversión o formato no soportado
    - **500**: Error al guardar en el servidor FTP
    """
    try:
        # Validar que la ruta destino termine en .jpg o .jpeg
        if not destination_path.lower().endswith(('.jpg', '.jpeg')):
            raise HTTPException(
                status_code=400,
                detail="La ruta destino debe terminar en .jpg o .jpeg"
            )
        
        # Leer el contenido del archivo
        content = await file.read()
        
        # Debug: Verificar que el archivo tiene contenido
        print(f"📸 Archivo recibido: {file.filename}")
        print(f"📦 Content-Type: {file.content_type}")
        print(f"📏 Tamaño: {len(content)} bytes")
        
        if len(content) == 0:
            raise HTTPException(
                status_code=400,
                detail="El archivo está vacío. No se recibió contenido."
            )
        
        # Intentar abrir la imagen
        try:
            # Primero intentar con pillow_heif directamente para archivos HEIC/HEIF
            if file.content_type in ('image/heic', 'image/heif', 'image/heic-sequence', 'image/heif-sequence'):
                print("🔄 Detectado archivo HEIC/HEIF, usando pillow_heif directamente")
                
                try:
                    # Método 1: Intentar con open_heif con opciones permisivas
                    heif_file = pillow_heif.open_heif(
                        io.BytesIO(content), 
                        convert_hdr_to_8bit=True,
                        decode_threads=1
                    )
                    print(f"📊 Archivo HEIC contiene {len(heif_file)} imagen(es)")
                    image = heif_file.to_pillow()
                    print(f"✅ HEIC abierto con open_heif: {image.size} {image.mode}")
                except Exception as e1:
                    print(f"⚠️  open_heif falló: {str(e1)}, intentando método alternativo...")
                    
                    # Método 2: Usar read_heif con opciones permisivas
                    try:
                        heif_file = pillow_heif.read_heif(
                            io.BytesIO(content),
                            convert_hdr_to_8bit=True
                        )
                        image = Image.frombytes(
                            heif_file.mode,
                            heif_file.size,
                            heif_file.data,
                            "raw",
                        )
                        print(f"✅ HEIC abierto con read_heif: {image.size} {image.mode}")
                    except Exception as e2:
                        print(f"⚠️  read_heif también falló: {str(e2)}")
                        
                        # Método 3: Intentar con from_bytes directamente
                        try:
                            print("🔄 Intentando método from_bytes...")
                            heif_file = pillow_heif.from_bytes(content)
                            image = heif_file[0].to_pillow()
                            print(f"✅ HEIC abierto con from_bytes: {image.size} {image.mode}")
                        except Exception as e3:
                            print(f"⚠️  from_bytes también falló: {str(e3)}")
                            raise e1  # Re-lanzar el primer error
            else:
                # Para otros formatos, usar PIL normal
                image = Image.open(io.BytesIO(content))
                print(f"✅ Imagen abierta correctamente: {image.format} {image.size} {image.mode}")
        except Exception as e:
            print(f"❌ Error abriendo imagen: {str(e)}")
            print(f"🔍 Primeros 100 bytes: {content[:100]}")
            raise HTTPException(
                status_code=400,
                detail=f"No se pudo abrir la imagen. Formato no soportado o archivo corrupto: {str(e)}"
            )
        
        # Convertir a RGB si es necesario (para transparencias, etc.)
        if image.mode in ('RGBA', 'LA', 'P'):
            # Crear fondo blanco
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            background.paste(image, mask=image.split()[-1] if image.mode in ('RGBA', 'LA') else None)
            image = background
        elif image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Convertir a JPG en memoria
        jpg_buffer = io.BytesIO()
        image.save(jpg_buffer, format='JPEG', quality=quality, optimize=True)
        jpg_buffer.seek(0)
        
        # Obtener información de la imagen
        original_size = len(content)
        converted_size = jpg_buffer.tell()
        width, height = image.size
        
        # Subir al servidor FTP
        try:
            with FTPConnection() as ftp:
                # Crear directorios si no existen
                directory = os.path.dirname(destination_path)
                print(f"📁 Directorio destino: {directory}")
                if directory and directory != "/":
                    create_directories(ftp, directory)
                
                # Subir el archivo JPG
                print(f"📤 Subiendo a FTP: {destination_path}")
                jpg_buffer.seek(0)  # Asegurar que el buffer esté al inicio
                ftp.storbinary(f'STOR {destination_path}', jpg_buffer)
                print(f"✅ Archivo guardado en FTP exitosamente")
        except Exception as e:
            print(f"❌ Error guardando en FTP: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error al guardar el archivo en el servidor FTP: {str(e)}"
            )
        
        # Construir URLs de acceso
        view_url = f"/files/view?file_path={destination_path}"
        download_url = f"/files/download?file_path={destination_path}"
        
        return {
            "message": "Imagen convertida y guardada exitosamente",
            "original_format": file.content_type,
            "original_filename": file.filename,
            "converted_path": destination_path,
            "file_url": view_url,  # URL para visualizar (usar en <img src="">)
            "download_url": download_url,  # URL para descargar
            "details": {
                "original_size_bytes": original_size,
                "original_size_mb": round(original_size / (1024 * 1024), 2),
                "converted_size_bytes": converted_size,
                "converted_size_mb": round(converted_size / (1024 * 1024), 2),
                "compression_ratio": round((1 - converted_size / original_size) * 100, 2) if original_size > 0 else 0,
                "width": width,
                "height": height,
                "quality": quality
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Error al convertir la imagen. Por favor, intenta nuevamente"
        )


def create_directories(ftp, path):
    """Crea directorios recursivamente en el servidor FTP"""
    if not path or path == '/':
        return
    
    parts = path.strip('/').split('/')
    current_path = ''
    
    for part in parts:
        if not part:  # Saltar partes vacías
            continue
            
        current_path += f'/{part}'
        try:
            # Intentar cambiar al directorio
            ftp.cwd(current_path)
            print(f"✅ Directorio existe: {current_path}")
        except Exception as e:
            # Si no existe, intentar crearlo
            try:
                print(f"📁 Creando directorio: {current_path}")
                ftp.mkd(current_path)
                ftp.cwd(current_path)
                print(f"✅ Directorio creado: {current_path}")
            except Exception as e2:
                print(f"⚠️  No se pudo crear directorio {current_path}: {str(e2)}")
                # Intentar continuar de todos modos
                pass
    
    # Volver al directorio raíz
    try:
        ftp.cwd('/')
    except:
        pass


@app.get("/files/search", tags=["Archivos"])
async def search_files(
    path: str = Query("/", description="Ruta donde buscar"),
    query: str = Query("", description="Término de búsqueda en el nombre"),
    extension: Optional[str] = Query(None, description="Filtrar por extensión (ej: pdf, txt)"),
    min_size: Optional[int] = Query(None, description="Tamaño mínimo en bytes"),
    max_size: Optional[int] = Query(None, description="Tamaño máximo en bytes")
):
    """
    Buscar Archivos
    
    Busca archivos en el servidor FTP con filtros avanzados.
    
    **Parámetros:**
    - **path**: Ruta donde buscar (default: "/")
    - **query**: Término de búsqueda en el nombre del archivo
    - **extension**: Filtrar por extensión (sin punto)
    - **min_size**: Tamaño mínimo en bytes
    - **max_size**: Tamaño máximo en bytes
    
    **Ejemplo de uso:**
    ```bash
    # Buscar archivos PDF
    curl "http://localhost:8000/files/search?path=/&extension=pdf"
    
    # Buscar archivos que contengan "documento"
    curl "http://localhost:8000/files/search?path=/&query=documento"
    
    # Buscar archivos entre 1MB y 10MB
    curl "http://localhost:8000/files/search?path=/&min_size=1048576&max_size=10485760"
    ```
    
    **Respuestas:**
    - **200**: Lista de archivos que coinciden con los filtros
    - **500**: Error en la búsqueda
    """
    try:
        def search_recursive(ftp, current_path, results):
            """Búsqueda recursiva en directorios"""
            try:
                ftp.cwd(current_path)
                lines = []
                ftp.dir(lines.append)
                
                for line in lines:
                    parts = line.split(maxsplit=8)
                    if len(parts) >= 9:
                        permissions = parts[0]
                        size = int(parts[4]) if parts[4].isdigit() else 0
                        name = parts[8]
                        file_type = "directory" if permissions.startswith('d') else "file"
                        modified = f"{parts[5]} {parts[6]} {parts[7]}"
                        
                        # Construir path completo
                        full_path = f"{current_path}/{name}".replace("//", "/")
                        
                        # Si es directorio, buscar recursivamente
                        if file_type == "directory" and name not in [".", ".."]:
                            search_recursive(ftp, full_path, results)
                        
                        # Aplicar filtros
                        if file_type == "file":
                            # Filtro por nombre
                            if query and query.lower() not in name.lower():
                                continue
                            
                            # Filtro por extensión
                            if extension:
                                file_ext = name.split(".")[-1] if "." in name else ""
                                if file_ext.lower() != extension.lower():
                                    continue
                            
                            # Filtro por tamaño mínimo
                            if min_size is not None and size < min_size:
                                continue
                            
                            # Filtro por tamaño máximo
                            if max_size is not None and size > max_size:
                                continue
                            
                            # Agregar a resultados
                            results.append(FileInfo(
                                name=name,
                                type=file_type,
                                size=size,
                                modified=modified,
                                permissions=permissions
                            ))
            except:
                pass  # Ignorar errores en subdirectorios sin permisos
        
        with FTPConnection() as ftp:
            results = []
            search_recursive(ftp, path, results)
            return results
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error en la búsqueda: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

# 🚀 Inicio Rápido - FTP File Management API

Guía rápida para poner en marcha el proyecto en menos de 5 minutos.

## ⚡ Pasos Rápidos

### 1. Iniciar los servicios

```bash
cd /home/agustin/Documentos/microservicios/FTP
docker-compose up -d
```

### 2. Verificar que todo esté funcionando

```bash
# Verificar estado de los contenedores
docker-compose ps

# Verificar health check de la API
curl http://localhost:8000/health
```

### 3. Acceder a la documentación interactiva

Abre en tu navegador: **http://localhost:8000/docs**

## 🧪 Prueba Rápida

### Crear un archivo de prueba

```bash
echo "Hola desde FTP API" > test.txt
```

### Subir el archivo

```bash
curl -X POST "http://localhost:8000/files/upload?destination_path=/" \
  -F "file=@test.txt"
```

### Listar archivos

```bash
curl "http://localhost:8000/files/list?path=/"
```

### Descargar el archivo

```bash
curl "http://localhost:8000/files/download?file_path=/test.txt" \
  -o test_descargado.txt
```

### Verificar el contenido

```bash
cat test_descargado.txt
```

## 📊 Comandos Útiles

### Ver logs en tiempo real

```bash
# Logs de la API
docker-compose logs -f ftp-api

# Logs del servidor FTP
docker-compose logs -f ftp-server
```

### Reiniciar servicios

```bash
docker-compose restart
```

### Detener servicios

```bash
docker-compose down
```

### Reconstruir después de cambios

```bash
docker-compose up -d --build
```

## 🔧 Configuración Personalizada

### Cambiar credenciales FTP

Edita el archivo `.env`:

```env
FTP_USER=mi_usuario
FTP_PASS=mi_contraseña_segura
```

Luego reinicia los servicios:

```bash
docker-compose down
docker-compose up -d
```

### Cambiar puertos

Edita `docker-compose.yml`:

```yaml
services:
  ftp-api:
    ports:
      - "8080:8000"  # Cambiar puerto de la API a 8080
```

## 📱 Prueba con Python

Crea un archivo `test_api.py`:

```python
import requests

API_URL = "http://localhost:8000"

# Health check
response = requests.get(f"{API_URL}/health")
print("Estado:", response.json())

# Subir archivo
with open("test.txt", "rb") as f:
    response = requests.post(
        f"{API_URL}/files/upload?destination_path=/",
        files={"file": f}
    )
    print("Upload:", response.json())

# Listar archivos
response = requests.get(f"{API_URL}/files/list?path=/")
print("Archivos:", response.json())
```

Ejecuta:

```bash
python3 test_api.py
```

## 🌐 Acceso desde otra máquina

Si quieres acceder desde otra máquina en tu red local:

1. Obtén tu IP local:
```bash
hostname -I | awk '{print $1}'
```

2. Usa esa IP en lugar de `localhost`:
```bash
curl "http://192.168.1.100:8000/health"
```

## 🐛 Solución de Problemas

### Error: "puerto ya en uso"

```bash
# Ver qué está usando el puerto 8000
sudo lsof -i :8000

# Cambiar el puerto en docker-compose.yml
```

### Error: "no se puede conectar al FTP"

```bash
# Verificar que el servidor FTP esté corriendo
docker-compose ps

# Ver logs del servidor FTP
docker-compose logs ftp-server

# Reiniciar servicios
docker-compose restart
```

### Error de permisos en ftp_data

```bash
# Dar permisos al directorio de datos
sudo chmod -R 777 ftp_data/
```

## 📚 Siguiente Paso

Lee la documentación completa en [README.md](README.md) para conocer todos los endpoints y opciones disponibles.

---

**¡Listo! Tu API FTP está funcionando** 🎉

Accede a http://localhost:8000/docs para explorar todos los endpoints disponibles.

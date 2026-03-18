# 🚀 Guía de Despliegue - FTP File Management System

Instrucciones completas para desplegar el sistema en diferentes entornos.

---

## 📋 Pre-requisitos

### Desarrollo Local
- Docker 20.10+
- Docker Compose 2.0+
- 2GB RAM disponible
- Puertos libres: 21, 3000, 8000, 30000-30009

### Producción
- Servidor Linux (Ubuntu 20.04+ recomendado)
- Docker y Docker Compose instalados
- Dominio configurado (opcional)
- Certificado SSL (recomendado)

---

## 🏠 Despliegue Local (Desarrollo)

### Opción 1: Con Docker (Recomendado)

```bash
# 1. Clonar o navegar al proyecto
cd /home/agustin/Documentos/microservicios/FTP

# 2. Configurar variables de entorno (opcional)
cp .env .env.local
nano .env.local

# 3. Iniciar todos los servicios
docker-compose up -d

# 4. Verificar estado
docker-compose ps

# 5. Ver logs
docker-compose logs -f

# 6. Acceder
# Frontend: http://localhost:3000
# API: http://localhost:8000/docs
```

### Opción 2: Desarrollo Sin Docker

**Backend:**
```bash
cd api
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

**Nota**: Necesitarás un servidor FTP corriendo externamente.

---

## 🌐 Despliegue en Producción

### 1. Preparar el Servidor

```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verificar instalación
docker --version
docker-compose --version
```

### 2. Configurar el Proyecto

```bash
# Clonar proyecto
git clone <tu-repositorio> /opt/ftp-manager
cd /opt/ftp-manager

# Configurar variables de entorno
cp .env .env.production
nano .env.production
```

**Configuración de producción (.env.production):**
```env
# Credenciales FTP (CAMBIAR)
FTP_USER=admin_ftp
FTP_PASS=SuperSecurePassword123!

# API
API_HOST=0.0.0.0
API_PORT=8000

# Frontend
VITE_API_URL=https://api.tudominio.com
```

### 3. Configurar Firewall

```bash
# Permitir puertos necesarios
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw allow 21/tcp    # FTP
sudo ufw allow 30000:30009/tcp  # FTP pasivo
sudo ufw enable
```

### 4. Configurar Nginx como Reverse Proxy

```bash
# Instalar Nginx
sudo apt install nginx -y

# Crear configuración
sudo nano /etc/nginx/sites-available/ftp-manager
```

**Configuración Nginx:**
```nginx
# Frontend
server {
    listen 80;
    server_name tudominio.com www.tudominio.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}

# API
server {
    listen 80;
    server_name api.tudominio.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Habilitar sitio
sudo ln -s /etc/nginx/sites-available/ftp-manager /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 5. Configurar SSL con Let's Encrypt

```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtener certificados
sudo certbot --nginx -d tudominio.com -d www.tudominio.com
sudo certbot --nginx -d api.tudominio.com

# Renovación automática (ya configurada)
sudo certbot renew --dry-run
```

### 6. Iniciar Servicios

```bash
cd /opt/ftp-manager

# Iniciar con variables de producción
docker-compose --env-file .env.production up -d

# Verificar
docker-compose ps
docker-compose logs -f
```

### 7. Configurar Reinicio Automático

```bash
# Crear servicio systemd
sudo nano /etc/systemd/system/ftp-manager.service
```

**Contenido del servicio:**
```ini
[Unit]
Description=FTP Manager Services
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/ftp-manager
ExecStart=/usr/local/bin/docker-compose --env-file .env.production up -d
ExecStop=/usr/local/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

```bash
# Habilitar servicio
sudo systemctl daemon-reload
sudo systemctl enable ftp-manager
sudo systemctl start ftp-manager
sudo systemctl status ftp-manager
```

---

## 🔒 Seguridad en Producción

### 1. Cambiar Credenciales por Defecto

```bash
# Editar .env.production
nano .env.production

# Generar contraseña segura
openssl rand -base64 32
```

### 2. Configurar FTPS (FTP sobre SSL)

Editar `docker-compose.yml`:
```yaml
ftp-server:
  image: stilliard/pure-ftpd
  environment:
    # ... otras variables
    TLS_CN: "tudominio.com"
    TLS_ORG: "Tu Organización"
  volumes:
    - ./ssl:/etc/ssl/private
```

### 3. Implementar Autenticación en la API

Agregar JWT authentication (ejemplo):
```python
# En api/app/main.py
from fastapi.security import HTTPBearer

security = HTTPBearer()

@app.get("/files/list")
async def list_files(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # Validar token
    # ...
```

### 4. Rate Limiting

Usar Nginx para rate limiting:
```nginx
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

server {
    location /api {
        limit_req zone=api_limit burst=20;
        # ...
    }
}
```

---

## 📊 Monitoreo y Logs

### Ver Logs en Producción

```bash
# Todos los servicios
docker-compose logs -f

# Servicio específico
docker-compose logs -f ftp-api
docker-compose logs -f ftp-frontend
docker-compose logs -f ftp-server

# Últimas 100 líneas
docker-compose logs --tail=100 ftp-api
```

### Configurar Logrotate

```bash
sudo nano /etc/logrotate.d/ftp-manager
```

```
/var/lib/docker/containers/*/*.log {
    rotate 7
    daily
    compress
    missingok
    delaycompress
    copytruncate
}
```

### Monitoreo con Prometheus (Opcional)

Agregar a `docker-compose.yml`:
```yaml
prometheus:
  image: prom/prometheus
  ports:
    - "9090:9090"
  volumes:
    - ./prometheus.yml:/etc/prometheus/prometheus.yml

grafana:
  image: grafana/grafana
  ports:
    - "3001:3000"
```

---

## 🔄 Actualización del Sistema

### Actualizar Código

```bash
cd /opt/ftp-manager

# Detener servicios
docker-compose down

# Actualizar código
git pull origin main

# Reconstruir imágenes
docker-compose build

# Iniciar servicios
docker-compose --env-file .env.production up -d

# Verificar
docker-compose ps
```

### Backup Antes de Actualizar

```bash
# Backup de datos FTP
tar -czf ftp_data_backup_$(date +%Y%m%d).tar.gz ftp_data/

# Backup de configuración
cp .env.production .env.production.backup
cp docker-compose.yml docker-compose.yml.backup
```

---

## 💾 Backup y Restauración

### Backup Automático

Crear script de backup:
```bash
sudo nano /usr/local/bin/backup-ftp-manager.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/backup/ftp-manager"
DATE=$(date +%Y%m%d_%H%M%S)

# Crear directorio de backup
mkdir -p $BACKUP_DIR

# Backup de datos FTP
tar -czf $BACKUP_DIR/ftp_data_$DATE.tar.gz /opt/ftp-manager/ftp_data/

# Backup de configuración
cp /opt/ftp-manager/.env.production $BACKUP_DIR/env_$DATE.backup

# Limpiar backups antiguos (más de 7 días)
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completado: $DATE"
```

```bash
# Hacer ejecutable
sudo chmod +x /usr/local/bin/backup-ftp-manager.sh

# Programar con cron (diario a las 2 AM)
sudo crontab -e
# Agregar:
0 2 * * * /usr/local/bin/backup-ftp-manager.sh >> /var/log/ftp-backup.log 2>&1
```

### Restaurar desde Backup

```bash
# Detener servicios
docker-compose down

# Restaurar datos
tar -xzf /backup/ftp-manager/ftp_data_YYYYMMDD.tar.gz -C /

# Restaurar configuración
cp /backup/ftp-manager/env_YYYYMMDD.backup /opt/ftp-manager/.env.production

# Iniciar servicios
docker-compose --env-file .env.production up -d
```

---

## 🧪 Testing en Producción

### Health Check

```bash
# API
curl https://api.tudominio.com/health

# Frontend
curl https://tudominio.com
```

### Test de Endpoints

```bash
# Listar archivos
curl https://api.tudominio.com/files/list?path=/

# Subir archivo
curl -X POST "https://api.tudominio.com/files/upload?destination_path=/" \
  -F "file=@test.txt"
```

---

## 📈 Escalabilidad

### Múltiples Instancias de API

```yaml
# docker-compose.yml
ftp-api:
  build: ./api
  deploy:
    replicas: 3
  # ...
```

### Load Balancer con Nginx

```nginx
upstream api_backend {
    least_conn;
    server localhost:8001;
    server localhost:8002;
    server localhost:8003;
}

server {
    location / {
        proxy_pass http://api_backend;
    }
}
```

---

## 🐛 Troubleshooting en Producción

### Problema: Servicios no inician

```bash
# Ver logs detallados
docker-compose logs --tail=100

# Verificar recursos
docker stats

# Verificar puertos
sudo netstat -tulpn | grep -E ':(21|3000|8000|30000)'
```

### Problema: Alto uso de memoria

```bash
# Limitar memoria en docker-compose.yml
services:
  ftp-api:
    mem_limit: 512m
    mem_reservation: 256m
```

### Problema: Conexión FTP lenta

```bash
# Verificar red
docker network inspect ftp_ftp-network

# Reiniciar servidor FTP
docker-compose restart ftp-server
```

---

## 📞 Checklist de Despliegue

### Pre-despliegue
- [ ] Servidor preparado con Docker
- [ ] Firewall configurado
- [ ] Dominio apuntando al servidor
- [ ] Credenciales cambiadas
- [ ] SSL configurado
- [ ] Backup configurado

### Post-despliegue
- [ ] Servicios corriendo
- [ ] Health checks pasando
- [ ] Frontend accesible
- [ ] API accesible
- [ ] FTP funcionando
- [ ] Logs monitoreados
- [ ] Backup funcionando

---

## 🎯 Mejores Prácticas

1. **Siempre usar HTTPS en producción**
2. **Cambiar credenciales por defecto**
3. **Configurar backups automáticos**
4. **Monitorear logs regularmente**
5. **Actualizar dependencias periódicamente**
6. **Usar variables de entorno para secretos**
7. **Implementar rate limiting**
8. **Configurar alertas de monitoreo**

---

## 📚 Recursos Adicionales

- [Docker Documentation](https://docs.docker.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Let's Encrypt](https://letsencrypt.org/)

---

**¡Despliegue exitoso! 🚀**

Para soporte, consulta los logs o la documentación completa en README.md

# 🎯 COMIENZA AQUÍ

## 🚀 Inicio Rápido (3 pasos)

### 1️⃣ Iniciar los servicios

```bash
cd /home/agustin/Documentos/microservicios/FTP
docker-compose up -d
```

O usando Makefile:
```bash
make up
```

### 2️⃣ Verificar que funciona

```bash
curl http://localhost:8000/health
```

O usando Makefile:
```bash
make health
```

### 3️⃣ Abrir la documentación

Visita en tu navegador: **http://localhost:8000/docs**

O usando Makefile:
```bash
make docs
```

---

## 📚 ¿Qué puedo hacer ahora?

### 🧪 Ejecutar pruebas automáticas
```bash
bash test_api.sh
# o
make test
```

### 📖 Ver documentación completa
- **README.md** - Documentación completa de todos los endpoints
- **QUICKSTART.md** - Guía rápida de 5 minutos
- **EXAMPLES.md** - Ejemplos en 7 lenguajes de programación
- **PROJECT_SUMMARY.md** - Resumen técnico del proyecto

### 🛠️ Comandos útiles con Makefile

```bash
make help        # Ver todos los comandos disponibles
make up          # Iniciar servicios
make down        # Detener servicios
make restart     # Reiniciar servicios
make logs        # Ver logs en tiempo real
make logs-api    # Ver solo logs de la API
make logs-ftp    # Ver solo logs del FTP
make status      # Ver estado de servicios
make health      # Verificar health de la API
make test        # Ejecutar tests
make rebuild     # Reconstruir y reiniciar
make clean       # Limpiar todo (⚠️ elimina datos)
```

---

## 🎨 Ejemplo Rápido

### Crear un archivo y subirlo

```bash
# 1. Crear archivo de prueba
echo "Hola Mundo desde FTP API" > hola.txt

# 2. Subir archivo
curl -X POST "http://localhost:8000/files/upload?destination_path=/" \
  -F "file=@hola.txt"

# 3. Listar archivos
curl "http://localhost:8000/files/list?path=/"

# 4. Descargar archivo
curl "http://localhost:8000/files/download?file_path=/hola.txt" \
  -o hola_descargado.txt

# 5. Ver contenido
cat hola_descargado.txt
```

---

## 🌐 URLs Importantes

| Servicio | URL |
|----------|-----|
| **Frontend Web** | **http://localhost:3000** |
| API Root | http://localhost:8000 |
| Swagger UI | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |
| Health Check | http://localhost:8000/health |

---

## 📋 Todos los Endpoints Disponibles

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/health` | Verificar estado del servicio |
| GET | `/files/list` | Listar archivos y directorios |
| POST | `/files/upload` | Subir archivo |
| GET | `/files/download` | Descargar archivo |
| DELETE | `/files/delete` | Eliminar archivo o directorio |
| POST | `/files/move` | Mover archivo |
| POST | `/files/rename` | Renombrar archivo |
| POST | `/files/mkdir` | Crear directorio |
| GET | `/files/info` | Información de archivo |

---

## 🔧 Configuración

### Cambiar credenciales FTP

Edita el archivo `.env`:
```env
FTP_USER=mi_usuario
FTP_PASS=mi_contraseña_segura
```

Luego reinicia:
```bash
make restart
```

---

## 🐛 ¿Problemas?

### La API no responde
```bash
make logs-api
make restart
```

### El FTP no conecta
```bash
make logs-ftp
make restart
```

### Ver estado de servicios
```bash
make status
```

---

## 📞 Más Ayuda

1. **Documentación completa**: Lee `README.md`
2. **Guía rápida**: Lee `QUICKSTART.md`
3. **Ejemplos de código**: Lee `EXAMPLES.md`
4. **Resumen técnico**: Lee `PROJECT_SUMMARY.md`

---

## ✅ Checklist de Inicio

- [ ] Ejecutar `docker-compose up -d` o `make up`
- [ ] Verificar con `curl http://localhost:8000/health`
- [ ] Abrir http://localhost:8000/docs en el navegador
- [ ] Ejecutar `bash test_api.sh` o `make test`
- [ ] Probar subir un archivo desde Swagger UI
- [ ] Leer la documentación completa en README.md

---

**🎉 ¡Listo! Tu API FTP está funcionando**

Para comenzar a usarla, visita: **http://localhost:8000/docs**

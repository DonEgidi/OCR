# 🎨 Guía del Frontend - FTP File Manager

Guía completa de uso del frontend web para gestión de archivos FTP.

## 🚀 Acceso Rápido

Una vez iniciados los servicios con `docker-compose up -d`, accede a:

**http://localhost:3000**

## 📱 Características Principales

### 1. Navegación por Carpetas

- **Breadcrumbs**: Navega fácilmente por la jerarquía de carpetas
- **Click en carpetas**: Haz clic en cualquier carpeta para entrar
- **Botón "Inicio"**: Vuelve a la raíz con un clic

### 2. Búsqueda Avanzada

#### Búsqueda Simple
- Escribe en el campo de búsqueda para filtrar por nombre de archivo
- La búsqueda es case-insensitive (no distingue mayúsculas/minúsculas)

#### Filtros Avanzados
Haz clic en el botón "Filtros" para acceder a:

- **Extensión**: Filtra por tipo de archivo (pdf, txt, jpg, etc.)
- **Tamaño mínimo**: Archivos mayores a X MB
- **Tamaño máximo**: Archivos menores a X MB

**Ejemplos de uso:**
```
Buscar todos los PDFs:
- Extensión: pdf

Buscar archivos grandes (más de 10 MB):
- Tamaño mínimo: 10

Buscar imágenes pequeñas (menos de 5 MB):
- Extensión: jpg
- Tamaño máximo: 5

Buscar documentos que contengan "reporte":
- Búsqueda: reporte
- Extensión: pdf
```

### 3. Subir Archivos

**Método 1: Botón "Subir Archivo"**
1. Haz clic en "Subir Archivo"
2. Selecciona el archivo desde tu computadora
3. Haz clic en "Subir"

**Método 2: Drag & Drop**
1. Haz clic en "Subir Archivo"
2. Arrastra el archivo desde tu explorador de archivos
3. Suéltalo en el área de subida
4. Haz clic en "Subir"

### 4. Crear Carpetas

1. Haz clic en "Nueva Carpeta"
2. Escribe el nombre de la carpeta
3. Haz clic en "Crear"

**Nota**: La carpeta se creará en el directorio actual.

### 5. Descargar Archivos

1. Localiza el archivo en la lista
2. Haz clic en el icono de descarga (⬇️)
3. El archivo se descargará automáticamente

### 6. Renombrar Archivos/Carpetas

1. Localiza el archivo o carpeta
2. Haz clic en el icono de edición (✏️)
3. Escribe el nuevo nombre
4. Haz clic en "Renombrar"

**Nota**: Mantén la extensión del archivo al renombrar.

### 7. Eliminar Archivos/Carpetas

1. Localiza el archivo o carpeta
2. Haz clic en el icono de eliminar (🗑️)
3. Confirma la eliminación

**⚠️ Advertencia**: Esta acción no se puede deshacer.

## 🎯 Casos de Uso Comunes

### Organizar Archivos por Tipo

1. Crea carpetas para cada tipo:
   - "Documentos"
   - "Imágenes"
   - "Videos"

2. Usa la búsqueda para encontrar archivos por extensión:
   - Extensión: pdf → Encuentra todos los PDFs
   - Extensión: jpg → Encuentra todas las imágenes

3. Descarga y vuelve a subir en la carpeta correcta

### Limpiar Archivos Grandes

1. Abre los filtros avanzados
2. Establece tamaño mínimo: 100 (MB)
3. Revisa los archivos grandes
4. Elimina los que no necesites

### Buscar Documentos Recientes

1. Ordena por fecha de modificación (columna "Modificado")
2. Los archivos más recientes aparecerán primero

### Backup de Archivos Importantes

1. Navega a la carpeta con archivos importantes
2. Usa el icono de descarga en cada archivo
3. Los archivos se guardarán en tu carpeta de descargas

## 🎨 Interfaz de Usuario

### Colores y Significados

- **Azul**: Acciones principales (Subir, Descargar)
- **Verde**: Crear nuevo (Nueva Carpeta)
- **Amarillo**: Editar/Modificar (Renombrar)
- **Rojo**: Eliminar (Borrar)
- **Morado**: Header/Branding

### Iconos

- 🏠 **Inicio**: Volver a la raíz
- 📁 **Carpeta**: Directorio
- 📄 **Archivo**: Documento
- ⬇️ **Descargar**: Bajar archivo
- ✏️ **Editar**: Renombrar
- 🗑️ **Eliminar**: Borrar
- 🔍 **Buscar**: Filtrar archivos
- 🎯 **Filtros**: Búsqueda avanzada

## 📱 Uso en Móviles

El frontend es completamente responsive:

### En Tablets (768px - 1024px)
- Layout adaptado con columnas más estrechas
- Botones optimizados para touch
- Navegación simplificada

### En Móviles (< 768px)
- Vista de lista vertical
- Botones de acción apilados
- Breadcrumbs compactos
- Modales a pantalla completa

## ⌨️ Atajos de Teclado

- **Enter** en modales: Confirmar acción
- **Escape** en modales: Cancelar
- **Tab**: Navegar entre campos

## 🔧 Solución de Problemas

### El frontend no carga

```bash
# Verificar que el contenedor está corriendo
docker-compose ps

# Ver logs del frontend
docker-compose logs ftp-frontend

# Reiniciar el frontend
docker-compose restart ftp-frontend
```

### Error al subir archivos

- Verifica que el archivo no sea demasiado grande
- Asegúrate de tener permisos en el directorio
- Revisa los logs de la API: `docker-compose logs ftp-api`

### La búsqueda no funciona

- Asegúrate de hacer clic en "Buscar" después de aplicar filtros
- Verifica que la API esté respondiendo: http://localhost:8000/health
- Usa "Limpiar Búsqueda" para resetear los filtros

### Los archivos no se muestran

- Verifica que estás en el directorio correcto
- Revisa los permisos del servidor FTP
- Comprueba la conexión con: `docker-compose logs ftp-server`

## 🎓 Tips y Trucos

### Navegación Rápida

- Usa los breadcrumbs para saltar entre niveles
- Haz clic en "Inicio" para volver a la raíz rápidamente

### Búsqueda Eficiente

- Combina múltiples filtros para búsquedas precisas
- Usa extensiones sin el punto (pdf, no .pdf)
- Los tamaños están en MB para facilitar el uso

### Gestión de Archivos

- Renombra archivos con nombres descriptivos
- Organiza en carpetas por proyecto o fecha
- Elimina archivos temporales regularmente

### Subida de Archivos

- Arrastra múltiples archivos uno por uno
- Verifica el tamaño antes de subir
- Usa nombres sin espacios ni caracteres especiales

## 🌟 Mejores Prácticas

1. **Organización**
   - Crea una estructura de carpetas lógica
   - Usa nombres descriptivos
   - Mantén una jerarquía no muy profunda

2. **Nomenclatura**
   - Usa guiones o guiones bajos en lugar de espacios
   - Incluye fechas en formato YYYY-MM-DD
   - Evita caracteres especiales

3. **Mantenimiento**
   - Limpia archivos antiguos regularmente
   - Usa la búsqueda para encontrar duplicados
   - Mantén backups de archivos importantes

4. **Seguridad**
   - No subas información sensible sin encriptar
   - Verifica los permisos de las carpetas
   - Cambia las credenciales por defecto

## 📊 Información Técnica

### Tecnologías

- **React 18**: Librería UI
- **TypeScript**: Tipado estático
- **Vite**: Build tool
- **Axios**: Cliente HTTP
- **Lucide React**: Iconos
- **CSS3**: Estilos personalizados

### Arquitectura

```
Frontend (React) → Nginx → API (FastAPI) → FTP Server
```

### Comunicación

- El frontend se comunica con la API vía HTTP
- La API se comunica con el servidor FTP vía protocolo FTP
- Todas las operaciones son asíncronas

## 🔗 Enlaces Útiles

- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 📞 Soporte

Si encuentras problemas:

1. Revisa esta guía
2. Consulta los logs: `docker-compose logs`
3. Verifica el estado: `docker-compose ps`
4. Reinicia los servicios: `docker-compose restart`

---

**¡Disfruta gestionando tus archivos FTP! 🚀**

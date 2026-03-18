# FTP Frontend - React + TypeScript + Vite

Frontend moderno para gestión de archivos FTP construido con React, TypeScript y Vite.

## 🚀 Características

- ✅ Navegación por carpetas intuitiva
- ✅ Búsqueda avanzada con filtros
- ✅ Filtrado por extensión de archivo
- ✅ Filtrado por tamaño (min/max)
- ✅ Subida de archivos con drag & drop
- ✅ Descarga de archivos
- ✅ Renombrar archivos y carpetas
- ✅ Eliminar archivos y carpetas
- ✅ Crear nuevas carpetas
- ✅ Interfaz responsive (mobile-friendly)
- ✅ Diseño moderno con gradientes

## 🛠️ Tecnologías

- **React 18** - Librería UI
- **TypeScript** - Tipado estático
- **Vite** - Build tool y dev server
- **Axios** - Cliente HTTP
- **Lucide React** - Iconos
- **CSS3** - Estilos personalizados

## 📦 Instalación Local

```bash
# Instalar dependencias
npm install

# Modo desarrollo
npm run dev

# Build para producción
npm run build

# Preview del build
npm run preview
```

## 🐳 Docker

El frontend está incluido en el docker-compose.yml principal:

```bash
# Desde la raíz del proyecto
docker-compose up -d ftp-frontend
```

## 🌐 Acceso

- **Desarrollo**: http://localhost:3000
- **Producción (Docker)**: http://localhost:3000

## 📁 Estructura

```
frontend/
├── src/
│   ├── components/         # Componentes React
│   │   ├── Header.tsx
│   │   ├── Breadcrumb.tsx
│   │   ├── SearchBar.tsx
│   │   ├── FileList.tsx
│   │   ├── UploadModal.tsx
│   │   ├── CreateFolderModal.tsx
│   │   └── RenameModal.tsx
│   ├── api.ts             # Cliente API
│   ├── types.ts           # Tipos TypeScript
│   ├── App.tsx            # Componente principal
│   ├── App.css            # Estilos principales
│   ├── main.tsx           # Entry point
│   └── index.css          # Estilos globales
├── public/                # Assets estáticos
├── index.html            # HTML template
├── vite.config.ts        # Configuración Vite
├── tsconfig.json         # Configuración TypeScript
├── package.json          # Dependencias
├── Dockerfile            # Imagen Docker
└── nginx.conf            # Configuración Nginx
```

## 🎨 Características de UI

### Breadcrumb Navigation
Navegación por rutas con breadcrumbs interactivos.

### Búsqueda Avanzada
- Búsqueda por nombre de archivo
- Filtro por extensión
- Filtro por tamaño mínimo/máximo

### Gestión de Archivos
- Vista de lista con información detallada
- Iconos diferenciados para archivos y carpetas
- Acciones rápidas (descargar, renombrar, eliminar)

### Modales
- Modal de subida con drag & drop
- Modal de creación de carpetas
- Modal de renombrado

## 🔧 Configuración

### Variables de Entorno

Crea un archivo `.env` en la raíz del frontend:

```env
VITE_API_URL=http://localhost:8000
```

### Proxy de Desarrollo

El proxy está configurado en `vite.config.ts` para redirigir `/api` al backend.

## 📱 Responsive Design

El frontend está optimizado para:
- Desktop (1400px+)
- Tablet (768px - 1024px)
- Mobile (< 768px)

## 🎯 Próximas Mejoras

- [ ] Vista de cuadrícula (grid view)
- [ ] Previsualización de imágenes
- [ ] Subida múltiple de archivos
- [ ] Progreso de subida/descarga
- [ ] Ordenamiento de columnas
- [ ] Selección múltiple
- [ ] Copiar/pegar archivos
- [ ] Historial de navegación
- [ ] Favoritos/marcadores
- [ ] Tema oscuro

## 📄 Licencia

MIT

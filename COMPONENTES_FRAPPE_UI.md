# Portal RRHH - Componentes Frappe UI Implementados

Este documento describe todos los componentes de Frappe UI implementados en el Portal RRHH, basado en la documentación oficial de [https://ui.frappe.io/](https://ui.frappe.io/).

## 🎨 Componentes Implementados

### 1. **Button (Botones)**
- **Variantes**: primary, secondary, outline, ghost, danger
- **Tamaños**: xs, sm, md, lg, xl
- **Estados**: normal, disabled, loading
- **Iconos**: Soporte para iconos FontAwesome
- **Uso**: Acciones principales, secundarias, cancelar, eliminar

### 2. **Card (Tarjetas)**
- **Variantes**: default, elevated, outlined
- **Secciones**: header, content, footer
- **Uso**: Contenedores de información, estadísticas, formularios

### 3. **Input (Campos de Entrada)**
- **Tipos**: text, email, password, number, tel, date
- **Tamaños**: sm, md, lg
- **Estados**: normal, error, disabled
- **Características**: labels, placeholders, validación, mensajes de ayuda/error

### 4. **Table (Tablas)**
- **Características**: Responsive, hover effects, sorting
- **Columnas**: Configurables con slots personalizados
- **Uso**: Listados de empleados, vacantes, solicitudes

### 5. **Dialog (Diálogos/Modales)**
- **Características**: Overlay, animaciones, teletransporte
- **Secciones**: header, content, footer
- **Uso**: Formularios de creación/edición, confirmaciones

### 6. **Badge (Insignias)**
- **Variantes**: default, primary, success, warning, error, info
- **Tamaños**: sm, md, lg
- **Uso**: Estados, categorías, etiquetas

### 7. **Alert (Alertas)**
- **Variantes**: success, warning, error, info
- **Características**: Iconos automáticos, títulos opcionales
- **Uso**: Notificaciones, mensajes de estado

### 8. **Progress (Barras de Progreso)**
- **Variantes**: primary, success, warning, error
- **Características**: Porcentajes, labels, animaciones
- **Uso**: Progreso de tareas, estadísticas

### 9. **Avatar (Avatares)**
- **Tamaños**: xs, sm, md, lg, xl
- **Características**: Imágenes o iconos por defecto
- **Uso**: Perfiles de empleados, usuarios

### 10. **Dropdown (Menús Desplegables)**
- **Alineación**: left, right
- **Características**: Trigger personalizable, cierre automático
- **Uso**: Menús de acciones, filtros

### 11. **Toast (Notificaciones)**
- **Variantes**: success, warning, error, info
- **Características**: Auto-dismiss, animaciones, posicionamiento
- **Uso**: Feedback de acciones, confirmaciones

## 🏗️ Estructura de Archivos

```
portal_rrhh/
├── templates/
│   └── pages/
│       ├── portal_rrhh.html      # Dashboard principal
│       ├── empleados.html        # Gestión de empleados
│       ├── vacantes.html         # Gestión de vacantes
│       ├── solicitudes.html      # Solicitudes (pendiente)
│       ├── evaluaciones.html     # Evaluaciones (pendiente)
│       └── reportes.html         # Reportes (pendiente)
├── public/
│   ├── frappe-ui-components.js   # Biblioteca de componentes
│   └── tailwind.config.js        # Configuración de Tailwind
└── hooks.py                      # Configuración de rutas
```

## 🎯 Páginas Implementadas

### 1. **Dashboard Principal** (`portal_rrhh.html`)
- **Componentes**: Sidebar, Cards, Stats, Buttons
- **Características**:
  - Sidebar con navegación completa
  - Tarjetas de estadísticas
  - Lista de actividades recientes
  - Acciones rápidas

### 2. **Gestión de Empleados** (`empleados.html`)
- **Componentes**: Table, Dialog, Input, Badge, Avatar, Button
- **Características**:
  - Tabla completa de empleados con filtros
  - Formulario de creación/edición
  - Estados visuales (activo, inactivo, en licencia)
  - Búsqueda y filtros avanzados

### 3. **Gestión de Vacantes** (`vacantes.html`)
- **Componentes**: Card, Dialog, Input, Badge, Button, Grid
- **Características**:
  - Vista de tarjetas para vacantes
  - Formulario completo de creación
  - Estados de vacantes (activa, pausada, cerrada)
  - Filtros por departamento y estado

## 🎨 Tema y Estilos

### Colores Principales
- **Primary**: Verde (#2e7d32) - Color principal de la marca
- **Secondary**: Gris (#f5f5f5) - Color secundario
- **Success**: Verde (#4caf50) - Estados exitosos
- **Warning**: Amarillo (#ffc107) - Advertencias
- **Error**: Rojo (#f44336) - Errores
- **Info**: Azul (#2196f3) - Información

### Tipografía
- **Fuente Principal**: Inter (sistema de fuentes)
- **Pesos**: 400 (normal), 500 (medium), 600 (semibold), 700 (bold)

### Espaciado
- **Sistema**: Basado en múltiplos de 4px
- **Breakpoints**: sm (640px), md (768px), lg (1024px), xl (1280px)

## 🚀 Funcionalidades Implementadas

### Dashboard
- ✅ Sidebar de navegación con iconos
- ✅ Tarjetas de estadísticas
- ✅ Lista de actividades recientes
- ✅ Acciones rápidas

### Empleados
- ✅ Lista completa de empleados
- ✅ Filtros por departamento y estado
- ✅ Búsqueda por nombre, email, departamento
- ✅ Formulario de creación de empleados
- ✅ Acciones de ver, editar, eliminar
- ✅ Estados visuales con badges

### Vacantes
- ✅ Vista de tarjetas para vacantes
- ✅ Filtros por departamento y estado
- ✅ Búsqueda por título y departamento
- ✅ Formulario completo de creación
- ✅ Acciones de gestión (pausar/activar, editar, eliminar)
- ✅ Información detallada de cada vacante

## 📱 Responsive Design

Todas las páginas están optimizadas para:
- **Desktop**: Layout completo con sidebar fijo
- **Tablet**: Sidebar colapsable, grid adaptativo
- **Mobile**: Sidebar overlay, stack vertical

## 🔧 Configuración Técnica

### Dependencias
- **Vue.js 3**: Framework principal
- **Tailwind CSS**: Sistema de estilos
- **FontAwesome**: Iconografía
- **Frappe UI**: Componentes base

### Configuración de Tailwind
```javascript
// tailwind.config.js
module.exports = {
  content: ["./templates/**/*.html", "./www/**/*.html"],
  theme: {
    extend: {
      colors: {
        primary: { /* Paleta de verdes */ },
        secondary: { /* Paleta de grises */ },
        // ... más colores personalizados
      }
    }
  }
}
```

## 🎯 Próximos Pasos

### Componentes Pendientes
- [ ] **Navigation**: Navbar, Breadcrumb
- [ ] **Layout**: Container, Grid, Flex
- [ ] **Feedback**: Spinner, Skeleton
- [ ] **Overlay**: Tooltip, Popover
- [ ] **Data Display**: List, Timeline, Stats
- [ ] **Controls**: Checkbox, Radio, Switch, Select
- [ ] **Date Time**: DatePicker, TimePicker
- [ ] **Advanced**: FileUploader, RichText

### Páginas Pendientes
- [ ] **Solicitudes**: Gestión de solicitudes de empleo
- [ ] **Evaluaciones**: Sistema de evaluaciones de desempeño
- [ ] **Reportes**: Dashboard de reportes y analytics

## 📚 Documentación de Referencia

- [Frappe UI Official Documentation](https://ui.frappe.io/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Vue.js 3 Documentation](https://vuejs.org/guide/)
- [FontAwesome Icons](https://fontawesome.com/icons)

## 🤝 Contribución

Para agregar nuevos componentes o funcionalidades:

1. Implementar el componente en `frappe-ui-components.js`
2. Crear la página correspondiente en `templates/pages/`
3. Actualizar las rutas en `hooks.py`
4. Documentar en este archivo

---

**Portal RRHH** - Desarrollado con ❤️ usando Frappe UI

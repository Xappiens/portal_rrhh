# 🚀 Instrucciones de Build - Portal RRHH

## Proceso de Desarrollo

Cada vez que hagas cambios en el frontend, necesitas seguir estos pasos:

### 1. Script Completo (Recomendado)
```bash
cd /home/frappe/frappe-bench/apps/portal_rrhh
./build_and_update.sh
```

### 2. Script Rápido
```bash
cd /home/frappe/frappe-bench/apps/portal_rrhh
./quick_build.sh
```

### 3. Proceso Manual
```bash
# 1. Compilar frontend
cd /home/frappe/frappe-bench/apps/portal_rrhh/frontend
yarn build

# 2. Actualizar rutas en HTML
cd /home/frappe/frappe-bench/apps/portal_rrhh
./build_and_update.sh
```

## ¿Qué hace cada script?

### `build_and_update.sh`
- ✅ Ejecuta `yarn build` en el frontend
- ✅ Busca automáticamente los archivos compilados
- ✅ Actualiza las rutas en `portal_rrhh.html`
- ✅ Crea backup del HTML original
- ✅ Limpia cache de Frappe (`bench clear-cache`)
- ✅ Limpia cache del sitio web (`bench clear-website-cache`)
- ✅ Muestra las rutas actualizadas

### `quick_build.sh`
- ⚡ Versión simplificada que ejecuta todo en una línea
- ⚡ Menos output, más rápido

## Archivos que se actualizan automáticamente

- `portal_rrhh.html` - Rutas de JS y CSS
- Se crea backup en `portal_rrhh.html.backup`

## Archivos compilados

Los archivos se generan en:
- `portal_rrhh/public/frontend/assets/`

Y se referencian en:
- `portal_rrhh/www/portal_rrhh.html`

## Comandos de Cache Incluidos

El script automáticamente ejecuta:

```bash
# Limpiar cache de Frappe
bench clear-cache

# Limpiar cache del sitio web
bench clear-website-cache
```

Esto asegura que:
- 🧹 **Cache de Frappe se limpia** - Para que los cambios en Python/APIs se reflejen
- 🌐 **Cache del sitio web se limpia** - Para que los cambios en frontend se vean inmediatamente
- ⚡ **No necesitas limpiar cache manualmente** - Todo está automatizado

## Notas Importantes

- 🔄 **Siempre ejecuta el build después de cambios en el frontend**
- 📁 **Los archivos compilados tienen hash en el nombre** (ej: `index.b203adf1.js`)
- 🔧 **El script actualiza automáticamente las rutas** en el HTML
- 💾 **Se crea backup automático** del HTML original
- 🧹 **Cache se limpia automáticamente** - No necesitas hacerlo manualmente

#!/bin/bash

# Script mejorado para compilar el frontend y actualizar las rutas automáticamente
# Uso: ./build.sh

set -e  # Salir si hay algún error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRONTEND_DIR="$SCRIPT_DIR/frontend"
PORTAL_DIR="$SCRIPT_DIR/portal_rrhh"
BENCH_DIR="$(dirname "$SCRIPT_DIR")"

echo "🚀 Iniciando proceso de build y actualización..."
echo "📁 Directorio de trabajo: $SCRIPT_DIR"

# Paso 1: Build del frontend
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📦 Paso 1: Compilando frontend..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

cd "$FRONTEND_DIR"

# Detectar si usar npm o yarn
if command -v npm &> /dev/null; then
    echo "📦 Usando npm..."
    npm run build
elif command -v yarn &> /dev/null; then
    echo "📦 Usando yarn..."
    yarn build
else
    echo "❌ Error: No se encontró npm ni yarn"
    exit 1
fi

if [ $? -ne 0 ]; then
    echo "❌ Error en el build del frontend"
    exit 1
fi

echo "✅ Build del frontend completado"

# Paso 2: Buscar archivos compilados
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 Paso 2: Buscando archivos compilados..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

cd "$PORTAL_DIR"

ASSETS_DIR="public/frontend/assets"

if [ ! -d "$ASSETS_DIR" ]; then
    echo "❌ Error: No se encontró el directorio $ASSETS_DIR"
    exit 1
fi

# Buscar archivos JS y CSS principales
INDEX_JS=$(find "$ASSETS_DIR" -name "index.*.js" -type f | head -1 | xargs basename)
VENDOR_JS=$(find "$ASSETS_DIR" -name "vendor.*.js" -type f | head -1 | xargs basename)
VENDOR_CSS=$(find "$ASSETS_DIR" -name "vendor.*.css" -type f | head -1 | xargs basename)
INDEX_CSS=$(find "$ASSETS_DIR" -name "index.*.css" -type f | head -1 | xargs basename)

echo "📄 Archivos encontrados:"
echo "  ✓ JS Principal:   $INDEX_JS"
echo "  ✓ JS Vendor:      $VENDOR_JS"
echo "  ✓ CSS Vendor:     $VENDOR_CSS"
echo "  ✓ CSS Principal:  $INDEX_CSS"

# Verificar que los archivos existen
if [ -z "$INDEX_JS" ] || [ -z "$VENDOR_JS" ] || [ -z "$VENDOR_CSS" ] || [ -z "$INDEX_CSS" ]; then
    echo "❌ Error: No se encontraron todos los archivos necesarios"
    exit 1
fi

# Paso 3: Actualizar HTML
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔄 Paso 3: Actualizando referencias en HTML..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

HTML_FILE="www/portal_rrhh.html"

if [ ! -f "$HTML_FILE" ]; then
    echo "❌ Error: No se encontró el archivo $HTML_FILE"
    exit 1
fi

# Crear backup del archivo original
BACKUP_FILE="${HTML_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
cp "$HTML_FILE" "$BACKUP_FILE"
echo "💾 Backup creado: $(basename "$BACKUP_FILE")"

# Actualizar las rutas en el HTML
sed -i "s|src=\"/assets/portal_rrhh/frontend/assets/index\.[a-f0-9]*\.js\"|src=\"/assets/portal_rrhh/frontend/assets/$INDEX_JS\"|g" "$HTML_FILE"
sed -i "s|href=\"/assets/portal_rrhh/frontend/assets/vendor\.[a-f0-9]*\.js\"|href=\"/assets/portal_rrhh/frontend/assets/$VENDOR_JS\"|g" "$HTML_FILE"
sed -i "s|href=\"/assets/portal_rrhh/frontend/assets/vendor\.[a-f0-9]*\.css\"|href=\"/assets/portal_rrhh/frontend/assets/$VENDOR_CSS\"|g" "$HTML_FILE"
sed -i "s|href=\"/assets/portal_rrhh/frontend/assets/index\.[a-f0-9]*\.css\"|href=\"/assets/portal_rrhh/frontend/assets/$INDEX_CSS\"|g" "$HTML_FILE"

echo "✅ Referencias actualizadas en portal_rrhh.html"

# Paso 4: Limpiar caché
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧹 Paso 4: Limpiando caché..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

cd "$BENCH_DIR"

if command -v bench &> /dev/null; then
    echo "🧹 Limpiando cache de Frappe..."
    bench clear-cache || echo "⚠️  Advertencia: Error al limpiar cache de Frappe"
    
    echo "🌐 Limpiando cache del sitio web..."
    bench clear-website-cache || echo "⚠️  Advertencia: Error al limpiar cache del sitio web"
    
    echo "✅ Caché limpiada"
else
    echo "⚠️  Advertencia: Comando 'bench' no encontrado, saltando limpieza de caché"
fi

# Resumen final
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 ¡Proceso completado exitosamente!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📋 Rutas actualizadas en portal_rrhh.html:"
grep -E "(src=|href=).*frontend/assets" "$PORTAL_DIR/$HTML_FILE" | sed 's/^/  /'
echo ""
echo "💡 Tip: Si no ves los cambios, haz un hard refresh en el navegador (Ctrl+Shift+R)"


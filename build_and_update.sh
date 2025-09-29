#!/bin/bash

# Script para compilar el frontend y actualizar las rutas en el HTML
# Uso: ./build_and_update.sh

echo "🚀 Iniciando proceso de build y actualización..."

# Cambiar al directorio del frontend
cd /home/frappe/frappe-bench/apps/portal_rrhh/frontend

echo "📦 Ejecutando yarn build..."
yarn build

if [ $? -eq 0 ]; then
    echo "✅ Build completado exitosamente"
else
    echo "❌ Error en el build"
    exit 1
fi

# Cambiar al directorio del portal
cd /home/frappe/frappe-bench/apps/portal_rrhh/portal_rrhh

echo "🔍 Buscando archivos compilados..."

# Buscar archivos JS y CSS principales
INDEX_JS=$(find public/frontend/assets -name "index.*.js" | head -1 | xargs basename)
VENDOR_JS=$(find public/frontend/assets -name "vendor.*.js" | head -1 | xargs basename)
VENDOR_CSS=$(find public/frontend/assets -name "vendor.*.css" | head -1 | xargs basename)
INDEX_CSS=$(find public/frontend/assets -name "index.*.css" | head -1 | xargs basename)

echo "📄 Archivos encontrados:"
echo "  - JS Principal: $INDEX_JS"
echo "  - JS Vendor: $VENDOR_JS"
echo "  - CSS Vendor: $VENDOR_CSS"
echo "  - CSS Principal: $INDEX_CSS"

# Actualizar el archivo HTML
echo "🔄 Actualizando portal_rrhh.html..."

# Crear backup del archivo original
cp www/portal_rrhh.html www/portal_rrhh.html.backup

# Actualizar las rutas en el HTML
sed -i "s|src=\"/assets/portal_rrhh/frontend/assets/index\.[a-f0-9]*\.js\"|src=\"/assets/portal_rrhh/frontend/assets/$INDEX_JS\"|g" www/portal_rrhh.html
sed -i "s|href=\"/assets/portal_rrhh/frontend/assets/vendor\.[a-f0-9]*\.js\"|href=\"/assets/portal_rrhh/frontend/assets/$VENDOR_JS\"|g" www/portal_rrhh.html
sed -i "s|href=\"/assets/portal_rrhh/frontend/assets/vendor\.[a-f0-9]*\.css\"|href=\"/assets/portal_rrhh/frontend/assets/$VENDOR_CSS\"|g" www/portal_rrhh.html
sed -i "s|href=\"/assets/portal_rrhh/frontend/assets/index\.[a-f0-9]*\.css\"|href=\"/assets/portal_rrhh/frontend/assets/$INDEX_CSS\"|g" www/portal_rrhh.html

echo "✅ HTML actualizado exitosamente"

# Limpiar cache de Frappe
echo "🧹 Limpiando cache de Frappe..."
cd /home/frappe/frappe-bench
bench clear-cache

if [ $? -eq 0 ]; then
    echo "✅ Cache de Frappe limpiado"
else
    echo "⚠️  Error al limpiar cache de Frappe"
fi

# Limpiar cache del sitio web
echo "🌐 Limpiando cache del sitio web..."
bench clear-website-cache

if [ $? -eq 0 ]; then
    echo "✅ Cache del sitio web limpiado"
else
    echo "⚠️  Error al limpiar cache del sitio web"
fi

echo "🎉 Proceso completado!"

# Mostrar las rutas actualizadas
echo ""
echo "📋 Rutas actualizadas en portal_rrhh.html:"
grep -E "(src=|href=).*frontend/assets" /home/frappe/frappe-bench/apps/portal_rrhh/portal_rrhh/www/portal_rrhh.html

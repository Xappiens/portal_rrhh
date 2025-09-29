#!/bin/bash

# Script rápido para build y actualización
# Uso: ./quick_build.sh

echo "⚡ Build rápido iniciado..."

cd /home/frappe/frappe-bench/apps/portal_rrhh/frontend && yarn build && cd /home/frappe/frappe-bench/apps/portal_rrhh && ./build_and_update.sh

echo "✅ Listo!"

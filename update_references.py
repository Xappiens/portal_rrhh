#!/usr/bin/env python3
"""
Script para actualizar referencias en portal_rrhh.html después del build
Se ejecuta automáticamente desde package.json
"""
import os
import re

def update_html_references():
	"""
	Actualiza las referencias en portal_rrhh.html después del build
	"""
	current_dir = os.path.dirname(os.path.abspath(__file__))
	portal_dir = os.path.join(current_dir, "portal_rrhh")
	html_file = os.path.join(portal_dir, "www", "portal_rrhh.html")
	assets_dir = os.path.join(portal_dir, "public", "frontend", "assets")
	
	# Buscar archivos compilados
	print("\n🔍 Buscando archivos compilados...")
	
	if not os.path.exists(assets_dir):
		print(f"⚠️  Directorio {assets_dir} no existe, saltando actualización de referencias")
		return
	
	# Buscar archivos con hash
	index_js = None
	vendor_js = None
	vendor_css = None
	index_css = None
	
	for file in os.listdir(assets_dir):
		if file.startswith("index.") and file.endswith(".js"):
			index_js = file
		elif file.startswith("vendor.") and file.endswith(".js"):
			vendor_js = file
		elif file.startswith("vendor.") and file.endswith(".css"):
			vendor_css = file
		elif file.startswith("index.") and file.endswith(".css"):
			index_css = file
	
	if not all([index_js, vendor_js, vendor_css, index_css]):
		print("⚠️  No se encontraron todos los archivos necesarios:")
		print(f"  - index.js: {index_js}")
		print(f"  - vendor.js: {vendor_js}")
		print(f"  - vendor.css: {vendor_css}")
		print(f"  - index.css: {index_css}")
		print("Saltando actualización de referencias")
		return
	
	print(f"📄 Archivos encontrados:")
	print(f"  ✓ JS Principal:   {index_js}")
	print(f"  ✓ JS Vendor:      {vendor_js}")
	print(f"  ✓ CSS Vendor:     {vendor_css}")
	print(f"  ✓ CSS Principal:  {index_css}")
	
	# Actualizar referencias en HTML
	if not os.path.exists(html_file):
		print(f"⚠️  Archivo {html_file} no existe, saltando actualización")
		return
	
	print("\n🔄 Actualizando referencias en portal_rrhh.html...")
	
	with open(html_file, 'r', encoding='utf-8') as f:
		content = f.read()
	
	# Actualizar referencias usando regex
	content = re.sub(
		r'src="/assets/portal_rrhh/frontend/assets/index\.[a-f0-9]+\.js"',
		f'src="/assets/portal_rrhh/frontend/assets/{index_js}"',
		content
	)
	content = re.sub(
		r'href="/assets/portal_rrhh/frontend/assets/vendor\.[a-f0-9]+\.js"',
		f'href="/assets/portal_rrhh/frontend/assets/{vendor_js}"',
		content
	)
	content = re.sub(
		r'href="/assets/portal_rrhh/frontend/assets/vendor\.[a-f0-9]+\.css"',
		f'href="/assets/portal_rrhh/frontend/assets/{vendor_css}"',
		content
	)
	content = re.sub(
		r'href="/assets/portal_rrhh/frontend/assets/index\.[a-f0-9]+\.css"',
		f'href="/assets/portal_rrhh/frontend/assets/{index_css}"',
		content
	)
	
	with open(html_file, 'w', encoding='utf-8') as f:
		f.write(content)
	
	print("✅ Referencias actualizadas en portal_rrhh.html")
	print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

if __name__ == "__main__":
    update_html_references()

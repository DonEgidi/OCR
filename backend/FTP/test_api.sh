#!/bin/bash

# Script de prueba para la API FTP
# Ejecutar: bash test_api.sh

API_URL="http://localhost:8000"
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== Test de API FTP ===${NC}\n"

# 1. Health Check
echo -e "${YELLOW}1. Health Check${NC}"
response=$(curl -s "${API_URL}/health")
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ API está funcionando${NC}"
    echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
else
    echo -e "${RED}✗ Error: API no responde${NC}"
    exit 1
fi
echo ""

# 2. Crear archivo de prueba
echo -e "${YELLOW}2. Creando archivo de prueba${NC}"
echo "Este es un archivo de prueba - $(date)" > test_file.txt
echo -e "${GREEN}✓ Archivo test_file.txt creado${NC}"
echo ""

# 3. Crear directorio
echo -e "${YELLOW}3. Creando directorio /test_dir${NC}"
response=$(curl -s -X POST "${API_URL}/files/mkdir" \
  -H "Content-Type: application/json" \
  -d '{"directory_path": "/test_dir"}')
echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
echo ""

# 4. Subir archivo
echo -e "${YELLOW}4. Subiendo archivo a /test_dir${NC}"
response=$(curl -s -X POST "${API_URL}/files/upload?destination_path=/test_dir" \
  -F "file=@test_file.txt")
echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
echo ""

# 5. Listar archivos
echo -e "${YELLOW}5. Listando archivos en /test_dir${NC}"
response=$(curl -s "${API_URL}/files/list?path=/test_dir")
echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
echo ""

# 6. Obtener info del archivo
echo -e "${YELLOW}6. Obteniendo información del archivo${NC}"
response=$(curl -s "${API_URL}/files/info?file_path=/test_dir/test_file.txt")
echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
echo ""

# 7. Descargar archivo
echo -e "${YELLOW}7. Descargando archivo${NC}"
curl -s "${API_URL}/files/download?file_path=/test_dir/test_file.txt" \
  -o test_file_downloaded.txt
if [ -f test_file_downloaded.txt ]; then
    echo -e "${GREEN}✓ Archivo descargado exitosamente${NC}"
    echo "Contenido:"
    cat test_file_downloaded.txt
else
    echo -e "${RED}✗ Error al descargar archivo${NC}"
fi
echo ""

# 8. Renombrar archivo
echo -e "${YELLOW}8. Renombrando archivo${NC}"
response=$(curl -s -X POST "${API_URL}/files/rename" \
  -H "Content-Type: application/json" \
  -d '{
    "old_path": "/test_dir/test_file.txt",
    "new_path": "/test_dir/test_file_renamed.txt"
  }')
echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
echo ""

# 9. Mover archivo
echo -e "${YELLOW}9. Moviendo archivo a raíz${NC}"
response=$(curl -s -X POST "${API_URL}/files/move" \
  -H "Content-Type: application/json" \
  -d '{
    "source_path": "/test_dir/test_file_renamed.txt",
    "destination_path": "/test_file_renamed.txt"
  }')
echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
echo ""

# 10. Listar archivos en raíz
echo -e "${YELLOW}10. Listando archivos en raíz${NC}"
response=$(curl -s "${API_URL}/files/list?path=/")
echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
echo ""

# 11. Eliminar archivo
echo -e "${YELLOW}11. Eliminando archivo${NC}"
response=$(curl -s -X DELETE "${API_URL}/files/delete?file_path=/test_file_renamed.txt")
echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
echo ""

# 12. Eliminar directorio
echo -e "${YELLOW}12. Eliminando directorio${NC}"
response=$(curl -s -X DELETE "${API_URL}/files/delete?file_path=/test_dir")
echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
echo ""

# Limpiar archivos locales
rm -f test_file.txt test_file_downloaded.txt

echo -e "${GREEN}=== Test completado exitosamente ===${NC}"
echo -e "\nPara más información, visita: ${YELLOW}http://localhost:8000/docs${NC}"

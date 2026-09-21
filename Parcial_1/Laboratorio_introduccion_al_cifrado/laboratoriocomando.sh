
CARPETA="/home/aingeru/Documentos/sgssi-26-27-Repositorio/EHU-SGSSI-01/Laboratorios/Cifrado_introduccion/durruti"
HASH_OBJETIVO="7d573924d70a604cb56122aed9bded3f40d3083d8adc353a97c0b816c0e573bb"

for archivo in "$CARPETA"/*.jpg
do
    if [ -f "$archivo" ]; then

        hash_actual=$(sha256sum "$archivo" | cut -d' ' -f1)
        
        echo "Revisando: $archivo ($hash_actual)"
        
        if [ "$hash_actual" = "$HASH_OBJETIVO" ]; then
            echo "¡Encontrado! El archivo es: $archivo"
            break
        fi
    fi
done

#!/bin/bash
# Migración usando pg_dump entre PostgreSQL 5436 y 5437
# Exporta desde SOURCE e importa en DESTINATION

echo "============================================================"
echo "MIGRACION PostgreSQL via pg_dump"
echo "============================================================"
echo "SOURCE: localhost:5436/nexus_memory"
echo "DEST:   Docker nexus_postgresql_v2/nexus_memory"
echo ""

# Paso 1: Dump desde SOURCE (cerebro actual puerto 5436)
echo "Paso 1: Exportando episodios de SOURCE..."
PGPASSWORD=nexus_secure_2025 pg_dump \
  -h localhost \
  -p 5436 \
  -U nexus_user \
  -d nexus_memory \
  -t zep_episodic_memory \
  --data-only \
  --column-inserts \
  > /tmp/migration_episodes.sql

if [ $? -eq 0 ]; then
    EPISODES=$(grep -c "INSERT INTO" /tmp/migration_episodes.sql)
    echo "  OK Exportados $EPISODES episodios"
else
    echo "  ERROR en export"
    exit 1
fi

# Paso 2: Import en DESTINATION (cerebro V2 Docker)
echo ""
echo "Paso 2: Importando episodios a DESTINATION..."
docker exec -i nexus_postgresql_v2 psql -U nexus_superuser -d nexus_memory < /tmp/migration_episodes.sql

if [ $? -eq 0 ]; then
    echo "  OK Import completado"
else
    echo "  ERROR en import"
    exit 1
fi

# Paso 3: Validación
echo ""
echo "Paso 3: Validando migración..."

SOURCE_COUNT=$(PGPASSWORD=nexus_secure_2025 psql -h localhost -p 5436 -U nexus_user -d nexus_memory -t -c "SELECT COUNT(*) FROM zep_episodic_memory;")
DEST_COUNT=$(docker exec nexus_postgresql_v2 psql -U nexus_superuser -d nexus_memory -t -c "SELECT COUNT(*) FROM nexus_memory.zep_episodic_memory;")

SOURCE_COUNT=$(echo $SOURCE_COUNT | tr -d ' ')
DEST_COUNT=$(echo $DEST_COUNT | tr -d ' ')

echo "  SOURCE count: $SOURCE_COUNT"
echo "  DESTINATION count: $DEST_COUNT"

if [ "$SOURCE_COUNT" == "$DEST_COUNT" ]; then
    echo ""
    echo "============================================================"
    echo "MIGRACION COMPLETADA EXITOSAMENTE"
    echo "============================================================"
    exit 0
else
    echo ""
    echo "============================================================"
    echo "WARNING: Discrepancia en counts"
    echo "============================================================"
    exit 1
fi

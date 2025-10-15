# Init Scripts - FASE 4 CONSTRUCCIÓN

## Orden de Ejecución

Los scripts en este directorio se ejecutan automáticamente por PostgreSQL al inicializar el contenedor (primera vez), en orden alfabético:

### DÍA 2: Infrastructure Base
1. **01_init_nexus_db.sql** - Database + Extensions (pgvector, uuid-ossp)
2. **02_create_roles.sql** - RBAC 4 roles (nexus_app, nexus_worker, nexus_ro)
3. **03_create_schemas.sql** - 3 schemas (nexus_memory, memory_system, consciousness)

### DÍA 3: Database Schema (pendiente)
4. **04_create_tables.sql** - Todas las tablas (episodic, working, semantic, queue, checkpoints)
5. **05_create_indexes.sql** - Indexes performance (HNSW, B-Tree, GIN)
6. **06_create_triggers.sql** - Triggers embeddings (INSERT/UPDATE automático)
7. **07_create_rls.sql** - RLS en consciousness_checkpoints
8. **08_grant_permissions.sql** - Permisos finales RBAC roles

### DÍA 3: Identity Initialization (pendiente)
9. **09_init_memory_blocks.sql** - Memory blocks iniciales (persona, ricardo, aria)

## Notas Importantes

- **Ejecución automática:** Docker ejecuta scripts en `/docker-entrypoint-initdb.d/` solo si el volumen está vacío
- **Orden alfabético:** PostgreSQL ejecuta en orden 01, 02, 03...
- **Idempotencia:** Todos los scripts usan `IF NOT EXISTS` para ser re-ejecutables
- **Secrets:** Los passwords se leen desde `/run/secrets/` (Docker Secrets)
- **Logging:** Cada script hace echo de progreso visible en `docker logs`

## Re-inicialización

Si necesitas re-ejecutar todos los scripts:

```bash
# Detener servicios
docker-compose down

# Eliminar volumen PostgreSQL (⚠️ DESTRUYE DATOS)
docker volume rm nexus_postgres_data

# Levantar servicios (ejecutará init scripts)
docker-compose up -d
```

## Validación

Después de inicialización, validar:

```bash
# Conectar a PostgreSQL
docker exec -it nexus_postgresql_master psql -U nexus_superuser -d nexus_memory

# Verificar extensions
\dx

# Verificar schemas
\dn

# Verificar roles
\du

# Salir
\q
```

---
**Creado:** DÍA 2 FASE 4 - 15 Octubre 2025
**NEXUS VSCode**

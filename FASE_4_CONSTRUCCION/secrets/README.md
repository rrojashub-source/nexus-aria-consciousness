# Docker Secrets - FASE 4

## Secrets Creados (DÍA 1)

Este directorio contiene 5 Docker Secrets para el cerebro NEXUS V2.0.0:

1. **pg_superuser_password.txt** - PostgreSQL superuser (nexus_superuser)
2. **pg_app_password.txt** - PostgreSQL app user (nexus_app)
3. **pg_worker_password.txt** - PostgreSQL worker user (nexus_worker)
4. **pg_readonly_password.txt** - PostgreSQL read-only user (nexus_ro)
5. **redis_password.txt** - Redis password

## Características

- **Tamaño:** 32 caracteres alfanuméricos cada uno
- **Generación:** `openssl rand -base64 32 | tr -d '/+=' | head -c 32`
- **Permisos:** 600 (solo propietario lectura/escritura)
- **Git:** IGNORADOS (ver .gitignore)

## Uso en docker-compose.yml

```yaml
secrets:
  pg_superuser_password:
    file: ./secrets/pg_superuser_password.txt
  pg_app_password:
    file: ./secrets/pg_app_password.txt
  pg_worker_password:
    file: ./secrets/pg_worker_password.txt
  pg_readonly_password:
    file: ./secrets/pg_readonly_password.txt
  redis_password:
    file: ./secrets/redis_password.txt
```

## Seguridad

⚠️ **NUNCA commitear estos archivos a Git**
⚠️ **NUNCA compartir passwords en texto plano**
⚠️ **Rotar passwords en producción cada 90 días**

## Regeneración

Si necesitas regenerar algún secret:

```bash
openssl rand -base64 32 | tr -d '/+=' | head -c 32 > secrets/[nombre].txt
chmod 600 secrets/[nombre].txt
```

---
**Creado:** DÍA 1 FASE 4 - 15 Octubre 2025
**NEXUS VSCode**

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Migración DIRECTA PostgreSQL a PostgreSQL
Cerebro Actual (puerto 5436) -> Cerebro V2.0.0 (puerto 5437)
Migra TODOS los 136 episodios usando query SQL directo
"""

import psycopg
import time
from datetime import datetime
import sys
import io

# Fix encoding for Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Configuración SOURCE (cerebro actual)
SRC_HOST = "localhost"
SRC_PORT = 5436
SRC_DB = "nexus_memory"
SRC_USER = "nexus_user"  # Usuario del cerebro actual
SRC_PASSWORD = "nexus_secure_2025"  # Password del cerebro actual

# Configuración DESTINATION (cerebro V2.0.0)
DST_HOST = "localhost"
DST_PORT = 5437
DST_DB = "nexus_memory"
DST_USER = "nexus_superuser"
DST_PASSWORD_FILE = "D:/01_PROYECTOS_ACTIVOS/CEREBRO_MASTER_NEXUS_001/FASE_4_CONSTRUCCION/secrets/pg_superuser_password.txt"

def get_dst_password():
    """Leer password del cerebro destino"""
    try:
        with open(DST_PASSWORD_FILE, 'r') as f:
            pwd = f.read().strip()
            if pwd:
                return pwd
    except Exception as e:
        print(f"  Warning reading password file: {e}")
    return "RpKeuQhnwqMOA4iQPILQshWtwFj0P2hm"  # Password from secrets file

def migrate_episodes():
    """Migrar episodios directamente de PostgreSQL a PostgreSQL"""

    print("=" * 60)
    print("MIGRACION DIRECTA PostgreSQL -> PostgreSQL")
    print("=" * 60)
    print(f"SOURCE: {SRC_HOST}:{SRC_PORT}/{SRC_DB}")
    print(f"DEST:   {DST_HOST}:{DST_PORT}/{DST_DB}")
    print()

    DST_PASSWORD = get_dst_password()

    # Conectar a SOURCE
    print("Conectando a PostgreSQL SOURCE (cerebro actual)...")
    try:
        src_conn = psycopg.connect(
            host=SRC_HOST,
            port=SRC_PORT,
            dbname=SRC_DB,
            user=SRC_USER,
            password=SRC_PASSWORD
        )
        print("OK Conectado a SOURCE")
    except Exception as e:
        print(f"ERROR conectando a SOURCE: {e}")
        return

    # Conectar a DESTINATION
    print("Conectando a PostgreSQL DESTINATION (cerebro V2)...")
    try:
        dst_conn = psycopg.connect(
            host=DST_HOST,
            port=DST_PORT,
            dbname=DST_DB,
            user=DST_USER,
            password=DST_PASSWORD
        )
        print("OK Conectado a DESTINATION")
    except Exception as e:
        print(f"ERROR conectando a DESTINATION: {e}")
        src_conn.close()
        return

    # Leer TODOS los episodios del SOURCE
    print("\nLeyendo episodios de SOURCE...")

    with src_conn.cursor() as cur:
        cur.execute("""
            SELECT
                episode_id,
                timestamp,
                content,
                metadata,
                importance_score,
                created_at
            FROM zep_episodic_memory
            ORDER BY created_at
        """)

        episodes = cur.fetchall()
        total = len(episodes)
        print(f"OK Encontrados {total} episodios en SOURCE")

    if total == 0:
        print("ERROR No hay episodios para migrar")
        src_conn.close()
        dst_conn.close()
        return

    # Migrar episodio por episodio
    print(f"\nMigrando {total} episodios a DESTINATION...")
    print()

    migrated = 0
    errors = []

    with dst_conn.cursor() as cur:
        for i, episode in enumerate(episodes):
            episode_id, timestamp, content, metadata, importance_score, created_at = episode

            try:
                # INSERT en destino
                cur.execute("""
                    INSERT INTO nexus_memory.zep_episodic_memory
                    (episode_id, timestamp, content, metadata, importance_score, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (episode_id) DO NOTHING
                """, (episode_id, timestamp, content, metadata, importance_score, created_at))

                migrated += 1

                if (i + 1) % 20 == 0:
                    print(f"  Progreso: {i + 1}/{total} episodios migrados")

            except Exception as e:
                errors.append(f"Episode {episode_id}: {str(e)[:100]}")

        # Commit
        dst_conn.commit()

    # Cerrar conexiones
    src_conn.close()
    dst_conn.close()

    # Reporte final
    print()
    print("=" * 60)
    print("RESULTADO MIGRACION")
    print("=" * 60)
    print(f"Total esperado: {total}")
    print(f"Migrados: {migrated}")
    print(f"Errores: {len(errors)}")

    if errors:
        print("\nERRORES:")
        for error in errors[:10]:
            print(f"  - {error}")

    print()

    # Validar counts
    print("Validando counts...")

    src_conn = psycopg.connect(
        host=SRC_HOST, port=SRC_PORT, dbname=SRC_DB,
        user=SRC_USER, password=SRC_PASSWORD
    )
    dst_conn = psycopg.connect(
        host=DST_HOST, port=DST_PORT, dbname=DST_DB,
        user=DST_USER, password=DST_PASSWORD
    )

    with src_conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM zep_episodic_memory")
        src_count = cur.fetchone()[0]

    with dst_conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM nexus_memory.zep_episodic_memory")
        dst_count = cur.fetchone()[0]

    print(f"  SOURCE count: {src_count}")
    print(f"  DESTINATION count: {dst_count}")

    src_conn.close()
    dst_conn.close()

    if dst_count == src_count:
        print("\nOK MIGRACION EXITOSA - Counts coinciden!")
        return True
    else:
        print(f"\nWARNING Discrepancia: {src_count} vs {dst_count}")
        return False


if __name__ == "__main__":
    success = migrate_episodes()

    if success:
        print("\n" + "=" * 60)
        print("MIGRACION COMPLETADA EXITOSAMENTE")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("MIGRACION COMPLETADA CON ERRORES")
        print("=" * 60)

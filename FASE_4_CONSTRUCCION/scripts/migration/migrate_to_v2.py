#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de migracion: Cerebro Actual (puerto 8002) -> Cerebro V2.0.0 (puerto 8003)
Migra episodios desde el API del cerebro actual al API del cerebro nuevo
"""

import requests
import json
import time
from datetime import datetime
import sys
import io

# Fix encoding for Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Configuración
SRC_API = "http://localhost:8002"
DST_API = "http://localhost:8003"
TIMEOUT = 30

def get_source_episodes():
    """Obtener episodios del cerebro actual via API"""
    print("Conectando al cerebro actual (puerto 8002)...")

    try:
        # Obtener episodios recientes
        response = requests.get(
            f"{SRC_API}/memory/episodic/recent?limit=1000",
            timeout=TIMEOUT
        )

        if response.status_code == 200:
            data = response.json()
            episodes = data.get("episodes", [])
            print(f"OK Encontrados {len(episodes)} episodios en cerebro actual")
            return episodes
        else:
            print(f"ERROR Endpoint no disponible (status {response.status_code})")
            return []

    except Exception as e:
        print(f"ERROR conectando a cerebro actual: {e}")
        return []


def migrate_episode(episode, index, total):
    """Migrar un episodio al cerebro nuevo"""
    try:
        # Preparar payload para el nuevo API
        # El cerebro actual tiene formato: id, timestamp, action_type, action_details, etc.
        # El nuevo API usa el formato MemoryActionRequest

        # Extraer campos del episodio actual
        episode_id = episode.get("id")
        action_type = episode.get("action_type", "migrated_episode")
        action_details_str = episode.get("action_details", "{}")
        context_state_str = episode.get("context_state", "{}")
        tags = episode.get("tags", [])
        importance_score = episode.get("importance_score", 0.5)
        timestamp = episode.get("timestamp")

        # Parse JSON strings
        try:
            action_details = json.loads(action_details_str) if isinstance(action_details_str, str) else action_details_str
        except:
            action_details = {"message": action_details_str}

        try:
            context_state = json.loads(context_state_str) if isinstance(context_state_str, str) else context_state_str
        except:
            context_state = {}

        # Agregar metadata de migración
        if not isinstance(action_details, dict):
            action_details = {"message": str(action_details)}

        action_details["original_id"] = str(episode_id)
        action_details["migrated_from"] = "cerebro_fase3"
        action_details["original_timestamp"] = timestamp

        # Construir payload para nuevo API
        payload = {
            "action_type": action_type,
            "action_details": action_details,
            "context_state": context_state,
            "tags": tags if isinstance(tags, list) else []
        }

        # POST al cerebro nuevo
        response = requests.post(
            f"{DST_API}/memory/action",
            json=payload,
            timeout=TIMEOUT
        )

        if response.status_code == 200:
            result = response.json()
            new_id = result.get("episode_id")

            if (index + 1) % 10 == 0:
                print(f"  ✅ Migrados: {index + 1}/{total}")

            return {"success": True, "old_id": episode_id, "new_id": new_id}
        else:
            error_msg = f"HTTP {response.status_code}: {response.text[:200]}"
            print(f"  ❌ Error en episodio {index + 1}: {error_msg}")
            return {"success": False, "old_id": episode_id, "error": error_msg}

    except Exception as e:
        error_msg = str(e)
        print(f"  ❌ Excepción en episodio {index + 1}: {error_msg}")
        return {"success": False, "old_id": episode.get("episode_id"), "error": error_msg}


def wait_for_embeddings(expected_count):
    """Esperar a que se generen todos los embeddings"""
    print(f"\n⏳ Esperando generación de embeddings ({expected_count} esperados)...")

    max_wait = 300  # 5 minutos máximo
    start_time = time.time()
    last_count = 0

    while time.time() - start_time < max_wait:
        try:
            response = requests.get(f"{DST_API}/stats", timeout=TIMEOUT)
            if response.status_code == 200:
                stats = response.json()["stats"]
                total = stats.get("total_episodes", 0)
                with_embeddings = stats.get("episodes_with_embeddings", 0)
                queue = stats.get("embeddings_queue", {})
                done = queue.get("done", 0)

                if with_embeddings != last_count:
                    print(f"  Progreso: {with_embeddings}/{expected_count} embeddings generados")
                    last_count = with_embeddings

                if with_embeddings >= expected_count and done >= expected_count:
                    print(f"✅ Todos los embeddings generados ({with_embeddings}/{expected_count})")
                    return True

            time.sleep(5)

        except Exception as e:
            print(f"  ⚠️  Error consultando stats: {e}")
            time.sleep(5)

    print(f"⚠️  Timeout esperando embeddings ({time.time() - start_time:.0f}s)")
    return False


def validate_migration():
    """Validar que la migración fue exitosa"""
    print("\n🔍 VALIDANDO MIGRACIÓN...")

    try:
        # Stats cerebro nuevo
        response = requests.get(f"{DST_API}/stats", timeout=TIMEOUT)
        if response.status_code != 200:
            print("❌ No se pudo obtener stats del cerebro nuevo")
            return False

        stats = response.json()["stats"]
        total = stats.get("total_episodes", 0)
        with_embeddings = stats.get("episodes_with_embeddings", 0)

        print(f"  Total episodios: {total}")
        print(f"  Con embeddings: {with_embeddings} ({with_embeddings/total*100:.1f}%)")

        # Validar 100% embeddings
        if with_embeddings < total:
            print(f"⚠️  No todos los episodios tienen embeddings")
            return False

        # Test búsqueda semántica
        print("\n  Testeando búsqueda semántica...")
        search_payload = {
            "query": "fase 4 construccion cerebro nexus",
            "limit": 5,
            "min_similarity": 0.3
        }

        response = requests.post(
            f"{DST_API}/memory/search",
            json=search_payload,
            timeout=TIMEOUT
        )

        if response.status_code == 200:
            results = response.json()
            print(f"  ✅ Búsqueda semántica funcional ({results['count']} resultados)")
        else:
            print(f"  ⚠️  Búsqueda semántica falló (status {response.status_code})")

        # Health check
        response = requests.get(f"{DST_API}/health", timeout=TIMEOUT)
        if response.status_code == 200:
            health = response.json()
            print(f"\n  Health Status: {health['status']}")
            print(f"  Database: {health['database']}")
            print(f"  Redis: {health.get('redis', 'N/A')}")
            print(f"  Queue Depth: {health.get('queue_depth', 'N/A')}")

        print("\n✅ VALIDACIÓN COMPLETADA")
        return True

    except Exception as e:
        print(f"❌ Error en validación: {e}")
        return False


def main():
    """Ejecutar migración completa"""
    print("=" * 60)
    print("MIGRACION CEREBRO NEXUS: FASE 3 -> V2.0.0")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # 1. Obtener episodios origen
    source_episodes = get_source_episodes()

    if not source_episodes:
        print("\n❌ No se encontraron episodios para migrar")
        return

    total_episodes = len(source_episodes)
    print(f"\n📊 PLAN: Migrar {total_episodes} episodios")
    print()

    # 2. Migrar episodios
    print("🔄 INICIANDO MIGRACIÓN...")
    results = []

    for i, episode in enumerate(source_episodes):
        result = migrate_episode(episode, i, total_episodes)
        results.append(result)

        # Pequeña pausa para no saturar
        if i % 20 == 0 and i > 0:
            time.sleep(0.5)

    # 3. Reporte migración
    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]

    print("\n" + "=" * 60)
    print("📊 RESULTADO MIGRACIÓN")
    print("=" * 60)
    print(f"✅ Exitosos: {len(successful)}/{total_episodes}")
    print(f"❌ Fallidos: {len(failed)}/{total_episodes}")

    if failed:
        print("\n⚠️  EPISODIOS FALLIDOS:")
        for fail in failed[:10]:  # Mostrar primeros 10
            print(f"  - ID: {fail.get('old_id')} - Error: {fail.get('error', 'Unknown')[:100]}")

        if len(failed) > 10:
            print(f"  ... y {len(failed) - 10} más")

    # 4. Esperar embeddings
    if successful:
        wait_for_embeddings(len(successful))

    # 5. Validar
    validation_ok = validate_migration()

    # 6. Reporte final
    print("\n" + "=" * 60)
    if len(successful) == total_episodes and validation_ok:
        print("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
    elif len(successful) > 0:
        print(f"⚠️  MIGRACIÓN COMPLETADA CON {len(failed)} ERRORES")
    else:
        print("❌ MIGRACIÓN FALLIDA")
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()

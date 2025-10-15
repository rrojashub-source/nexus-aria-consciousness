#!/bin/bash
# audit_episodes.sh - Auditoría completa de episodios pre-migración
# Fecha: 15 Octubre 2025
# Por: Ricardo + NEXUS

set -e

echo "═══════════════════════════════════════════════════════════"
echo "🔍 AUDITORÍA DE EPISODIOS - CEREBRO NEXUS PUERTO 5436"
echo "═══════════════════════════════════════════════════════════"
echo ""

PGPASSWORD=nexus_secure_2025 psql -h localhost -p 5436 -U nexus_user -d nexus_memory <<'EOF'

-- 1. RESUMEN GENERAL
\echo '═══════════════════════════════════════════════════════════'
\echo '📊 AUDITORÍA - RESUMEN GENERAL'
\echo '═══════════════════════════════════════════════════════════'
\echo ''

SELECT
  'TOTAL EPISODIOS' as category,
  COUNT(*) as count,
  ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM zep_episodic_memory), 1) || '%' as percentage
FROM zep_episodic_memory
UNION ALL
SELECT
  'BASURA: shadow_checkpoint' as category,
  COUNT(*) as count,
  ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM zep_episodic_memory), 1) || '%' as percentage
FROM zep_episodic_memory
WHERE metadata->>'action_type' = 'nexus_shadow_checkpoint'
UNION ALL
SELECT
  'BASURA: pre_compaction' as category,
  COUNT(*) as count,
  ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM zep_episodic_memory), 1) || '%' as percentage
FROM zep_episodic_memory
WHERE metadata->>'action_type' = 'nexus_pre_compaction_checkpoint'
UNION ALL
SELECT
  'MALFORMADOS (sin metadata)' as category,
  COUNT(*) as count,
  ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM zep_episodic_memory), 1) || '%' as percentage
FROM zep_episodic_memory
WHERE metadata IS NULL OR metadata = '{}'
UNION ALL
SELECT
  'ANTIGUOS (antes 2025-08-25)' as category,
  COUNT(*) as count,
  ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM zep_episodic_memory), 1) || '%' as percentage
FROM zep_episodic_memory
WHERE timestamp < '2025-08-25'
UNION ALL
SELECT
  '✅ VÁLIDOS PARA MIGRACIÓN' as category,
  COUNT(*) as count,
  ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM zep_episodic_memory), 1) || '%' as percentage
FROM zep_episodic_memory
WHERE
  timestamp >= '2025-08-25'
  AND metadata IS NOT NULL
  AND metadata != '{}'
  AND metadata->>'action_type' NOT IN ('nexus_shadow_checkpoint', 'nexus_pre_compaction_checkpoint');

-- 2. EPISODIOS VÁLIDOS POR CATEGORÍA
\echo ''
\echo '═══════════════════════════════════════════════════════════'
\echo '✅ EPISODIOS VÁLIDOS - DESGLOSE POR CATEGORÍA'
\echo '═══════════════════════════════════════════════════════════'
\echo ''

SELECT
  CASE
    WHEN metadata->>'action_type' LIKE 'fase4_%' THEN '🚀 FASE 4 Construcción'
    WHEN metadata->>'action_type' LIKE 'neural_mesh_%' THEN '🧠 Neural Mesh'
    WHEN metadata->>'action_type' IN ('project_milestone', 'milestone_completed', 'cerebro_master_milestone') THEN '🎯 Milestones'
    WHEN metadata->>'action_type' LIKE '%genesis%' THEN '🧬 Genesis History'
    WHEN metadata->>'action_type' LIKE 'forensic_%' THEN '🔍 Forensic Audit'
    WHEN metadata->>'action_type' = 'critical_bug_report' THEN '🐛 Critical Bugs'
    WHEN metadata->>'tags' LIKE '%cerebro_master_nexus_001%' THEN '📦 Proyecto Master'
    ELSE '📋 Otros Relevantes'
  END as category,
  COUNT(*) as count
FROM zep_episodic_memory
WHERE
  timestamp >= '2025-08-25'
  AND metadata IS NOT NULL
  AND metadata != '{}'
  AND metadata->>'action_type' NOT IN ('nexus_shadow_checkpoint', 'nexus_pre_compaction_checkpoint')
GROUP BY category
ORDER BY count DESC;

-- 3. TOP 30 EPISODIOS MÁS RECIENTES VÁLIDOS
\echo ''
\echo '═══════════════════════════════════════════════════════════'
\echo '📋 TOP 30 EPISODIOS RECIENTES VÁLIDOS'
\echo '═══════════════════════════════════════════════════════════'
\echo ''

SELECT
  TO_CHAR(timestamp, 'YYYY-MM-DD HH24:MI') as timestamp,
  RPAD(COALESCE(metadata->>'action_type', 'N/A'), 40) as action_type,
  LEFT(content, 50) || '...' as content_preview
FROM zep_episodic_memory
WHERE
  timestamp >= '2025-08-25'
  AND metadata IS NOT NULL
  AND metadata->>'action_type' NOT IN ('nexus_shadow_checkpoint', 'nexus_pre_compaction_checkpoint')
ORDER BY timestamp DESC
LIMIT 30;

-- 4. DISTRIBUCIÓN TEMPORAL (últimos 30 días)
\echo ''
\echo '═══════════════════════════════════════════════════════════'
\echo '📅 DISTRIBUCIÓN TEMPORAL - ÚLTIMOS 30 DÍAS (VÁLIDOS)'
\echo '═══════════════════════════════════════════════════════════'
\echo ''

SELECT
  DATE(timestamp) as date,
  COUNT(*) as valid_episodes,
  STRING_AGG(DISTINCT SUBSTRING(metadata->>'action_type', 1, 30), ', ') as action_types
FROM zep_episodic_memory
WHERE
  timestamp >= CURRENT_DATE - INTERVAL '30 days'
  AND metadata IS NOT NULL
  AND metadata->>'action_type' NOT IN ('nexus_shadow_checkpoint', 'nexus_pre_compaction_checkpoint')
GROUP BY DATE(timestamp)
ORDER BY date DESC;

-- 5. VERIFICAR TAGS (cerebro_master_nexus_001)
\echo ''
\echo '═══════════════════════════════════════════════════════════'
\echo '🏷️  EPISODIOS CON TAG: cerebro_master_nexus_001'
\echo '═══════════════════════════════════════════════════════════'
\echo ''

SELECT
  COUNT(*) as episodes_with_project_tag,
  MIN(timestamp) as oldest,
  MAX(timestamp) as newest
FROM zep_episodic_memory
WHERE metadata->>'tags' LIKE '%cerebro_master_nexus_001%';

-- 6. EXPORTAR IDs VÁLIDOS
\echo ''
\echo '═══════════════════════════════════════════════════════════'
\echo '💾 EXPORTANDO IDs DE EPISODIOS VÁLIDOS'
\echo '═══════════════════════════════════════════════════════════'
\echo ''

\copy (SELECT episode_id FROM zep_episodic_memory WHERE timestamp >= '2025-08-25' AND metadata IS NOT NULL AND metadata != '{}' AND metadata->>'action_type' NOT IN ('nexus_shadow_checkpoint', 'nexus_pre_compaction_checkpoint') ORDER BY timestamp) TO '/tmp/episodes_to_migrate.txt'

SELECT
  COUNT(*) || ' episodios válidos exportados a /tmp/episodes_to_migrate.txt' as resultado
FROM zep_episodic_memory
WHERE
  timestamp >= '2025-08-25'
  AND metadata IS NOT NULL
  AND metadata != '{}'
  AND metadata->>'action_type' NOT IN ('nexus_shadow_checkpoint', 'nexus_pre_compaction_checkpoint');

-- 7. RESUMEN FINAL
\echo ''
\echo '═══════════════════════════════════════════════════════════'
\echo '🎯 RESUMEN FINAL - DECISIÓN DE MIGRACIÓN'
\echo '═══════════════════════════════════════════════════════════'
\echo ''

WITH stats AS (
  SELECT
    COUNT(*) as total,
    COUNT(*) FILTER (WHERE metadata->>'action_type' IN ('nexus_shadow_checkpoint', 'nexus_pre_compaction_checkpoint')) as basura,
    COUNT(*) FILTER (WHERE timestamp >= '2025-08-25' AND metadata IS NOT NULL AND metadata != '{}' AND metadata->>'action_type' NOT IN ('nexus_shadow_checkpoint', 'nexus_pre_compaction_checkpoint')) as validos
  FROM zep_episodic_memory
)
SELECT
  '📊 EPISODIOS TOTALES: ' || total as stat1,
  '🗑️  BASURA A EXCLUIR: ' || basura || ' (' || ROUND(100.0 * basura / total, 1) || '%)' as stat2,
  '✅ VÁLIDOS A MIGRAR: ' || validos || ' (' || ROUND(100.0 * validos / total, 1) || '%)' as stat3,
  '💾 ESPACIO AHORRADO: ' || ROUND(100.0 * basura / total, 0) || '% del cerebro nuevo limpio' as stat4
FROM stats;

\echo ''
\echo '═══════════════════════════════════════════════════════════'
\echo '✅ AUDITORÍA COMPLETADA'
\echo '═══════════════════════════════════════════════════════════'
\echo ''
\echo 'Próximos pasos:'
\echo '1. Revisar este reporte con Ricardo'
\echo '2. Verificar /tmp/episodes_to_migrate.txt'
\echo '3. Confirmar lista de episodios antes de migrar'
\echo '4. SOLO DESPUÉS → Proceder a FASE 1 (Pre-migración)'
\echo ''

EOF

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "📄 Archivos generados:"
echo "  - /tmp/episodes_to_migrate.txt (IDs de episodios válidos)"
echo "═══════════════════════════════════════════════════════════"

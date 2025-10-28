"""
A/B Testing Framework for LAB_005 Performance Measurement

Tracks and compares metrics before/after spreading activation implementation:
- Retrieval latency (ms)
- Cache hit rate (%)
- Context coherence (cosine similarity)
- Number of primed episodes
"""

import time
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from collections import defaultdict
import numpy as np
import psycopg
from enum import Enum


class TestVariant(str, Enum):
    """A/B test variants"""
    CONTROL = "control"      # Without LAB_005
    TREATMENT = "treatment"  # With LAB_005


@dataclass
class RetrievalMetrics:
    """Metrics for a single retrieval operation"""
    variant: TestVariant
    retrieval_time_ms: float
    cache_hit: bool
    num_results: int
    context_coherence: Optional[float] = None  # Average similarity of results
    primed_count: int = 0
    timestamp: float = field(default_factory=time.time)
    query_id: Optional[str] = None


@dataclass
class AggregatedMetrics:
    """Aggregated metrics for a test variant"""
    variant: TestVariant
    sample_count: int
    avg_retrieval_time_ms: float
    p50_retrieval_time_ms: float
    p95_retrieval_time_ms: float
    cache_hit_rate: float
    avg_context_coherence: float
    avg_primed_count: float
    total_duration_seconds: float


class ABTestManager:
    """
    Manages A/B tests for LAB_005 performance measurement.

    Tracks metrics for both control (no priming) and treatment (with priming)
    variants, enabling statistical comparison of performance improvements.
    """

    def __init__(self, db_conn_string: str):
        self.db_conn_string = db_conn_string
        self.in_memory_buffer: Dict[TestVariant, List[RetrievalMetrics]] = {
            TestVariant.CONTROL: [],
            TestVariant.TREATMENT: []
        }
        self._ensure_tables()

    def _ensure_tables(self):
        """Create A/B testing tables if they don't exist"""
        with psycopg.connect(self.db_conn_string) as conn:
            with conn.cursor() as cur:
                # Metrics table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS ab_test_metrics (
                        id SERIAL PRIMARY KEY,
                        variant VARCHAR(20) NOT NULL,
                        retrieval_time_ms FLOAT NOT NULL,
                        cache_hit BOOLEAN NOT NULL,
                        num_results INTEGER NOT NULL,
                        context_coherence FLOAT,
                        primed_count INTEGER DEFAULT 0,
                        query_id VARCHAR(255),
                        timestamp TIMESTAMP DEFAULT NOW()
                    )
                """)

                # Test runs table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS ab_test_runs (
                        id SERIAL PRIMARY KEY,
                        test_name VARCHAR(255) NOT NULL,
                        variant VARCHAR(20) NOT NULL,
                        start_time TIMESTAMP NOT NULL,
                        end_time TIMESTAMP,
                        sample_count INTEGER DEFAULT 0,
                        status VARCHAR(20) DEFAULT 'active'
                    )
                """)

                # Indexes for performance
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_ab_variant_timestamp
                    ON ab_test_metrics(variant, timestamp)
                """)

                conn.commit()

    def record_retrieval(
        self,
        variant: TestVariant,
        retrieval_time_ms: float,
        cache_hit: bool,
        num_results: int,
        context_coherence: Optional[float] = None,
        primed_count: int = 0,
        query_id: Optional[str] = None
    ):
        """Record a single retrieval operation"""
        metrics = RetrievalMetrics(
            variant=variant,
            retrieval_time_ms=retrieval_time_ms,
            cache_hit=cache_hit,
            num_results=num_results,
            context_coherence=context_coherence,
            primed_count=primed_count,
            query_id=query_id
        )

        # Add to in-memory buffer
        self.in_memory_buffer[variant].append(metrics)

        # Persist to database
        self._persist_metrics(metrics)

    def _persist_metrics(self, metrics: RetrievalMetrics):
        """Persist metrics to PostgreSQL"""
        with psycopg.connect(self.db_conn_string) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO ab_test_metrics (
                        variant, retrieval_time_ms, cache_hit, num_results,
                        context_coherence, primed_count, query_id, timestamp
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, to_timestamp(%s))
                """, (
                    metrics.variant.value,
                    metrics.retrieval_time_ms,
                    metrics.cache_hit,
                    metrics.num_results,
                    metrics.context_coherence,
                    metrics.primed_count,
                    metrics.query_id,
                    metrics.timestamp
                ))
                conn.commit()

    def get_aggregated_metrics(
        self,
        variant: TestVariant,
        hours_back: int = 24
    ) -> Optional[AggregatedMetrics]:
        """Get aggregated metrics for a variant over a time period"""
        cutoff_time = datetime.now() - timedelta(hours=hours_back)

        with psycopg.connect(self.db_conn_string) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT
                        retrieval_time_ms,
                        cache_hit,
                        context_coherence,
                        primed_count,
                        EXTRACT(EPOCH FROM timestamp) as ts
                    FROM ab_test_metrics
                    WHERE variant = %s AND timestamp >= %s
                    ORDER BY timestamp ASC
                """, (variant.value, cutoff_time))

                rows = cur.fetchall()

        if not rows:
            return None

        # Extract data
        retrieval_times = [row[0] for row in rows]
        cache_hits = [row[1] for row in rows]
        coherence_scores = [row[2] for row in rows if row[2] is not None]
        primed_counts = [row[3] for row in rows]
        timestamps = [row[4] for row in rows]

        # Calculate aggregates
        return AggregatedMetrics(
            variant=variant,
            sample_count=len(rows),
            avg_retrieval_time_ms=float(np.mean(retrieval_times)),
            p50_retrieval_time_ms=float(np.percentile(retrieval_times, 50)),
            p95_retrieval_time_ms=float(np.percentile(retrieval_times, 95)),
            cache_hit_rate=float(sum(cache_hits) / len(cache_hits)),
            avg_context_coherence=float(np.mean(coherence_scores)) if coherence_scores else 0.0,
            avg_primed_count=float(np.mean(primed_counts)),
            total_duration_seconds=max(timestamps) - min(timestamps)
        )

    def compare_variants(self, hours_back: int = 24) -> Dict:
        """Compare control vs treatment variants"""
        control = self.get_aggregated_metrics(TestVariant.CONTROL, hours_back)
        treatment = self.get_aggregated_metrics(TestVariant.TREATMENT, hours_back)

        if not control or not treatment:
            return {
                "error": "Insufficient data for both variants",
                "control_samples": control.sample_count if control else 0,
                "treatment_samples": treatment.sample_count if treatment else 0
            }

        # Calculate improvements
        latency_improvement = (
            (control.avg_retrieval_time_ms - treatment.avg_retrieval_time_ms) /
            control.avg_retrieval_time_ms * 100
        )

        cache_improvement = (
            (treatment.cache_hit_rate - control.cache_hit_rate) /
            max(control.cache_hit_rate, 0.01) * 100
        )

        coherence_improvement = (
            (treatment.avg_context_coherence - control.avg_context_coherence) /
            max(control.avg_context_coherence, 0.01) * 100
        )

        return {
            "control": asdict(control),
            "treatment": asdict(treatment),
            "improvements": {
                "latency_reduction_percent": round(latency_improvement, 2),
                "cache_hit_rate_increase_percent": round(cache_improvement, 2),
                "coherence_increase_percent": round(coherence_improvement, 2),
                "avg_primed_episodes": round(treatment.avg_primed_count, 2)
            },
            "statistical_significance": self._calculate_significance(control, treatment),
            "recommendation": self._generate_recommendation(
                latency_improvement,
                cache_improvement,
                coherence_improvement
            )
        }

    def _calculate_significance(
        self,
        control: AggregatedMetrics,
        treatment: AggregatedMetrics
    ) -> Dict:
        """Calculate statistical significance (simplified t-test approximation)"""
        # In a production system, you'd use scipy.stats.ttest_ind
        # This is a simplified version

        sample_size_ok = control.sample_count >= 30 and treatment.sample_count >= 30

        # Simple effect size calculation (Cohen's d approximation)
        latency_diff = abs(treatment.avg_retrieval_time_ms - control.avg_retrieval_time_ms)
        latency_effect_size = latency_diff / max(control.avg_retrieval_time_ms, 1)

        return {
            "sample_size_adequate": sample_size_ok,
            "control_samples": control.sample_count,
            "treatment_samples": treatment.sample_count,
            "latency_effect_size": round(latency_effect_size, 3),
            "confidence_level": "high" if sample_size_ok and latency_effect_size > 0.2 else "medium"
        }

    def _generate_recommendation(
        self,
        latency_improvement: float,
        cache_improvement: float,
        coherence_improvement: float
    ) -> str:
        """Generate human-readable recommendation"""
        if latency_improvement > 40 and cache_improvement > 30:
            return "✅ STRONG POSITIVE: Deploy LAB_005 to production"
        elif latency_improvement > 20 and cache_improvement > 15:
            return "✅ POSITIVE: LAB_005 shows clear improvements, recommended for deployment"
        elif latency_improvement > 0 and cache_improvement > 0:
            return "⚠️ MARGINAL: LAB_005 shows minor improvements, consider longer testing"
        else:
            return "❌ NEGATIVE: LAB_005 does not show improvements, needs optimization"

    def get_time_series(
        self,
        variant: TestVariant,
        hours_back: int = 24,
        bucket_minutes: int = 60
    ) -> List[Dict]:
        """Get time-series data for visualization"""
        cutoff_time = datetime.now() - timedelta(hours=hours_back)

        with psycopg.connect(self.db_conn_string) as conn:
            with conn.cursor() as cur:
                cur.execute(f"""
                    SELECT
                        DATE_TRUNC('hour', timestamp) as bucket,
                        AVG(retrieval_time_ms) as avg_latency,
                        AVG(CASE WHEN cache_hit THEN 1.0 ELSE 0.0 END) as hit_rate,
                        COUNT(*) as sample_count
                    FROM ab_test_metrics
                    WHERE variant = %s AND timestamp >= %s
                    GROUP BY bucket
                    ORDER BY bucket ASC
                """, (variant.value, cutoff_time))

                rows = cur.fetchall()

        return [
            {
                "timestamp": row[0].isoformat(),
                "avg_latency_ms": float(row[1]),
                "cache_hit_rate": float(row[2]),
                "sample_count": row[3]
            }
            for row in rows
        ]

    def clear_test_data(self, variant: Optional[TestVariant] = None):
        """Clear test data (for resetting experiments)"""
        with psycopg.connect(self.db_conn_string) as conn:
            with conn.cursor() as cur:
                if variant:
                    cur.execute(
                        "DELETE FROM ab_test_metrics WHERE variant = %s",
                        (variant.value,)
                    )
                else:
                    cur.execute("TRUNCATE TABLE ab_test_metrics")
                conn.commit()

        # Clear in-memory buffer
        if variant:
            self.in_memory_buffer[variant] = []
        else:
            self.in_memory_buffer = {
                TestVariant.CONTROL: [],
                TestVariant.TREATMENT: []
            }


# Singleton instance
_ab_test_manager: Optional[ABTestManager] = None

def get_ab_test_manager(db_conn_string: str) -> ABTestManager:
    """Get or create singleton ABTestManager instance"""
    global _ab_test_manager
    if _ab_test_manager is None:
        _ab_test_manager = ABTestManager(db_conn_string)
    return _ab_test_manager

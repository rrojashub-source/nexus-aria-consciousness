#!/usr/bin/env python3
"""
Consolidation Engine for NEXUS Memory System

Mimics biological sleep consolidation: selective replay, backward tracing,
and prevention of catastrophic forgetting through interleaved processing.

Inspired by:
- Wilson & McNaughton (1994): Hippocampal replay discovery
- Nature 2024 (Chang): Sleep microstructure organizes replay
- bioRxiv 2025: Interleaved replay prevents catastrophic forgetting
- O'Neill 2010: 5-10x replay of reward-related memories

Author: NEXUS + Ricardo
Date: October 27, 2025
Lab: LAB_003 - Sleep Consolidation
"""

import numpy as np
import psycopg
from psycopg.rows import dict_row
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
import json
import math


@dataclass
class Episode:
    """Episode from memory system"""
    episode_id: str
    content: str
    embedding: List[float]
    created_at: datetime
    session_id: Optional[str]
    tags: List[str]
    importance_score: float

    # LAB_001 scores
    salience_score: float
    emotional_8d: Dict[str, float]
    somatic_7d: Dict[str, float]

    # LAB_003 scores (calculated)
    breakthrough_score: float = 0.0
    consolidated_salience_score: Optional[float] = None


@dataclass
class MemoryTrace:
    """Directed edge in memory graph"""
    source_episode_id: str
    target_episode_id: str
    trace_type: str  # 'initiator', 'progression', 'conclusion'
    strength: float  # 0.0 to 1.0
    narrative_id: str
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ConsolidationReport:
    """Report of consolidation process"""
    date: datetime
    episodes_processed: int
    breakthrough_count: int
    chain_count: int
    episodes_boosted: int
    trace_count: int
    avg_boost: float
    max_boost: float
    processing_time_seconds: float
    top_breakthroughs: List[Dict]


class ConsolidationEngine:
    """
    Offline batch processing for memory consolidation

    Mimics biological sleep: selective replay, backward tracing,
    interleaved processing to prevent catastrophic forgetting.
    """

    def __init__(self,
                 db_host: str = 'localhost',
                 db_port: int = 5432,
                 db_name: str = 'nexus_memory',
                 db_user: str = 'nexus_user',
                 db_password: str = 'nexus_password'):
        """
        Initialize consolidation engine

        Args:
            db_host: PostgreSQL host
            db_port: PostgreSQL port
            db_name: Database name
            db_user: Database user
            db_password: Database password
        """
        self.db_host = db_host
        self.db_port = db_port
        self.db_name = db_name
        self.db_user = db_user
        self.db_password = db_password

        self.conn = None
        self.cursor = None

    def connect(self):
        """Establish database connection"""
        self.conn = psycopg.connect(
            host=self.db_host,
            port=self.db_port,
            dbname=self.db_name,
            user=self.db_user,
            password=self.db_password
        )
        self.cursor = self.conn.cursor(row_factory=dict_row)

    def close(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()

    # =====================================================================
    # STEP 1: FETCH EPISODES
    # =====================================================================

    def fetch_episodes_from_date(self, target_date: datetime) -> List[Episode]:
        """
        Fetch all episodes from a specific date

        Args:
            target_date: Date to fetch episodes from

        Returns:
            List of Episode objects
        """
        start_of_day = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)

        query = """
            SELECT
                episode_id,
                content,
                created_at,
                tags,
                importance_score,
                metadata
            FROM nexus_memory.zep_episodic_memory
            WHERE created_at >= %s AND created_at < %s
            ORDER BY created_at ASC
        """

        self.cursor.execute(query, (start_of_day, end_of_day))
        rows = self.cursor.fetchall()

        episodes = []
        for row in rows:
            # Parse metadata for LAB_001 scores (psycopg v3 auto-decodes JSONB)
            metadata = row['metadata'] if row['metadata'] else {}

            emotional_8d = metadata.get('emotional_8d', {
                'joy': 0.5, 'trust': 0.5, 'fear': 0.0, 'surprise': 0.5,
                'sadness': 0.0, 'disgust': 0.0, 'anger': 0.0, 'anticipation': 0.5
            })

            somatic_7d = metadata.get('somatic_7d', {
                'valence': 0.0, 'arousal': 0.5, 'body_state': 0.5,
                'cognitive_load': 0.5, 'emotional_regulation': 0.5,
                'social_engagement': 0.5, 'temporal_awareness': 0.5
            })

            salience_score = metadata.get('salience_score', 0.5)
            session_id = metadata.get('session_id', None)
            # embedding = metadata.get('embedding', [])  # Not used in consolidation

            episode = Episode(
                episode_id=str(row['episode_id']),
                content=row['content'],
                embedding=[],  # Not needed for consolidation
                created_at=row['created_at'],
                session_id=session_id,
                tags=row['tags'] if row['tags'] else [],
                importance_score=float(row['importance_score']),
                salience_score=salience_score,
                emotional_8d=emotional_8d,
                somatic_7d=somatic_7d
            )

            episodes.append(episode)

        return episodes

    # =====================================================================
    # STEP 2: IDENTIFY BREAKTHROUGHS
    # =====================================================================

    def identify_breakthroughs(self,
                               episodes: List[Episode],
                               threshold_percentile: int = 80) -> List[Episode]:
        """
        Detect breakthrough episodes using composite scoring

        Based on O'Neill 2010: Reward-related memories replayed 5-10x more

        Args:
            episodes: List of episodes from the day
            threshold_percentile: Top X% considered breakthroughs

        Returns:
            List of breakthrough episodes sorted by importance
        """
        if not episodes:
            return []

        for episode in episodes:
            score = 0.0

            # Signal 1: Emotional salience (LAB_001) - 40% weight
            score += episode.salience_score * 0.4

            # Signal 2: Breakthrough emotions - 25% weight
            breakthrough_emotions = ['joy', 'trust', 'anticipation', 'surprise']
            emotion_sum = sum(episode.emotional_8d.get(e, 0)
                            for e in breakthrough_emotions)
            score += (emotion_sum / 4) * 0.25

            # Signal 3: Somatic valence (positive outcomes) - 15% weight
            valence = episode.somatic_7d.get('valence', 0)
            score += max(0, valence) * 0.15

            # Signal 4: Importance score (pre-existing) - 20% weight
            score += episode.importance_score * 0.20

            episode.breakthrough_score = score

        # Calculate threshold (top 20%)
        scores = [e.breakthrough_score for e in episodes]
        threshold = np.percentile(scores, threshold_percentile)

        breakthroughs = [e for e in episodes if e.breakthrough_score >= threshold]
        breakthroughs.sort(key=lambda x: x.breakthrough_score, reverse=True)

        return breakthroughs

    # =====================================================================
    # STEP 3: TRACE BACKWARD CHAINS
    # =====================================================================

    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        if not vec1 or not vec2:
            return 0.0

        vec1_np = np.array(vec1)
        vec2_np = np.array(vec2)

        dot_product = np.dot(vec1_np, vec2_np)
        norm1 = np.linalg.norm(vec1_np)
        norm2 = np.linalg.norm(vec2_np)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return float(dot_product / (norm1 * norm2))

    def trace_breakthrough_chains(self,
                                  breakthroughs: List[Episode],
                                  all_episodes: List[Episode]) -> List[List[Episode]]:
        """
        Trace backward from breakthroughs to find precursor episodes

        Based on Dickinson 1996: Retrospective revaluation

        Args:
            breakthroughs: List of breakthrough episodes
            all_episodes: All episodes from the day

        Returns:
            List of chains (sequences of related episodes)
        """
        chains = []

        for breakthrough in breakthroughs:
            chain = [breakthrough]
            current_time = breakthrough.created_at

            # Look back up to 12 hours
            window_start = current_time - timedelta(hours=12)

            # Find candidates
            candidates = [e for e in all_episodes
                         if window_start <= e.created_at < current_time]

            # Sort by recency (most recent first)
            candidates.sort(key=lambda x: x.created_at, reverse=True)

            for candidate in candidates:
                # Relatedness criteria
                is_related = False

                # Same session
                if (candidate.session_id and breakthrough.session_id and
                    candidate.session_id == breakthrough.session_id):
                    is_related = True

                # Semantic similarity
                if candidate.embedding and breakthrough.embedding:
                    sim = self.cosine_similarity(candidate.embedding,
                                                 breakthrough.embedding)
                    if sim > 0.65:
                        is_related = True

                # Shared tags (at least 2)
                shared_tags = set(candidate.tags) & set(breakthrough.tags)
                if len(shared_tags) >= 2:
                    is_related = True

                # Temporal proximity (within 1 hour)
                time_diff = (current_time - candidate.created_at).total_seconds()
                if time_diff < 3600:
                    is_related = True

                if is_related:
                    chain.insert(0, candidate)  # Add to beginning
                    current_time = candidate.created_at  # Update search time

            # Only keep chains with 2+ episodes
            if len(chain) >= 2:
                chains.append(chain)

        return chains

    # =====================================================================
    # STEP 4: CONSOLIDATED SALIENCE CALCULATION
    # =====================================================================

    def consolidate_chain(self, chain: List[Episode]):
        """
        Calculate consolidated_salience_score for each episode in chain

        Based on:
        - O'Neill 2010: 5-10x replay for rewarding experiences
        - Dickinson 1996: Retrospective revaluation

        Args:
            chain: List of episodes leading to breakthrough
        """
        if len(chain) < 2:
            return

        breakthrough = chain[-1]
        breakthrough_score = breakthrough.breakthrough_score

        for i, episode in enumerate(chain):
            original_salience = episode.salience_score

            # Position in chain (earlier episodes get more boost)
            position_weight = 1.0 - (i / len(chain))

            # Distance from breakthrough (temporal decay)
            time_diff_hours = (breakthrough.created_at - episode.created_at).total_seconds() / 3600
            temporal_decay = np.exp(-time_diff_hours / 6.0)  # Half-life 6 hours

            # Consolidation boost formula
            boost = (
                breakthrough_score *
                position_weight *
                temporal_decay *
                0.25  # Scale factor
            )

            # Cap boost at +0.20
            boost = min(boost, 0.20)

            # Calculate consolidated salience
            consolidated_salience = min(original_salience + boost, 1.0)

            # Store both scores
            episode.consolidated_salience_score = consolidated_salience

            # Update importance_score
            episode.importance_score *= (1.0 + boost)

    # =====================================================================
    # STEP 5: INTERLEAVED REPLAY
    # =====================================================================

    def fetch_old_important_memories(self,
                                     sample_size: int,
                                     min_consolidated_salience: float = 0.70,
                                     min_age_days: int = 7,
                                     max_age_days: int = 90) -> List[Episode]:
        """
        Sample older important memories for interleaved replay

        Based on bioRxiv 2025: Prevents catastrophic forgetting

        Args:
            sample_size: Number of old memories to sample
            min_consolidated_salience: Minimum salience threshold
            min_age_days: Minimum age in days
            max_age_days: Maximum age in days

        Returns:
            List of sampled old episodes
        """
        now = datetime.now()
        min_date = now - timedelta(days=max_age_days)
        max_date = now - timedelta(days=min_age_days)

        query = """
            SELECT
                episode_id,
                content,
                created_at,
                tags,
                importance_score,
                metadata
            FROM nexus_memory.zep_episodic_memory
            WHERE created_at >= %s
              AND created_at < %s
              AND metadata->>'consolidated_salience_score' IS NOT NULL
              AND CAST(metadata->>'consolidated_salience_score' AS FLOAT) >= %s
            ORDER BY RANDOM()
            LIMIT %s
        """

        self.cursor.execute(query, (min_date, max_date,
                                   min_consolidated_salience, sample_size))
        rows = self.cursor.fetchall()

        episodes = []
        for row in rows:
            # psycopg v3 auto-decodes JSONB
            metadata = row['metadata'] if row['metadata'] else {}

            episode = Episode(
                episode_id=str(row['episode_id']),
                content=row['content'],
                embedding=[],  # Not needed for consolidation
                created_at=row['created_at'],
                session_id=metadata.get('session_id', None),
                tags=row['tags'] if row['tags'] else [],
                importance_score=float(row['importance_score']),
                salience_score=metadata.get('salience_score', 0.5),
                emotional_8d=metadata.get('emotional_8d', {}),
                somatic_7d=metadata.get('somatic_7d', {}),
                consolidated_salience_score=metadata.get('consolidated_salience_score')
            )

            episodes.append(episode)

        return episodes

    # =====================================================================
    # STEP 6: MEMORY TRACES
    # =====================================================================

    def create_memory_traces(self, chains: List[List[Episode]]) -> List[MemoryTrace]:
        """
        Create directed graph edges between chain episodes

        Enables narrative retrieval: Find any episode → Get full chain

        Args:
            chains: List of episode chains

        Returns:
            List of MemoryTrace objects
        """
        traces = []
        date_str = datetime.now().strftime('%Y%m%d')

        for chain_id, chain in enumerate(chains):
            narrative_id = f"chain_{date_str}_{chain_id}"

            for i in range(len(chain) - 1):
                source = chain[i]
                target = chain[i + 1]

                # Calculate trace strength
                time_gap_hours = (target.created_at - source.created_at).total_seconds() / 3600
                strength = 1.0 / (1.0 + time_gap_hours / 3.0)

                # Determine trace type
                if i == 0:
                    trace_type = 'initiator'
                elif i == len(chain) - 2:
                    trace_type = 'conclusion'
                else:
                    trace_type = 'progression'

                trace = MemoryTrace(
                    source_episode_id=source.episode_id,
                    target_episode_id=target.episode_id,
                    trace_type=trace_type,
                    strength=strength,
                    narrative_id=narrative_id
                )

                traces.append(trace)

        return traces

    # =====================================================================
    # STEP 7: DATABASE UPDATES
    # =====================================================================

    def update_consolidated_scores(self, episodes: List[Episode]):
        """
        Update database with consolidated salience scores

        Args:
            episodes: List of episodes with calculated consolidated scores
        """
        for episode in episodes:
            if episode.consolidated_salience_score is None:
                continue

            # Update metadata with new scores
            self.cursor.execute("""
                UPDATE nexus_memory.zep_episodic_memory
                SET
                    metadata = metadata || jsonb_build_object(
                        'consolidated_salience_score', %s,
                        'breakthrough_score', %s,
                        'last_consolidated_at', %s
                    ),
                    importance_score = %s
                WHERE episode_id = %s
            """, (
                float(episode.consolidated_salience_score),
                float(episode.breakthrough_score),
                datetime.now().isoformat(),
                float(episode.importance_score),
                episode.episode_id
            ))

        self.conn.commit()

    def store_memory_traces(self, traces: List[MemoryTrace]):
        """
        Store memory traces in database

        Args:
            traces: List of MemoryTrace objects
        """
        # Check if table exists
        self.cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_schema = 'nexus_memory'
                  AND table_name = 'memory_traces'
            )
        """)

        table_exists = self.cursor.fetchone()['exists']

        if not table_exists:
            # Create table if it doesn't exist
            self.cursor.execute("""
                CREATE TABLE nexus_memory.memory_traces (
                    trace_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    source_episode_id UUID,
                    target_episode_id UUID,
                    trace_type VARCHAR(50),
                    strength FLOAT,
                    narrative_id VARCHAR(100),
                    created_at TIMESTAMP DEFAULT NOW()
                );

                CREATE INDEX idx_memory_traces_source ON nexus_memory.memory_traces(source_episode_id);
                CREATE INDEX idx_memory_traces_target ON nexus_memory.memory_traces(target_episode_id);
                CREATE INDEX idx_memory_traces_narrative ON nexus_memory.memory_traces(narrative_id);
            """)
            self.conn.commit()

        # Insert traces
        for trace in traces:
            self.cursor.execute("""
                INSERT INTO nexus_memory.memory_traces
                    (source_episode_id, target_episode_id, trace_type,
                     strength, narrative_id, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                trace.source_episode_id,
                trace.target_episode_id,
                trace.trace_type,
                trace.strength,
                trace.narrative_id,
                trace.created_at
            ))

        self.conn.commit()

    # =====================================================================
    # MAIN CONSOLIDATION PIPELINE
    # =====================================================================

    def consolidate_daily_memories(self, target_date: datetime) -> ConsolidationReport:
        """
        Execute complete nightly consolidation process

        Mimics biological sleep: selective replay, backward tracing,
        interleaved processing to prevent forgetting.

        Args:
            target_date: Date to consolidate

        Returns:
            ConsolidationReport with statistics
        """
        start_time = datetime.now()

        print(f"[{start_time}] Starting consolidation for {target_date.date()}")

        # Step 1: Fetch episodes
        print("  Step 1: Fetching episodes...")
        episodes = self.fetch_episodes_from_date(target_date)
        print(f"    Found {len(episodes)} episodes")

        if len(episodes) == 0:
            return ConsolidationReport(
                date=target_date,
                episodes_processed=0,
                breakthrough_count=0,
                chain_count=0,
                episodes_boosted=0,
                trace_count=0,
                avg_boost=0.0,
                max_boost=0.0,
                processing_time_seconds=0.0,
                top_breakthroughs=[]
            )

        # Step 2: Identify breakthroughs
        print("  Step 2: Identifying breakthroughs...")
        breakthroughs = self.identify_breakthroughs(episodes)
        print(f"    Detected {len(breakthroughs)} breakthroughs")

        # Step 3: Trace backward chains
        print("  Step 3: Tracing backward chains...")
        chains = self.trace_breakthrough_chains(breakthroughs, episodes)
        print(f"    Found {len(chains)} chains")

        # Step 4: Calculate consolidated salience
        print("  Step 4: Calculating consolidated salience...")
        for chain in chains:
            self.consolidate_chain(chain)

        # Step 5: Interleaved replay
        print("  Step 5: Interleaved replay...")
        if len(chains) > 0:
            old_sample_size = int(len(chains) * 0.3 / 0.7)  # 30% old, 70% new
            old_memories = self.fetch_old_important_memories(old_sample_size)
            print(f"    Sampled {len(old_memories)} old memories")

        # Step 6: Create memory traces
        print("  Step 6: Creating memory traces...")
        traces = self.create_memory_traces(chains)
        print(f"    Created {len(traces)} memory traces")

        # Step 7: Update database
        print("  Step 7: Updating database...")

        # Collect all boosted episodes
        boosted_episodes = []
        boosts = []
        for chain in chains:
            for episode in chain:
                if episode.consolidated_salience_score:
                    boosted_episodes.append(episode)
                    boost = episode.consolidated_salience_score - episode.salience_score
                    boosts.append(boost)

        self.update_consolidated_scores(boosted_episodes)
        self.store_memory_traces(traces)

        # Calculate statistics
        avg_boost = float(np.mean(boosts)) if boosts else 0.0
        max_boost = float(np.max(boosts)) if boosts else 0.0

        # Top breakthroughs
        top_breakthroughs = [
            {
                'episode_id': b.episode_id,
                'content': b.content[:100],
                'breakthrough_score': b.breakthrough_score,
                'salience_score': b.salience_score
            }
            for b in breakthroughs[:5]
        ]

        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()

        print(f"[{end_time}] Consolidation complete ({processing_time:.1f}s)")

        report = ConsolidationReport(
            date=target_date,
            episodes_processed=len(episodes),
            breakthrough_count=len(breakthroughs),
            chain_count=len(chains),
            episodes_boosted=len(boosted_episodes),
            trace_count=len(traces),
            avg_boost=avg_boost,
            max_boost=max_boost,
            processing_time_seconds=processing_time,
            top_breakthroughs=top_breakthroughs
        )

        return report


# Example usage
if __name__ == "__main__":
    # Test consolidation
    import os

    DB_HOST = os.getenv('POSTGRES_HOST', 'localhost')
    DB_PORT = int(os.getenv('POSTGRES_PORT', '5437'))
    DB_NAME = os.getenv('POSTGRES_DB', 'nexus_memory')
    DB_USER = os.getenv('POSTGRES_USER', 'nexus_superuser')
    DB_PASSWORD = os.getenv('POSTGRES_PASSWORD', '')

    with ConsolidationEngine(
        db_host=DB_HOST,
        db_port=DB_PORT,
        db_name=DB_NAME,
        db_user=DB_USER,
        db_password=DB_PASSWORD
    ) as engine:
        # Consolidate yesterday
        yesterday = datetime.now() - timedelta(days=1)
        report = engine.consolidate_daily_memories(yesterday)

        print("\n" + "="*60)
        print("CONSOLIDATION REPORT")
        print("="*60)
        print(f"Date: {report.date.date()}")
        print(f"Episodes processed: {report.episodes_processed}")
        print(f"Breakthroughs detected: {report.breakthrough_count}")
        print(f"Chains traced: {report.chain_count}")
        print(f"Episodes boosted: {report.episodes_boosted}")
        print(f"Memory traces created: {report.trace_count}")
        print(f"Average boost: +{report.avg_boost:.3f}")
        print(f"Max boost: +{report.max_boost:.3f}")
        print(f"Processing time: {report.processing_time_seconds:.1f}s")
        print("\nTop Breakthroughs:")
        for i, bt in enumerate(report.top_breakthroughs, 1):
            print(f"  {i}. {bt['content']} (score: {bt['breakthrough_score']:.2f})")

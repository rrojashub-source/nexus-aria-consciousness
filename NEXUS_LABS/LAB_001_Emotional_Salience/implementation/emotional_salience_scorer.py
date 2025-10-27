#!/usr/bin/env python3
"""
Emotional Salience Scorer for NEXUS Memory System

Calculates salience scores for episodic memories based on emotional
and somatic context at time of encoding.

Inspired by neuroscience research on amygdala-hippocampus interaction
and emotional memory consolidation.

Author: NEXUS + Ricardo
Date: October 27, 2025
Lab: LAB_001 - Emotional Salience
"""

import math
from typing import Optional, Tuple, Dict, Any
from dataclasses import dataclass
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor


@dataclass
class EmotionalState:
    """Plutchik 8D LOVE emotional state"""
    joy: float
    trust: float
    fear: float
    surprise: float
    sadness: float
    disgust: float
    anger: float
    anticipation: float
    complexity: float
    created_at: datetime


@dataclass
class SomaticMarker:
    """Damasio 7D somatic marker"""
    situation: str
    valence: float
    arousal: float
    body_state: str
    strength: float
    timestamp: datetime


@dataclass
class SalienceScore:
    """Complete salience calculation result"""
    total_score: float
    emotional_intensity: float
    emotional_complexity: float
    somatic_valence_score: float
    somatic_arousal_score: float
    breakthrough_bonus: float
    has_emotional_context: bool
    has_somatic_context: bool


class EmotionalSalienceScorer:
    """
    Calculates emotional salience scores for memory retrieval weighting

    Based on neuroscience principles:
    - Amygdala tags emotionally salient events
    - Hippocampus preferentially consolidates emotional memories
    - Inverted-U relationship: moderate emotion = optimal recall
    """

    def __init__(self, db_host="localhost", db_port=5437, db_name="nexus_memory",
                 db_user="nexus_superuser", db_password="RpKeuQhnwqMOA4iQPILQshWtwFj0P2hm"):
        """
        Initialize scorer with database connection

        Args:
            db_host: PostgreSQL host
            db_port: PostgreSQL port (5437 for NEXUS V2)
            db_name: Database name
            db_user: Database user
            db_password: Database password
        """
        self.db_config = {
            'host': db_host,
            'port': db_port,
            'dbname': db_name,
            'user': db_user,
            'password': db_password
        }

        # Algorithm weights (tunable)
        self.weights = {
            'emotional_intensity': 0.35,
            'emotional_complexity': 0.25,
            'somatic_valence': 0.20,
            'somatic_arousal': 0.10,
            'breakthrough_bonus': 0.10
        }

    def _get_db_connection(self):
        """Get database connection"""
        return psycopg2.connect(**self.db_config)

    def get_emotional_context(self, timestamp: datetime) -> Tuple[Optional[EmotionalState], Optional[SomaticMarker]]:
        """
        Fetch emotional and somatic state closest to episode timestamp

        Args:
            timestamp: Episode creation timestamp

        Returns:
            Tuple of (EmotionalState, SomaticMarker) or (None, None) if not found
        """
        conn = self._get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        try:
            # Get emotional state closest to (but not after) timestamp
            cursor.execute("""
                SELECT
                    joy, trust, fear, surprise, sadness, disgust, anger, anticipation,
                    complexity, created_at
                FROM consciousness.emotional_states_log
                WHERE created_at <= %s
                ORDER BY created_at DESC
                LIMIT 1
            """, [timestamp])

            emotional_row = cursor.fetchone()
            emotional_state = None

            if emotional_row:
                emotional_state = EmotionalState(
                    joy=float(emotional_row['joy']),
                    trust=float(emotional_row['trust']),
                    fear=float(emotional_row['fear']),
                    surprise=float(emotional_row['surprise']),
                    sadness=float(emotional_row['sadness']),
                    disgust=float(emotional_row['disgust']),
                    anger=float(emotional_row['anger']),
                    anticipation=float(emotional_row['anticipation']),
                    complexity=float(emotional_row['complexity']),
                    created_at=emotional_row['created_at']
                )

            # Get somatic marker closest to timestamp
            cursor.execute("""
                SELECT
                    situation, valence, arousal, body_state, strength, timestamp
                FROM consciousness.somatic_markers_log
                WHERE timestamp <= %s
                ORDER BY timestamp DESC
                LIMIT 1
            """, [timestamp])

            somatic_row = cursor.fetchone()
            somatic_marker = None

            if somatic_row:
                somatic_marker = SomaticMarker(
                    situation=somatic_row['situation'],
                    valence=float(somatic_row['valence']),
                    arousal=float(somatic_row['arousal']),
                    body_state=somatic_row['body_state'],
                    strength=float(somatic_row['strength']),
                    timestamp=somatic_row['timestamp']
                )

            return emotional_state, somatic_marker

        finally:
            cursor.close()
            conn.close()

    def emotional_intensity(self, emotional_state: EmotionalState) -> float:
        """
        Calculate overall emotional arousal from 8D vector

        Uses L2 norm with inverted-U curve:
        - Moderate emotion (0.5-0.9) = optimal recall
        - Low emotion (<0.5) = slightly boosted
        - Extreme emotion (>0.9) = capped (too much arousal impairs memory)

        Args:
            emotional_state: 8D emotional vector

        Returns:
            Intensity score (0.0 - 1.0)
        """
        emotions = [
            emotional_state.joy,
            emotional_state.trust,
            emotional_state.fear,
            emotional_state.surprise,
            emotional_state.sadness,
            emotional_state.disgust,
            emotional_state.anger,
            emotional_state.anticipation
        ]

        # L2 norm of emotion vector, normalized by sqrt(8)
        l2_norm = math.sqrt(sum(e**2 for e in emotions))
        intensity = l2_norm / math.sqrt(8)

        # Apply inverted-U curve
        if intensity < 0.5:
            # Boost low emotions slightly (still memorable)
            return intensity * 1.4
        elif intensity < 0.9:
            # Optimal range - no modification
            return intensity
        else:
            # Cap extreme emotions (too much stress impairs memory)
            return 0.9

    def emotional_complexity(self, emotional_state: EmotionalState) -> float:
        """
        Calculate entropy of emotion distribution

        Mixed emotions = more salient (richer, more complex experience)
        Single dominant emotion = less complex

        Uses Shannon entropy normalized to 0-1

        Args:
            emotional_state: 8D emotional vector

        Returns:
            Complexity score (0.0 - 1.0)
        """
        emotions = [
            emotional_state.joy,
            emotional_state.trust,
            emotional_state.fear,
            emotional_state.surprise,
            emotional_state.sadness,
            emotional_state.disgust,
            emotional_state.anger,
            emotional_state.anticipation
        ]

        # Normalize to probability distribution
        total = sum(emotions) + 1e-10  # Avoid division by zero
        probs = [e / total for e in emotions]

        # Shannon entropy: H = -Σ(p * log2(p))
        entropy = -sum(p * math.log2(p) if p > 0 else 0 for p in probs)

        # Normalize to 0-1 (max entropy for 8 emotions is log2(8) = 3)
        complexity = entropy / 3.0

        return complexity

    def somatic_valence_score(self, somatic_marker: SomaticMarker) -> float:
        """
        Convert valence (-1 to +1) to salience weight (0 to 1)

        Both strong positive and negative body markers are salient,
        but positive slightly favored (easier retrieval in biology)

        Args:
            somatic_marker: Body marker with valence

        Returns:
            Valence-based salience score (0.0 - 1.0)
        """
        valence = somatic_marker.valence  # -1.0 to +1.0

        if valence >= 0:
            # Positive valence: 0.5 to 1.0
            return 0.5 + (valence * 0.5)
        else:
            # Negative valence: 0.5 to 0.9 (slightly less salient than positive)
            return 0.5 + (abs(valence) * 0.4)

    def somatic_arousal_score(self, somatic_marker: SomaticMarker) -> float:
        """
        High arousal = more memorable

        Direct mapping with slight boost

        Args:
            somatic_marker: Body marker with arousal

        Returns:
            Arousal-based salience score (0.0 - 1.0)
        """
        arousal = somatic_marker.arousal  # 0.0 to 1.0

        # Boost slightly, cap at 1.0
        return min(arousal * 1.2, 1.0)

    def breakthrough_bonus(self, somatic_marker: SomaticMarker,
                          emotional_state: EmotionalState) -> float:
        """
        Special bonus for "aha!" breakthrough moments

        Detected by:
        - Explicit "breakthrough" situation marker, OR
        - High anticipation + high joy combination

        Args:
            somatic_marker: Body marker
            emotional_state: Emotional state

        Returns:
            Bonus (0.0 or 0.3)
        """
        is_breakthrough = (
            somatic_marker.situation == "breakthrough" or
            (emotional_state.anticipation > 0.8 and emotional_state.joy > 0.6)
        )

        return 0.3 if is_breakthrough else 0.0

    def calculate_salience(self, episode_id: str, timestamp: datetime) -> SalienceScore:
        """
        Calculate overall salience score for an episode

        Combines emotional and somatic components with weighted sum

        Args:
            episode_id: Episode UUID
            timestamp: Episode creation timestamp

        Returns:
            SalienceScore object with total and component scores
        """
        # Fetch emotional context
        emotional_state, somatic_marker = self.get_emotional_context(timestamp)

        # If no context available, return neutral salience
        if not emotional_state or not somatic_marker:
            return SalienceScore(
                total_score=0.5,  # Neutral default
                emotional_intensity=0.0,
                emotional_complexity=0.0,
                somatic_valence_score=0.0,
                somatic_arousal_score=0.0,
                breakthrough_bonus=0.0,
                has_emotional_context=emotional_state is not None,
                has_somatic_context=somatic_marker is not None
            )

        # Calculate components
        intensity = self.emotional_intensity(emotional_state)
        complexity = self.emotional_complexity(emotional_state)
        valence = self.somatic_valence_score(somatic_marker)
        arousal = self.somatic_arousal_score(somatic_marker)
        breakthrough = self.breakthrough_bonus(somatic_marker, emotional_state)

        # Weighted sum
        total_score = (
            intensity * self.weights['emotional_intensity'] +
            complexity * self.weights['emotional_complexity'] +
            valence * self.weights['somatic_valence'] +
            arousal * self.weights['somatic_arousal'] +
            breakthrough  # Additive bonus, not weighted
        )

        # Cap at 1.0
        total_score = min(total_score, 1.0)

        return SalienceScore(
            total_score=total_score,
            emotional_intensity=intensity,
            emotional_complexity=complexity,
            somatic_valence_score=valence,
            somatic_arousal_score=arousal,
            breakthrough_bonus=breakthrough,
            has_emotional_context=True,
            has_somatic_context=True
        )

    def batch_calculate_salience(self, episodes: list) -> Dict[str, SalienceScore]:
        """
        Calculate salience for multiple episodes efficiently

        Args:
            episodes: List of dicts with 'episode_id' and 'timestamp'

        Returns:
            Dict mapping episode_id -> SalienceScore
        """
        results = {}

        for episode in episodes:
            episode_id = episode['episode_id']
            timestamp = episode['timestamp']

            salience = self.calculate_salience(episode_id, timestamp)
            results[episode_id] = salience

        return results


# Example usage
if __name__ == "__main__":
    # Test the scorer
    scorer = EmotionalSalienceScorer()

    # Example episode timestamp
    test_timestamp = datetime(2025, 10, 27, 14, 3, 12)

    print("Testing Emotional Salience Scorer")
    print("=" * 50)

    # Get emotional context
    emotional_state, somatic_marker = scorer.get_emotional_context(test_timestamp)

    if emotional_state:
        print(f"\nEmotional State at {test_timestamp}:")
        print(f"  Joy: {emotional_state.joy:.2f}")
        print(f"  Trust: {emotional_state.trust:.2f}")
        print(f"  Anticipation: {emotional_state.anticipation:.2f}")
        print(f"  Complexity: {emotional_state.complexity:.2f}")

    if somatic_marker:
        print(f"\nSomatic Marker:")
        print(f"  Situation: {somatic_marker.situation}")
        print(f"  Valence: {somatic_marker.valence:.2f}")
        print(f"  Arousal: {somatic_marker.arousal:.2f}")

    # Calculate salience
    salience = scorer.calculate_salience("test-episode-id", test_timestamp)

    print(f"\nSalience Score:")
    print(f"  Total: {salience.total_score:.3f}")
    print(f"  Emotional Intensity: {salience.emotional_intensity:.3f}")
    print(f"  Emotional Complexity: {salience.emotional_complexity:.3f}")
    print(f"  Somatic Valence: {salience.somatic_valence_score:.3f}")
    print(f"  Somatic Arousal: {salience.somatic_arousal_score:.3f}")
    print(f"  Breakthrough Bonus: {salience.breakthrough_bonus:.3f}")
    print(f"\nHas Context: Emotional={salience.has_emotional_context}, Somatic={salience.has_somatic_context}")

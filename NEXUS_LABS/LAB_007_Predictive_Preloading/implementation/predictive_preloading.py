"""
LAB_007: Predictive Preloading Engine

Anticipatory memory system that learns temporal patterns and predicts
which episodes will be accessed next, preloading them before requested.

Based on neuroscience: Predictive processing theory, sequence learning,
anticipatory brain activity (2023-2025 research).

Author: NEXUS (Autonomous)
Date: October 28, 2025
"""

import asyncio
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple
import math
import heapq
import numpy as np


# ============================================================================
# Data Structures
# ============================================================================

@dataclass
class AccessEvent:
    """Single memory access event"""
    episode_id: str
    timestamp: datetime
    tags: Set[str]
    embedding: Optional[np.ndarray] = None


@dataclass
class SequencePattern:
    """Learned temporal sequence pattern"""
    source_id: str
    target_id: str
    count: int
    last_seen: datetime

    @property
    def probability(self) -> float:
        """Will be computed relative to total transitions from source"""
        return 0.0  # Computed dynamically

    @property
    def weight(self) -> float:
        """Decay weight based on age"""
        age_days = (datetime.now() - self.last_seen).days
        decay_rate = 0.1
        return math.exp(-decay_rate * age_days)


@dataclass
class Prediction:
    """Predicted next episode with confidence"""
    episode_id: str
    confidence: float
    sources: List[str]  # Which algorithms contributed

    def __lt__(self, other):
        """For heapq (max heap by confidence)"""
        return self.confidence > other.confidence


@dataclass
class SessionContext:
    """Current session context for prediction"""
    recent_episodes: List[str]
    recent_tags: Set[str]
    time_of_day: int  # 0-23
    day_of_week: int  # 0-6
    mean_embedding: Optional[np.ndarray] = None


# ============================================================================
# Component 1: TemporalPatternLearner
# ============================================================================

class TemporalPatternLearner:
    """
    Learn temporal sequences from access history.
    Implements bigram and trigram models with pattern decay.
    """

    def __init__(self, history_size: int = 100):
        self.access_history: deque = deque(maxlen=history_size)

        # Bigram model: (source, target) -> count
        self.bigram_counts: Dict[Tuple[str, str], int] = defaultdict(int)
        self.bigram_last_seen: Dict[Tuple[str, str], datetime] = {}

        # Trigram model: (prev_prev, prev, current) -> count
        self.trigram_counts: Dict[Tuple[str, str, str], int] = defaultdict(int)
        self.trigram_last_seen: Dict[Tuple[str, str, str], datetime] = {}

        # Total transitions from each source (for probability calculation)
        self.source_totals: Dict[str, int] = defaultdict(int)
        self.trigram_source_totals: Dict[Tuple[str, str], int] = defaultdict(int)

    def learn_from_access(self, episode_id: str, timestamp: datetime):
        """
        Update patterns based on new access.

        Args:
            episode_id: Accessed episode
            timestamp: When it was accessed
        """
        recent = list(self.access_history)

        # Learn bigram: previous → current
        if len(recent) >= 1:
            prev = recent[-1]
            key = (prev, episode_id)
            self.bigram_counts[key] += 1
            self.bigram_last_seen[key] = timestamp
            self.source_totals[prev] += 1

        # Learn trigram: (prev_prev, prev) → current
        if len(recent) >= 2:
            prev_prev, prev = recent[-2], recent[-1]
            key = (prev_prev, prev, episode_id)
            self.trigram_counts[key] += 1
            self.trigram_last_seen[key] = timestamp
            self.trigram_source_totals[(prev_prev, prev)] += 1

        # Add to history
        self.access_history.append(episode_id)

    def get_bigram_successors(
        self,
        source_id: str,
        min_confidence: float = 0.1
    ) -> List[Tuple[str, float, float]]:
        """
        Get likely next episodes based on bigram patterns.

        Args:
            source_id: Current episode
            min_confidence: Minimum probability threshold

        Returns:
            List of (target_id, probability, weight) sorted by probability
        """
        if source_id not in self.source_totals:
            return []

        total = self.source_totals[source_id]
        successors = []

        for (src, tgt), count in self.bigram_counts.items():
            if src == source_id:
                probability = count / total

                if probability >= min_confidence:
                    # Compute decay weight
                    last_seen = self.bigram_last_seen[(src, tgt)]
                    age_days = (datetime.now() - last_seen).days
                    weight = math.exp(-0.1 * age_days)

                    successors.append((tgt, probability, weight))

        # Sort by probability (descending)
        successors.sort(key=lambda x: x[1] * x[2], reverse=True)
        return successors

    def get_trigram_successors(
        self,
        prev_prev_id: str,
        prev_id: str,
        min_confidence: float = 0.1
    ) -> List[Tuple[str, float, float]]:
        """
        Get likely next episodes based on trigram patterns.

        Args:
            prev_prev_id: Episode before previous
            prev_id: Previous episode
            min_confidence: Minimum probability threshold

        Returns:
            List of (target_id, probability, weight)
        """
        key = (prev_prev_id, prev_id)
        if key not in self.trigram_source_totals:
            return []

        total = self.trigram_source_totals[key]
        successors = []

        for (pp, p, curr), count in self.trigram_counts.items():
            if (pp, p) == key:
                probability = count / total

                if probability >= min_confidence:
                    last_seen = self.trigram_last_seen[(pp, p, curr)]
                    age_days = (datetime.now() - last_seen).days
                    weight = math.exp(-0.1 * age_days)

                    successors.append((curr, probability, weight))

        successors.sort(key=lambda x: x[1] * x[2], reverse=True)
        return successors

    def decay_patterns(self):
        """
        Remove old patterns that have decayed to near zero.
        Call periodically (e.g., daily).
        """
        threshold_weight = 0.01  # 1% strength
        now = datetime.now()

        # Decay bigrams
        to_remove = []
        for key, last_seen in self.bigram_last_seen.items():
            age_days = (now - last_seen).days
            weight = math.exp(-0.1 * age_days)
            if weight < threshold_weight:
                to_remove.append(key)

        for key in to_remove:
            source, target = key
            self.source_totals[source] -= self.bigram_counts[key]
            del self.bigram_counts[key]
            del self.bigram_last_seen[key]

        # Decay trigrams (similar logic)
        to_remove = []
        for key, last_seen in self.trigram_last_seen.items():
            age_days = (now - last_seen).days
            weight = math.exp(-0.1 * age_days)
            if weight < threshold_weight:
                to_remove.append(key)

        for key in to_remove:
            pp, p, curr = key
            self.trigram_source_totals[(pp, p)] -= self.trigram_counts[key]
            del self.trigram_counts[key]
            del self.trigram_last_seen[key]


# ============================================================================
# Component 2: ContextAnalyzer
# ============================================================================

class ContextAnalyzer:
    """
    Analyze current session context for prediction.
    Computes similarity between candidates and current context.
    """

    def __init__(self):
        self.episode_metadata: Dict[str, dict] = {}  # Cache episode info

    def build_context(
        self,
        recent_events: List[AccessEvent]
    ) -> SessionContext:
        """
        Build session context from recent access history.

        Args:
            recent_events: Recent access events (last 5-10)

        Returns:
            SessionContext object
        """
        if not recent_events:
            return SessionContext(
                recent_episodes=[],
                recent_tags=set(),
                time_of_day=datetime.now().hour,
                day_of_week=datetime.now().weekday()
            )

        # Extract recent episode IDs
        recent_episodes = [e.episode_id for e in recent_events]

        # Union of all tags
        recent_tags = set()
        for event in recent_events:
            recent_tags.update(event.tags)

        # Current time context
        now = datetime.now()

        # Mean embedding (if available)
        embeddings = [e.embedding for e in recent_events if e.embedding is not None]
        mean_embedding = None
        if embeddings:
            mean_embedding = np.mean(embeddings, axis=0)

        return SessionContext(
            recent_episodes=recent_episodes,
            recent_tags=recent_tags,
            time_of_day=now.hour,
            day_of_week=now.weekday(),
            mean_embedding=mean_embedding
        )

    def compute_context_similarity(
        self,
        candidate_id: str,
        candidate_tags: Set[str],
        candidate_embedding: Optional[np.ndarray],
        context: SessionContext
    ) -> float:
        """
        Score how well candidate fits current context.

        Args:
            candidate_id: Candidate episode ID
            candidate_tags: Candidate tags
            candidate_embedding: Candidate embedding vector
            context: Current session context

        Returns:
            Similarity score (0.0 - 1.0)
        """
        scores = []

        # 1. Tag overlap
        if context.recent_tags:
            tag_overlap = len(candidate_tags & context.recent_tags) / len(context.recent_tags)
            scores.append(('tag_overlap', 0.4, tag_overlap))

        # 2. Semantic similarity (embeddings)
        if candidate_embedding is not None and context.mean_embedding is not None:
            # Cosine similarity
            cos_sim = np.dot(candidate_embedding, context.mean_embedding) / (
                np.linalg.norm(candidate_embedding) * np.linalg.norm(context.mean_embedding)
            )
            # Normalize to 0-1
            semantic_sim = (cos_sim + 1.0) / 2.0
            scores.append(('semantic', 0.6, semantic_sim))

        # Weighted average
        if not scores:
            return 0.5  # Neutral if no information

        total_weight = sum(w for _, w, _ in scores)
        weighted_sum = sum(w * s for _, w, s in scores)

        return weighted_sum / total_weight


# ============================================================================
# Component 3: PredictionEngine
# ============================================================================

class PredictionEngine:
    """
    Generate predictions by combining pattern learning and context analysis.
    """

    def __init__(
        self,
        pattern_learner: TemporalPatternLearner,
        context_analyzer: ContextAnalyzer
    ):
        self.pattern_learner = pattern_learner
        self.context_analyzer = context_analyzer

    def predict_next_episodes(
        self,
        current_episode_id: str,
        context: SessionContext,
        candidate_pool: Dict[str, dict],  # {episode_id: {tags, embedding, ...}}
        k: int = 5,
        min_confidence: float = 0.5
    ) -> List[Prediction]:
        """
        Predict top-K most likely next episodes.

        Args:
            current_episode_id: Currently accessed episode
            context: Session context
            candidate_pool: Pool of candidate episodes to consider
            k: Number of predictions to return
            min_confidence: Minimum confidence threshold

        Returns:
            List of Prediction objects, sorted by confidence (desc)
        """
        candidate_scores: Dict[str, Dict[str, float]] = defaultdict(lambda: {
            'pattern': 0.0,
            'context': 0.0,
            'recency': 0.0,
            'total': 0.0
        })

        # Source 1: Bigram patterns (60% weight)
        bigram_successors = self.pattern_learner.get_bigram_successors(
            current_episode_id,
            min_confidence=0.1
        )
        for target_id, prob, weight in bigram_successors:
            if target_id in candidate_pool:
                candidate_scores[target_id]['pattern'] += 0.6 * prob * weight

        # Source 2: Trigram patterns (30% weight)
        if len(context.recent_episodes) >= 2:
            prev_prev = context.recent_episodes[-2]
            prev = context.recent_episodes[-1]

            trigram_successors = self.pattern_learner.get_trigram_successors(
                prev_prev, prev, min_confidence=0.1
            )
            for target_id, prob, weight in trigram_successors:
                if target_id in candidate_pool:
                    candidate_scores[target_id]['pattern'] += 0.3 * prob * weight

        # Source 3: Context similarity (30% weight)
        for episode_id, metadata in candidate_pool.items():
            ctx_sim = self.context_analyzer.compute_context_similarity(
                episode_id,
                metadata.get('tags', set()),
                metadata.get('embedding'),
                context
            )
            candidate_scores[episode_id]['context'] = 0.3 * ctx_sim

        # Source 4: Recency boost (10% weight)
        # Recent episodes more likely to be revisited
        for episode_id in context.recent_episodes[-3:]:  # Last 3
            if episode_id in candidate_scores:
                candidate_scores[episode_id]['recency'] = 0.1

        # Compute total confidence
        for episode_id, scores in candidate_scores.items():
            scores['total'] = (
                scores['pattern'] +
                scores['context'] +
                scores['recency']
            )

        # Filter by minimum confidence
        filtered = [
            Prediction(
                episode_id=ep_id,
                confidence=scores['total'],
                sources=['pattern', 'context', 'recency']
            )
            for ep_id, scores in candidate_scores.items()
            if scores['total'] >= min_confidence
        ]

        # Sort by confidence (desc) and return top-K
        filtered.sort(key=lambda p: p.confidence, reverse=True)
        return filtered[:k]


# ============================================================================
# Component 4: PreloadingScheduler
# ============================================================================

class PreloadingScheduler:
    """
    Schedule and execute background preloading of predicted episodes.
    Manages cache, resource limits, and eviction policy.
    """

    def __init__(self, max_cache_size: int = 100):
        self.max_cache_size = max_cache_size

        # Cache: {episode_id: (data, confidence, timestamp)}
        self.cache: Dict[str, Tuple[dict, float, datetime]] = {}

        # Metrics
        self.metrics = {
            'preload_success': 0,
            'preload_failure': 0,
            'preload_wasted': 0,  # Preloaded but never accessed
            'cache_hits': 0,
            'cache_misses': 0
        }

    async def preload_predictions(
        self,
        predictions: List[Prediction],
        fetch_fn
    ):
        """
        Asynchronously preload predicted episodes.

        Args:
            predictions: List of predictions to preload
            fetch_fn: Async function to fetch episode data
        """
        tasks = []

        for prediction in predictions:
            # Skip if already cached
            if prediction.episode_id in self.cache:
                continue

            # Check resource limits
            if len(self.cache) >= self.max_cache_size:
                self._evict_lowest_score()

            # Schedule preload task
            task = self._preload_single(
                prediction.episode_id,
                prediction.confidence,
                fetch_fn
            )
            tasks.append(task)

        # Execute all preloads concurrently
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _preload_single(
        self,
        episode_id: str,
        confidence: float,
        fetch_fn
    ):
        """Preload single episode"""
        try:
            data = await fetch_fn(episode_id)
            self.cache[episode_id] = (data, confidence, datetime.now())
            self.metrics['preload_success'] += 1
        except Exception as e:
            self.metrics['preload_failure'] += 1

    def get_cached(self, episode_id: str) -> Optional[dict]:
        """
        Retrieve from cache.

        Args:
            episode_id: Episode to retrieve

        Returns:
            Episode data if cached, None otherwise
        """
        if episode_id in self.cache:
            self.metrics['cache_hits'] += 1
            data, confidence, timestamp = self.cache[episode_id]
            return data
        else:
            self.metrics['cache_misses'] += 1
            return None

    def _evict_lowest_score(self):
        """
        Evict entry with lowest combined score (recency * confidence).
        """
        if not self.cache:
            return

        now = datetime.now()
        scores = {}

        for ep_id, (data, confidence, timestamp) in self.cache.items():
            age_seconds = (now - timestamp).total_seconds()
            recency_score = math.exp(-age_seconds / 3600)  # Decay over hours
            scores[ep_id] = recency_score * confidence

        # Evict lowest
        min_id = min(scores, key=scores.get)
        del self.cache[min_id]
        self.metrics['preload_wasted'] += 1

    def get_cache_stats(self) -> dict:
        """Get cache performance statistics"""
        total_requests = self.metrics['cache_hits'] + self.metrics['cache_misses']
        hit_rate = (
            self.metrics['cache_hits'] / total_requests
            if total_requests > 0 else 0.0
        )

        total_preloads = self.metrics['preload_success'] + self.metrics['preload_failure']
        success_rate = (
            self.metrics['preload_success'] / total_preloads
            if total_preloads > 0 else 0.0
        )

        waste_rate = (
            self.metrics['preload_wasted'] / self.metrics['preload_success']
            if self.metrics['preload_success'] > 0 else 0.0
        )

        return {
            'cache_size': len(self.cache),
            'max_cache_size': self.max_cache_size,
            'cache_hit_rate': hit_rate,
            'preload_success_rate': success_rate,
            'preload_waste_rate': waste_rate,
            **self.metrics
        }


# ============================================================================
# Main Predictive Preloading Engine
# ============================================================================

class PredictivePreloadingEngine:
    """
    Main orchestrator for LAB_007.
    Integrates all components into unified predictive system.
    """

    def __init__(
        self,
        max_cache_size: int = 100,
        prediction_k: int = 5,
        min_confidence: float = 0.5
    ):
        self.pattern_learner = TemporalPatternLearner()
        self.context_analyzer = ContextAnalyzer()
        self.prediction_engine = PredictionEngine(
            self.pattern_learner,
            self.context_analyzer
        )
        self.preload_scheduler = PreloadingScheduler(max_cache_size)

        self.prediction_k = prediction_k
        self.min_confidence = min_confidence

        # Recent access history for context
        self.recent_events: deque = deque(maxlen=10)

    async def on_episode_access(
        self,
        episode_id: str,
        tags: Set[str],
        embedding: Optional[np.ndarray],
        candidate_pool: Dict[str, dict],
        fetch_fn
    ):
        """
        Called when an episode is accessed.

        1. Learn from this access
        2. Build current context
        3. Generate predictions
        4. Schedule preloading

        Args:
            episode_id: Accessed episode
            tags: Episode tags
            embedding: Episode embedding
            candidate_pool: Pool of all episodes to consider
            fetch_fn: Async function to fetch episode data
        """
        now = datetime.now()

        # Record access event
        event = AccessEvent(
            episode_id=episode_id,
            timestamp=now,
            tags=tags,
            embedding=embedding
        )
        self.recent_events.append(event)

        # Learn temporal patterns
        self.pattern_learner.learn_from_access(episode_id, now)

        # Build session context
        context = self.context_analyzer.build_context(list(self.recent_events))

        # Generate predictions
        predictions = self.prediction_engine.predict_next_episodes(
            current_episode_id=episode_id,
            context=context,
            candidate_pool=candidate_pool,
            k=self.prediction_k,
            min_confidence=self.min_confidence
        )

        # Background preload (non-blocking)
        if predictions:
            await self.preload_scheduler.preload_predictions(predictions, fetch_fn)

    def get_cached(self, episode_id: str) -> Optional[dict]:
        """Try to retrieve episode from predictive cache"""
        return self.preload_scheduler.get_cached(episode_id)

    def get_stats(self) -> dict:
        """Get comprehensive statistics"""
        return {
            'pattern_learner': {
                'bigram_patterns': len(self.pattern_learner.bigram_counts),
                'trigram_patterns': len(self.pattern_learner.trigram_counts),
                'history_size': len(self.pattern_learner.access_history)
            },
            'preload_scheduler': self.preload_scheduler.get_cache_stats()
        }


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == "__main__":
    # This would be integrated with NEXUS API
    # See main.py for actual integration

    print("LAB_007: Predictive Preloading Engine")
    print("=" * 60)
    print()
    print("✅ All components implemented:")
    print("  [1] TemporalPatternLearner - N-gram sequence learning")
    print("  [2] ContextAnalyzer - Session context analysis")
    print("  [3] PredictionEngine - Confidence-based prediction")
    print("  [4] PreloadingScheduler - Async background preloading")
    print()
    print("Ready for integration with NEXUS API.")

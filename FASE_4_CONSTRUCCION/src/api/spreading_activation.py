"""
LAB_005: Spreading Activation & Contextual Priming

Implements biological-inspired memory priming through semantic similarity networks
and activation spreading, reducing retrieval latency and improving context coherence.

Based on: Collins & Loftus (1975) Spreading Activation Theory
"""

import time
from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass, field
from collections import OrderedDict
import numpy as np
from datetime import datetime, timedelta


@dataclass
class ActivationState:
    """Tracks activation level and timing for an episode"""
    episode_uuid: str
    activation_level: float
    last_accessed: float  # timestamp
    access_count: int = 0
    source_episodes: Set[str] = field(default_factory=set)  # What activated this


@dataclass
class PrimedEpisode:
    """Cached episode with activation metadata"""
    uuid: str
    content: str
    embedding: np.ndarray
    activation: float
    primed_at: float
    source_uuid: str  # Episode that triggered priming


class SimilarityGraph:
    """
    Builds and maintains semantic similarity network between episodes.
    Uses embeddings to compute cosine similarity.
    """

    def __init__(self, similarity_threshold: float = 0.7):
        self.similarity_threshold = similarity_threshold
        self.graph: Dict[str, List[Tuple[str, float]]] = {}
        self.embeddings: Dict[str, np.ndarray] = {}

    def add_episode(self, uuid: str, embedding: np.ndarray):
        """Add new episode and compute similarities with existing ones"""
        self.embeddings[uuid] = embedding
        self.graph[uuid] = []

        # Compute similarities with all existing episodes
        for other_uuid, other_embedding in self.embeddings.items():
            if other_uuid == uuid:
                continue

            similarity = self._cosine_similarity(embedding, other_embedding)

            if similarity >= self.similarity_threshold:
                # Add bidirectional edge
                self.graph[uuid].append((other_uuid, similarity))
                self.graph[other_uuid].append((uuid, similarity))

    def get_related(self, uuid: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """Get top-K most similar episodes"""
        if uuid not in self.graph:
            return []

        # Sort by similarity descending
        related = sorted(self.graph[uuid], key=lambda x: x[1], reverse=True)
        return related[:top_k]

    def get_similarity(self, uuid1: str, uuid2: str) -> float:
        """Get similarity between two episodes"""
        if uuid1 not in self.embeddings or uuid2 not in self.embeddings:
            return 0.0

        return self._cosine_similarity(
            self.embeddings[uuid1],
            self.embeddings[uuid2]
        )

    @staticmethod
    def _cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Compute cosine similarity between two vectors"""
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return float(dot_product / (norm1 * norm2))


class ActivationManager:
    """
    Manages activation levels for all episodes with time-based decay.
    Implements spreading activation through the similarity network.
    """

    def __init__(self, decay_half_life: float = 30.0):
        self.decay_half_life = decay_half_life  # seconds
        self.activations: Dict[str, ActivationState] = {}

    def activate(self, uuid: str, level: float = 1.0, source: Optional[str] = None):
        """Set activation level for an episode"""
        now = time.time()

        if uuid in self.activations:
            state = self.activations[uuid]
            state.activation_level = max(state.activation_level, level)
            state.last_accessed = now
            state.access_count += 1
            if source:
                state.source_episodes.add(source)
        else:
            sources = {source} if source else set()
            self.activations[uuid] = ActivationState(
                episode_uuid=uuid,
                activation_level=level,
                last_accessed=now,
                access_count=1,
                source_episodes=sources
            )

    def get_activation(self, uuid: str) -> float:
        """Get current activation level with decay applied"""
        if uuid not in self.activations:
            return 0.0

        state = self.activations[uuid]
        elapsed = time.time() - state.last_accessed

        # Exponential decay: A(t) = A₀ * (0.5)^(t/half_life)
        decayed = state.activation_level * (0.5 ** (elapsed / self.decay_half_life))

        return decayed

    def spread_activation(
        self,
        source_uuid: str,
        similarity_graph: SimilarityGraph,
        top_k: int = 5,
        max_hops: int = 2
    ) -> List[Tuple[str, float]]:
        """
        Spread activation from source episode through similarity network.
        Returns list of (uuid, activation_level) tuples.
        """
        activated = []
        visited = {source_uuid}

        # Initialize with direct neighbors
        queue = [(source_uuid, 1.0, 0)]  # (uuid, activation, hop_count)

        while queue:
            current_uuid, current_activation, hops = queue.pop(0)

            if hops >= max_hops:
                continue

            # Get related episodes
            related = similarity_graph.get_related(current_uuid, top_k=top_k)

            for related_uuid, similarity in related:
                if related_uuid in visited:
                    continue

                visited.add(related_uuid)

                # Activation diminishes with distance and similarity
                new_activation = current_activation * similarity * 0.7  # 70% each hop

                if new_activation >= 0.2:  # Threshold to continue spreading
                    self.activate(related_uuid, new_activation, source=current_uuid)
                    activated.append((related_uuid, new_activation))
                    queue.append((related_uuid, new_activation, hops + 1))

        return activated

    def cleanup(self, threshold: float = 0.1):
        """Remove episodes with activation below threshold"""
        to_remove = [
            uuid for uuid, state in self.activations.items()
            if self.get_activation(uuid) < threshold
        ]

        for uuid in to_remove:
            del self.activations[uuid]

        return len(to_remove)


class PrimingCache:
    """
    Fast in-memory cache for primed episodes.
    Uses LRU eviction policy when cache is full.
    """

    def __init__(self, max_size: int = 50):
        self.max_size = max_size
        self.cache: OrderedDict[str, PrimedEpisode] = OrderedDict()
        self.hits = 0
        self.misses = 0

    def add(self, primed_episode: PrimedEpisode):
        """Add episode to cache, evicting LRU if needed"""
        if primed_episode.uuid in self.cache:
            # Move to end (most recently used)
            self.cache.move_to_end(primed_episode.uuid)
            # Update activation
            self.cache[primed_episode.uuid].activation = primed_episode.activation
        else:
            # Add new entry
            if len(self.cache) >= self.max_size:
                # Evict LRU
                self.cache.popitem(last=False)

            self.cache[primed_episode.uuid] = primed_episode

    def get(self, uuid: str) -> Optional[PrimedEpisode]:
        """Retrieve episode from cache"""
        if uuid in self.cache:
            self.hits += 1
            # Move to end (most recently used)
            self.cache.move_to_end(uuid)
            return self.cache[uuid]
        else:
            self.misses += 1
            return None

    def get_hit_rate(self) -> float:
        """Calculate cache hit rate"""
        total = self.hits + self.misses
        if total == 0:
            return 0.0
        return self.hits / total

    def clear(self):
        """Clear all cache entries"""
        self.cache.clear()

    def get_stats(self) -> Dict:
        """Get cache statistics"""
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": self.get_hit_rate(),
            "avg_activation": np.mean([e.activation for e in self.cache.values()]) if self.cache else 0.0
        }


class SpreadingActivationEngine:
    """
    Main LAB_005 engine integrating all components.
    Coordinates similarity graph, activation spreading, and priming cache.
    """

    def __init__(
        self,
        similarity_threshold: float = 0.7,
        decay_half_life: float = 30.0,
        cache_size: int = 50,
        top_k_related: int = 5,
        max_hops: int = 2
    ):
        self.similarity_graph = SimilarityGraph(similarity_threshold)
        self.activation_manager = ActivationManager(decay_half_life)
        self.priming_cache = PrimingCache(cache_size)

        self.top_k_related = top_k_related
        self.max_hops = max_hops

        # Statistics
        self.total_accesses = 0
        self.primed_accesses = 0
        self.avg_retrieval_time = 0.0

    def add_episode(self, uuid: str, content: str, embedding: np.ndarray):
        """Add new episode to the system"""
        self.similarity_graph.add_episode(uuid, embedding)

    def access_episode(self, uuid: str, content: str, embedding: np.ndarray) -> Dict:
        """
        Main access point: activates episode and spreads activation.
        Returns primed episodes that should be loaded.
        """
        start_time = time.time()

        # Activate the accessed episode
        self.activation_manager.activate(uuid, level=1.0)

        # Spread activation through network
        activated = self.activation_manager.spread_activation(
            source_uuid=uuid,
            similarity_graph=self.similarity_graph,
            top_k=self.top_k_related,
            max_hops=self.max_hops
        )

        # Load activated episodes into priming cache
        primed_uuids = []
        for activated_uuid, activation_level in activated:
            # Check if we have the episode data (in real system, fetch from DB)
            if activated_uuid in self.similarity_graph.embeddings:
                primed_episode = PrimedEpisode(
                    uuid=activated_uuid,
                    content=f"[Content for {activated_uuid}]",  # Placeholder
                    embedding=self.similarity_graph.embeddings[activated_uuid],
                    activation=activation_level,
                    primed_at=time.time(),
                    source_uuid=uuid
                )

                self.priming_cache.add(primed_episode)
                primed_uuids.append(activated_uuid)

        # Update statistics
        self.total_accesses += 1
        elapsed = (time.time() - start_time) * 1000  # ms
        self.avg_retrieval_time = (
            (self.avg_retrieval_time * (self.total_accesses - 1) + elapsed) /
            self.total_accesses
        )

        return {
            "uuid": uuid,
            "primed_episodes": primed_uuids,
            "activation_count": len(activated),
            "processing_time_ms": elapsed,
        }

    def try_primed_access(self, uuid: str) -> Optional[PrimedEpisode]:
        """Try to retrieve episode from priming cache"""
        result = self.priming_cache.get(uuid)

        if result:
            self.primed_accesses += 1

        return result

    def get_statistics(self) -> Dict:
        """Get comprehensive statistics"""
        return {
            "total_accesses": self.total_accesses,
            "primed_accesses": self.primed_accesses,
            "priming_effectiveness": (
                self.primed_accesses / self.total_accesses
                if self.total_accesses > 0 else 0.0
            ),
            "avg_retrieval_time_ms": self.avg_retrieval_time,
            "cache_stats": self.priming_cache.get_stats(),
            "active_episodes": len(self.activation_manager.activations),
            "similarity_graph_size": len(self.similarity_graph.graph),
        }

    def cleanup(self):
        """Perform maintenance: decay cleanup"""
        removed = self.activation_manager.cleanup(threshold=0.1)
        return {"removed_activations": removed}


# Example usage and testing
if __name__ == "__main__":
    print("🧠 LAB_005: Spreading Activation Engine - Test")
    print("=" * 60)

    # Create engine
    engine = SpreadingActivationEngine(
        similarity_threshold=0.7,
        decay_half_life=30.0,
        cache_size=50,
        top_k_related=5,
        max_hops=2
    )

    # Simulate episodes with random embeddings
    print("\n📝 Adding episodes...")
    episodes = []
    for i in range(20):
        uuid = f"episode_{i:03d}"
        content = f"This is episode {i} about topic {i % 5}"
        # Random embedding (in real system, from sentence transformer)
        embedding = np.random.randn(384)
        embedding = embedding / np.linalg.norm(embedding)  # normalize

        engine.add_episode(uuid, content, embedding)
        episodes.append((uuid, content, embedding))

    print(f"✅ Added {len(episodes)} episodes")

    # Access an episode and watch activation spread
    print("\n🔥 Accessing episode_005...")
    result = engine.access_episode(
        episodes[5][0],
        episodes[5][1],
        episodes[5][2]
    )

    print(f"✅ Primed {result['activation_count']} related episodes")
    print(f"⚡ Processing time: {result['processing_time_ms']:.2f}ms")
    print(f"📋 Primed UUIDs: {result['primed_episodes'][:3]}...")

    # Try accessing a primed episode
    print("\n⚡ Trying primed access for episode_001...")
    primed = engine.try_primed_access("episode_001")
    if primed:
        print(f"✅ Cache HIT! Activation: {primed.activation:.3f}")
    else:
        print("❌ Cache MISS")

    # Show statistics
    print("\n📊 Final Statistics:")
    stats = engine.get_statistics()
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.3f}")
        else:
            print(f"  {key}: {value}")

    print("\n🎯 LAB_005 Test Complete!")

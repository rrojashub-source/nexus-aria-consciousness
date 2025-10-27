"""
LAB_004: Curiosity-Driven Memory - Novelty Detection System

Implements neuroscience-backed novelty detection for episodic memories.

Research basis:
- Schultz (1997): Dopamine prediction error signaling
- Lisman & Grace (2005): Hippocampal-VTA novelty loop
- Yassa & Stark (2011): Pattern separation for optimal novelty
- Groch et al. (2017): Sleep preferentially replays novel episodes (5.8x)
- Hyman et al. (2006): Emotional surprise triggers consolidation
- Bubic et al. (2010): Sequence prediction violation
- Ranganath & Ritchey (2012): Contextual schema mismatch

Author: NEXUS (Claude Code)
Date: October 27, 2025
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import numpy as np
from scipy.spatial.distance import cosine
from sklearn.cluster import KMeans


# =====================================================================
# DATA STRUCTURES
# =====================================================================

@dataclass
class Episode:
    """Episode representation for novelty detection"""
    episode_id: str
    content: str
    embedding: List[float]
    created_at: datetime
    somatic_7d: Dict[str, float]
    emotional_8d: Optional[Dict[str, float]] = None
    metadata: Optional[Dict[str, Any]] = None
    salience_score: Optional[float] = None
    novelty_score: Optional[float] = None


@dataclass
class BaselineModels:
    """Container for all baseline models"""
    semantic_clusters: Dict[str, Any]
    emotional_baseline: Dict[str, float]
    sequence_patterns: Dict[str, Any]
    context_content: Dict[str, Any]
    created_at: datetime
    episodes_trained: int


@dataclass
class NoveltyBreakdown:
    """Detailed breakdown of novelty components"""
    semantic_novelty: float
    emotional_surprise: float
    pattern_violation: float
    contextual_mismatch: float
    total_novelty: float


# =====================================================================
# BASELINE MODEL BUILDING
# =====================================================================

def build_semantic_clusters(embeddings: List[List[float]], n_clusters: int = 10) -> Tuple[List[List[float]], List[int]]:
    """
    Cluster historical embeddings to find semantic centroids

    Research: Yassa & Stark (2011) - Pattern separation
    Optimal novelty at 0.6-0.8 distance from known patterns

    Args:
        embeddings: List of 1536-dim vectors
        n_clusters: Number of clusters (default 10)

    Returns:
        centroids: List of cluster centers
        labels: Cluster assignment for each embedding
    """
    if len(embeddings) < n_clusters:
        n_clusters = max(1, len(embeddings) // 2)

    embeddings_array = np.array(embeddings)

    # K-means clustering
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = kmeans.fit_predict(embeddings_array)
    centroids = kmeans.cluster_centers_.tolist()

    return centroids, labels.tolist()


def build_emotional_baseline(episodes: List[Episode]) -> Dict[str, Any]:
    """
    Calculate normal emotional state distributions

    Research: Hyman et al. (2006) - Emotional transitions
    Transitions >2 std trigger dopamine surge

    Args:
        episodes: Historical episodes with somatic_7d data

    Returns:
        stats: Dictionary with mean/std for valence/arousal
    """
    if not episodes:
        return {
            'valence_mean': 0.0,
            'valence_std': 0.3,
            'arousal_mean': 0.5,
            'arousal_std': 0.25,
            'typical_transitions': {
                'small': 0.15,
                'medium': 0.30,
                'large': 0.60
            }
        }

    valences = [ep.somatic_7d.get('valence', 0.0) for ep in episodes if ep.somatic_7d]
    arousals = [ep.somatic_7d.get('arousal', 0.5) for ep in episodes if ep.somatic_7d]

    if not valences:
        valences = [0.0]
    if not arousals:
        arousals = [0.5]

    # Calculate distributions
    stats = {
        'valence_mean': float(np.mean(valences)),
        'valence_std': float(np.std(valences)) if len(valences) > 1 else 0.3,
        'arousal_mean': float(np.mean(arousals)),
        'arousal_std': float(np.std(arousals)) if len(arousals) > 1 else 0.25
    }

    # Learn typical transition magnitudes
    transitions = []
    for i in range(1, len(valences)):
        delta = abs(valences[i] - valences[i-1])
        transitions.append(delta)

    if transitions:
        stats['typical_transitions'] = {
            'small': float(np.percentile(transitions, 50)),   # Median
            'medium': float(np.percentile(transitions, 75)),  # 75th percentile
            'large': float(np.percentile(transitions, 95))    # 95th percentile
        }
    else:
        stats['typical_transitions'] = {
            'small': 0.15,
            'medium': 0.30,
            'large': 0.60
        }

    return stats


def classify_episode_type(episode: Episode) -> str:
    """
    Infer episode type from content/tags

    Heuristics:
    - Contains "bug", "error", "debug" → "debugging"
    - Contains "meeting", "discussion" → "meeting"
    - Contains "test", "pytest" → "testing"
    - Contains "deploy", "ship" → "deployment"
    - Contains "breakthrough", "insight" → "breakthrough"
    - Contains "document", "write" → "documentation"
    - Contains "implement", "code" → "coding"
    - Contains "research", "learn" → "learning"

    Args:
        episode: Episode to classify

    Returns:
        Episode type string
    """
    content_lower = episode.content.lower()

    # Priority order matters
    if any(word in content_lower for word in ['breakthrough', 'insight', 'eureka', 'aha']):
        return 'breakthrough'
    elif any(word in content_lower for word in ['bug', 'error', 'debug', 'fix', 'issue']):
        return 'debugging'
    elif any(word in content_lower for word in ['test', 'pytest', 'unittest', 'testing']):
        return 'testing'
    elif any(word in content_lower for word in ['deploy', 'ship', 'release', 'production']):
        return 'deployment'
    elif any(word in content_lower for word in ['meeting', 'discussion', 'standup', 'sync']):
        return 'meeting'
    elif any(word in content_lower for word in ['document', 'write', 'readme', 'docs']):
        return 'documentation'
    elif any(word in content_lower for word in ['implement', 'code', 'coding', 'develop']):
        return 'coding'
    elif any(word in content_lower for word in ['research', 'learn', 'study', 'investigate']):
        return 'learning'
    elif any(word in content_lower for word in ['review', 'audit', 'analyze', 'analysis']):
        return 'review'
    else:
        return 'other'


def build_sequence_model(episodes: List[Episode], n: int = 2) -> Dict[str, Any]:
    """
    Learn common episode type sequences (bigrams)

    Research: Bubic et al. (2010) - Prediction violation
    Unexpected sequences trigger dopamine surge

    Args:
        episodes: Ordered list of episodes (chronological)
        n: N-gram size (2 = bigrams)

    Returns:
        Dictionary with transition probabilities and episode types
    """
    if not episodes:
        return {
            'transitions': {},
            'n': n,
            'episode_types': []
        }

    # Extract episode types
    types = [classify_episode_type(ep) for ep in episodes]

    # Count bigrams
    bigrams = defaultdict(Counter)
    for i in range(len(types) - 1):
        current, next_type = types[i], types[i+1]
        bigrams[current][next_type] += 1

    # Convert to probabilities
    transitions = {}
    for current, next_counts in bigrams.items():
        total = sum(next_counts.values())
        for next_type, count in next_counts.items():
            transitions[(current, next_type)] = count / total

    # Get unique episode types
    unique_types = sorted(list(set(types)))

    return {
        'transitions': transitions,
        'n': n,
        'episode_types': unique_types
    }


def build_context_model(episodes: List[Episode]) -> Dict[str, Any]:
    """
    Learn what content is typical for each context

    Research: Ranganath & Ritchey (2012) - Schema mismatch
    Context-content violations trigger stronger encoding

    Args:
        episodes: Historical episodes with context metadata

    Returns:
        Dictionary with context profiles (expected content centroids)
    """
    if not episodes:
        return {'profiles': {}}

    # Group episodes by context
    context_groups = defaultdict(list)
    for ep in episodes:
        context = ep.metadata.get('context', 'unknown') if ep.metadata else 'unknown'
        if ep.embedding:
            context_groups[context].append(ep.embedding)

    # For each context, find typical content centroids
    context_profiles = {}
    for context, embeddings in context_groups.items():
        if len(embeddings) >= 5:  # Need minimum data
            # Cluster into 3 typical content types per context
            n_clusters = min(3, len(embeddings) // 2)
            if n_clusters >= 1:
                embeddings_array = np.array(embeddings)
                kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
                kmeans.fit(embeddings_array)
                context_profiles[context] = kmeans.cluster_centers_.tolist()

    return {'profiles': context_profiles}


# =====================================================================
# NOVELTY SCORING FUNCTIONS
# =====================================================================

def calculate_semantic_novelty(episode_embedding: List[float],
                               cluster_centroids: List[List[float]]) -> float:
    """
    Measure semantic distance from established clusters

    Research: Yassa & Stark (2011) - Pattern separation
    Optimal novelty: 0.5-0.7 distance (novel but connected)

    Args:
        episode_embedding: 1536-dim vector for new episode
        cluster_centroids: List of cluster centers

    Returns:
        semantic_novelty: 0.0 (very familiar) to 1.0 (very novel)
    """
    if not cluster_centroids or not episode_embedding:
        return 0.5  # Default: moderate novelty if no baseline

    # Calculate distance to each cluster
    distances = []
    for centroid in cluster_centroids:
        try:
            dist = cosine(episode_embedding, centroid)
            distances.append(dist)
        except:
            continue

    if not distances:
        return 0.5

    # Use minimum distance (nearest cluster)
    min_distance = min(distances)

    # Normalize to 0-1 scale
    # Distance 0.0 = perfect match (novelty 0.0)
    # Distance 0.5+ = very far (novelty 1.0)
    # Based on Yassa & Stark: optimal novelty ~0.6
    semantic_novelty = min(min_distance / 0.5, 1.0)

    return float(semantic_novelty)


def calculate_emotional_surprise(current_emotional_state: Dict[str, float],
                                 recent_history: List[Episode],
                                 baseline_stats: Dict[str, Any]) -> float:
    """
    Detect unexpected emotional state changes

    Research: Hyman et al. (2006) - Emotional transitions
    Transition >2 std = dopamine surge

    Args:
        current_emotional_state: somatic_7d dict with valence/arousal
        recent_history: Last 6 hours of episodes
        baseline_stats: Learned mean/std from baseline

    Returns:
        emotional_surprise: 0.0 (expected) to 1.0 (very surprising)
    """
    current_valence = current_emotional_state.get('valence', 0.0)

    # Get recent valence trajectory
    if len(recent_history) >= 3:
        recent_valences = [
            ep.somatic_7d.get('valence', 0.0)
            for ep in recent_history[-6:]
            if ep.somatic_7d
        ]

        if recent_valences:
            expected_valence = np.mean(recent_valences)
            local_std = np.std(recent_valences) if len(recent_valences) > 1 else baseline_stats.get('valence_std', 0.3)
            local_std = max(local_std, 0.01)  # Avoid div by zero
        else:
            expected_valence = baseline_stats.get('valence_mean', 0.0)
            local_std = baseline_stats.get('valence_std', 0.3)
    else:
        # Fallback to baseline
        expected_valence = baseline_stats.get('valence_mean', 0.0)
        local_std = baseline_stats.get('valence_std', 0.3)

    # Calculate deviation (prediction error)
    deviation = abs(current_valence - expected_valence)
    z_score = deviation / local_std

    # Normalize: 2+ std deviations = maximal surprise
    # Based on Hyman: transitions >2 std trigger dopamine
    emotional_surprise = min(z_score / 2.0, 1.0)

    return float(emotional_surprise)


def calculate_pattern_violation(episode_type: str,
                                previous_types: List[str],
                                sequence_model: Dict[Tuple[str, str], float]) -> float:
    """
    Detect when episode type violates expected sequence

    Research: Bubic et al. (2010) - Prediction violation
    Unexpected continuation = dopamine surge

    Args:
        episode_type: Current episode type (inferred)
        previous_types: Last 3 episode types
        sequence_model: Learned bigram probabilities

    Returns:
        pattern_violation: 0.0 (expected) to 1.0 (very unexpected)
    """
    if not previous_types:
        return 0.0  # No history to violate

    # Get expected next type distribution
    previous_type = previous_types[-1]

    # Lookup probability P(current | previous)
    transition_key = (previous_type, episode_type)
    probability = sequence_model.get(transition_key, 0.01)  # Default: rare

    # Low probability = high violation
    # P=1.0 → violation=0.0 (fully expected)
    # P=0.0 → violation=1.0 (never seen before)
    pattern_violation = 1.0 - probability

    return float(pattern_violation)


def calculate_contextual_mismatch(episode_embedding: List[float],
                                  episode_context: str,
                                  context_model: Dict[str, List[List[float]]]) -> float:
    """
    Detect when content doesn't match expected context

    Research: Ranganath & Ritchey (2012) - Schema mismatch
    Office + elephant = high mismatch = strong encoding

    Args:
        episode_embedding: Content vector
        episode_context: Context label (e.g., 'technical_meeting')
        context_model: Expected content centroids per context

    Returns:
        contextual_mismatch: 0.0 (fits context) to 1.0 (doesn't fit)
    """
    if not episode_embedding or not context_model:
        return 0.0  # Can't judge mismatch without data

    # Get expected content centroids for this context
    expected_centroids = context_model.get(episode_context, [])

    if not expected_centroids:
        return 0.0  # Unknown context, can't judge mismatch

    # Calculate similarity to each expected centroid
    similarities = []
    for centroid in expected_centroids:
        try:
            similarity = 1.0 - cosine(episode_embedding, centroid)
            similarities.append(similarity)
        except:
            continue

    if not similarities:
        return 0.0

    # Use maximum similarity (best match to expected content)
    max_similarity = max(similarities)

    # Low similarity = high mismatch
    contextual_mismatch = 1.0 - max_similarity

    # Clamp to 0-1
    contextual_mismatch = max(0.0, min(1.0, contextual_mismatch))

    return float(contextual_mismatch)


def calculate_novelty_score(episode: Episode,
                            recent_history: List[Episode],
                            baseline_models: BaselineModels) -> Tuple[float, NoveltyBreakdown]:
    """
    Master function: Calculate composite novelty score

    Weights based on neuroscience research:
    - Semantic: 30% (Yassa & Stark - pattern separation)
    - Emotional: 25% (Hyman - emotional transitions)
    - Pattern: 25% (Bubic - sequence prediction)
    - Context: 20% (Ranganath - schema mismatch)

    Args:
        episode: New episode to score
        recent_history: Last 6 hours of episodes
        baseline_models: All baseline models

    Returns:
        novelty_score: 0.0 to 1.0
        breakdown: NoveltyBreakdown with individual components
    """
    # Extract baseline models
    semantic_clusters = baseline_models.semantic_clusters.get('centroids', [])
    emotional_baseline = baseline_models.emotional_baseline
    sequence_model = baseline_models.sequence_patterns.get('transitions', {})
    context_model = baseline_models.context_content.get('profiles', {})

    # Calculate each component
    semantic_novelty = calculate_semantic_novelty(
        episode.embedding,
        semantic_clusters
    )

    emotional_surprise = calculate_emotional_surprise(
        episode.somatic_7d,
        recent_history,
        emotional_baseline
    )

    # Infer episode type
    episode_type = classify_episode_type(episode)
    previous_types = [classify_episode_type(ep) for ep in recent_history[-3:]]

    pattern_violation = calculate_pattern_violation(
        episode_type,
        previous_types,
        sequence_model
    )

    contextual_mismatch = calculate_contextual_mismatch(
        episode.embedding,
        episode.metadata.get('context', 'unknown') if episode.metadata else 'unknown',
        context_model
    )

    # Weighted composite
    novelty_score = (
        semantic_novelty * 0.30 +
        emotional_surprise * 0.25 +
        pattern_violation * 0.25 +
        contextual_mismatch * 0.20
    )

    # Create breakdown
    breakdown = NoveltyBreakdown(
        semantic_novelty=round(semantic_novelty, 3),
        emotional_surprise=round(emotional_surprise, 3),
        pattern_violation=round(pattern_violation, 3),
        contextual_mismatch=round(contextual_mismatch, 3),
        total_novelty=round(novelty_score, 3)
    )

    return float(novelty_score), breakdown


# =====================================================================
# NOVELTY DETECTOR CLASS
# =====================================================================

class NoveltyDetector:
    """
    Main class for novelty detection and baseline model management

    Usage:
        detector = NoveltyDetector(db_connection)
        detector.build_baseline_models()  # One-time setup

        novelty, breakdown = detector.score_episode(new_episode)
    """

    def __init__(self, db_conn=None):
        """
        Initialize novelty detector

        Args:
            db_conn: Database connection for baseline storage (optional)
        """
        self.db_conn = db_conn
        self.baseline_models: Optional[BaselineModels] = None

    def build_baseline_models(self, episodes: List[Episode]) -> BaselineModels:
        """
        Build all baseline models from historical episodes

        Args:
            episodes: Historical episodes (30-60 days recommended)

        Returns:
            BaselineModels object with all models
        """
        print(f"Building baseline models from {len(episodes)} episodes...")

        # 1. Semantic clusters
        embeddings = [ep.embedding for ep in episodes if ep.embedding]
        centroids, labels = build_semantic_clusters(embeddings)

        semantic_model = {
            'centroids': centroids,
            'n_clusters': len(centroids),
            'trained_on_episodes': len(embeddings)
        }

        # 2. Emotional baseline
        emotional_model = build_emotional_baseline(episodes)

        # 3. Sequence patterns
        sequence_model = build_sequence_model(episodes)

        # 4. Context-content model
        context_model = build_context_model(episodes)

        # Create baseline models object
        baseline_models = BaselineModels(
            semantic_clusters=semantic_model,
            emotional_baseline=emotional_model,
            sequence_patterns=sequence_model,
            context_content=context_model,
            created_at=datetime.now(),
            episodes_trained=len(episodes)
        )

        self.baseline_models = baseline_models

        print(f"✅ Baseline models built:")
        print(f"   - {len(centroids)} semantic clusters")
        print(f"   - {len(sequence_model['episode_types'])} episode types")
        print(f"   - {len(context_model['profiles'])} context profiles")

        return baseline_models

    def score_episode(self, episode: Episode, recent_history: List[Episode]) -> Tuple[float, NoveltyBreakdown]:
        """
        Calculate novelty score for a new episode

        Args:
            episode: New episode to score
            recent_history: Recent episodes (last 6 hours)

        Returns:
            novelty_score: 0.0 to 1.0
            breakdown: Component breakdown
        """
        if not self.baseline_models:
            raise ValueError("Baseline models not loaded. Call build_baseline_models() first.")

        return calculate_novelty_score(episode, recent_history, self.baseline_models)

    def refresh_baselines(self, episodes: List[Episode]):
        """
        Refresh baseline models with new data (weekly recommended)

        Args:
            episodes: Recent episodes (60-day rolling window)
        """
        print(f"Refreshing baseline models with {len(episodes)} episodes...")
        self.build_baseline_models(episodes)
        print("✅ Baselines refreshed")


# =====================================================================
# HELPER FUNCTIONS
# =====================================================================

def get_primary_surprise_source(breakdown: NoveltyBreakdown) -> str:
    """
    Identify which component contributed most to surprise

    Args:
        breakdown: NoveltyBreakdown object

    Returns:
        Primary source name ('semantic', 'emotional', 'pattern', 'contextual')
    """
    components = {
        'semantic': breakdown.semantic_novelty,
        'emotional': breakdown.emotional_surprise,
        'pattern': breakdown.pattern_violation,
        'contextual': breakdown.contextual_mismatch
    }

    return max(components, key=components.get)


# =====================================================================
# TESTING UTILITIES
# =====================================================================

def validate_novelty_detector(detector: NoveltyDetector, test_episodes: List[Episode]) -> Dict[str, Any]:
    """
    Validate novelty detector on test episodes

    Args:
        detector: Trained NoveltyDetector instance
        test_episodes: Episodes to test on

    Returns:
        Validation metrics
    """
    scores = []
    breakdowns = []

    for i, ep in enumerate(test_episodes):
        recent = test_episodes[max(0, i-10):i]
        score, breakdown = detector.score_episode(ep, recent)
        scores.append(score)
        breakdowns.append(breakdown)

    return {
        'mean_novelty': float(np.mean(scores)),
        'std_novelty': float(np.std(scores)),
        'high_novelty_count': sum(1 for s in scores if s > 0.7),
        'low_novelty_count': sum(1 for s in scores if s < 0.3),
        'scores': scores,
        'breakdowns': breakdowns
    }


if __name__ == "__main__":
    print("LAB_004 NoveltyDetector - Ready for deployment")
    print("Research-backed novelty detection for curiosity-driven memory consolidation")

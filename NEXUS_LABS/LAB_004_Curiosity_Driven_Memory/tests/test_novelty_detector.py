#!/usr/bin/env python3
"""
LAB_004 Novelty Detector - Functional Tests

Tests the novelty detection system with synthetic and real data.

Author: NEXUS (Claude Code)
Date: October 27, 2025
"""

import sys
import os
import numpy as np
from datetime import datetime, timedelta

# Add implementation path
sys.path.insert(0, '/mnt/d/01_PROYECTOS_ACTIVOS/CEREBRO_MASTER_NEXUS_001/NEXUS_LABS/LAB_004_Curiosity_Driven_Memory/implementation')

from novelty_detector import (
    NoveltyDetector,
    Episode,
    build_semantic_clusters,
    build_emotional_baseline,
    build_sequence_model,
    build_context_model,
    calculate_semantic_novelty,
    calculate_emotional_surprise,
    calculate_pattern_violation,
    calculate_contextual_mismatch,
    classify_episode_type
)


def test_imports():
    """Test that all imports work"""
    print("✅ Test 1: Imports successful")
    return True


def test_episode_type_classification():
    """Test episode type classification"""
    print("\n🧪 Test 2: Episode Type Classification")

    test_cases = [
        ("Fixed critical bug in authentication", "debugging"),
        ("Implemented new user dashboard feature", "coding"),
        ("Team standup meeting discussion", "meeting"),
        ("Breakthrough insight on quantum approach", "breakthrough"),
        ("Running pytest on test suite", "testing"),
        ("Deployed to production successfully", "deployment"),
        ("Writing README documentation", "documentation"),
        ("Researching neural network architectures", "learning"),
    ]

    passed = 0
    for content, expected_type in test_cases:
        ep = Episode(
            episode_id="test",
            content=content,
            embedding=[],
            created_at=datetime.now(),
            somatic_7d={'valence': 0.0, 'arousal': 0.5},
            emotional_8d={}
        )

        result = classify_episode_type(ep)
        status = "✅" if result == expected_type else "❌"
        print(f"  {status} '{content[:40]}...' → {result} (expected: {expected_type})")

        if result == expected_type:
            passed += 1

    print(f"\n  Result: {passed}/{len(test_cases)} passed")
    return passed == len(test_cases)


def test_semantic_clustering():
    """Test semantic clustering on synthetic embeddings"""
    print("\n🧪 Test 3: Semantic Clustering")

    # Generate 30 synthetic embeddings (1536 dimensions)
    np.random.seed(42)
    embeddings = []

    # Create 3 clusters
    for cluster_id in range(3):
        cluster_center = np.random.randn(1536) * 0.1 + cluster_id * 2.0
        for i in range(10):
            noise = np.random.randn(1536) * 0.05
            embedding = cluster_center + noise
            embeddings.append(embedding.tolist())

    # Build clusters
    centroids, labels = build_semantic_clusters(embeddings, n_clusters=3)

    print(f"  ✅ Built {len(centroids)} clusters from {len(embeddings)} embeddings")
    print(f"  Cluster distribution: {np.bincount(labels).tolist()}")

    # Test novelty calculation
    # Similar to cluster 0
    similar_embedding = (centroids[0] + np.random.randn(1536) * 0.05).tolist()
    novelty_similar = calculate_semantic_novelty(similar_embedding, centroids)

    # Very different from all clusters
    different_embedding = (np.random.randn(1536) * 5.0).tolist()
    novelty_different = calculate_semantic_novelty(different_embedding, centroids)

    print(f"  Similar embedding novelty: {novelty_similar:.3f} (expected: <0.3)")
    print(f"  Different embedding novelty: {novelty_different:.3f} (expected: >0.7)")

    return novelty_similar < 0.3 and novelty_different > 0.7


def test_emotional_surprise():
    """Test emotional surprise detection"""
    print("\n🧪 Test 4: Emotional Surprise Detection")

    baseline = {
        'valence_mean': 0.0,
        'valence_std': 0.3,
        'arousal_mean': 0.5,
        'arousal_std': 0.2
    }

    # Recent history: neutral valence
    recent_history = []
    for i in range(5):
        ep = Episode(
            episode_id=f"test_{i}",
            content="routine work",
            embedding=[],
            created_at=datetime.now() - timedelta(hours=i),
            somatic_7d={'valence': 0.0, 'arousal': 0.5},
            emotional_8d={}
        )
        recent_history.append(ep)

    # Test 1: Small change (no surprise)
    current_state_small = {'valence': 0.1, 'arousal': 0.5}
    surprise_small = calculate_emotional_surprise(
        current_state_small,
        recent_history,
        baseline
    )

    # Test 2: Large change (high surprise)
    current_state_large = {'valence': 0.9, 'arousal': 0.8}
    surprise_large = calculate_emotional_surprise(
        current_state_large,
        recent_history,
        baseline
    )

    print(f"  Small valence change (0.0 → 0.1): {surprise_small:.3f} (expected: <0.3)")
    print(f"  Large valence change (0.0 → 0.9): {surprise_large:.3f} (expected: >0.7)")

    return surprise_small < 0.3 and surprise_large > 0.7


def test_pattern_violation():
    """Test pattern violation detection"""
    print("\n🧪 Test 5: Pattern Violation Detection")

    # Create sequence model
    sequence_model = {
        ('debugging', 'testing'): 0.75,      # Common
        ('debugging', 'breakthrough'): 0.05,  # Rare!
        ('testing', 'deployment'): 0.80,     # Common
        ('meeting', 'coding'): 0.50,         # Moderate
    }

    # Test 1: Expected transition (low violation)
    violation_expected = calculate_pattern_violation(
        'testing',
        ['debugging'],
        sequence_model
    )

    # Test 2: Unexpected transition (high violation)
    violation_unexpected = calculate_pattern_violation(
        'breakthrough',
        ['debugging'],
        sequence_model
    )

    print(f"  Expected transition (debugging → testing): {violation_expected:.3f} (expected: <0.3)")
    print(f"  Unexpected transition (debugging → breakthrough): {violation_unexpected:.3f} (expected: >0.9)")

    return violation_expected < 0.3 and violation_unexpected > 0.9


def test_novelty_detector_integration():
    """Test full NoveltyDetector workflow"""
    print("\n🧪 Test 6: NoveltyDetector Full Workflow")

    # Create synthetic episodes
    np.random.seed(42)
    episodes = []

    for i in range(30):
        # Generate random embedding
        embedding = np.random.randn(1536).tolist()

        # Alternate between routine and breakthrough episodes
        if i % 10 == 9:  # Every 10th episode is a breakthrough
            content = f"Breakthrough insight #{i//10}"
            valence = 0.8
            episode_type = "breakthrough"
        else:
            content = f"Routine debugging task #{i}"
            valence = -0.1
            episode_type = "debugging"

        ep = Episode(
            episode_id=f"test_ep_{i}",
            content=content,
            embedding=embedding,
            created_at=datetime.now() - timedelta(hours=30-i),
            somatic_7d={'valence': valence, 'arousal': 0.5},
            emotional_8d={
                'joy': 0.7 if episode_type == "breakthrough" else 0.3,
                'trust': 0.5,
                'fear': 0.1,
                'surprise': 0.8 if episode_type == "breakthrough" else 0.2,
                'sadness': 0.0,
                'disgust': 0.0,
                'anger': 0.1,
                'anticipation': 0.6
            },
            metadata={'context': 'debugging_session'},
            salience_score=0.8 if episode_type == "breakthrough" else 0.4
        )
        episodes.append(ep)

    print(f"  Created {len(episodes)} synthetic episodes")

    # Initialize detector and build baselines
    detector = NoveltyDetector()
    baseline_models = detector.build_baseline_models(episodes[:20])  # Use first 20 for baseline

    print(f"  ✅ Built baseline models from {baseline_models.episodes_trained} episodes")

    # Score remaining episodes
    test_episodes = episodes[20:]
    novelty_scores = []

    for ep in test_episodes:
        recent = [e for e in episodes if e.created_at < ep.created_at][-10:]
        score, breakdown = detector.score_episode(ep, recent)
        novelty_scores.append(score)

        if "Breakthrough" in ep.content:
            print(f"  Breakthrough episode: novelty={score:.3f}, breakdown={breakdown}")

    avg_novelty = np.mean(novelty_scores)
    print(f"\n  Average novelty score: {avg_novelty:.3f}")
    print(f"  High-novelty episodes (>0.7): {sum(1 for s in novelty_scores if s > 0.7)}")

    return True


def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("LAB_004 NOVELTY DETECTOR - FUNCTIONAL TESTS")
    print("=" * 60)

    tests = [
        ("Imports", test_imports),
        ("Episode Classification", test_episode_type_classification),
        ("Semantic Clustering", test_semantic_clustering),
        ("Emotional Surprise", test_emotional_surprise),
        ("Pattern Violation", test_pattern_violation),
        ("Full Integration", test_novelty_detector_integration)
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Test '{name}' failed with error: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))

    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {name}")

    print(f"\nTotal: {passed}/{total} tests passed ({passed/total*100:.1f}%)")

    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        return True
    else:
        print(f"\n⚠️ {total - passed} tests failed")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

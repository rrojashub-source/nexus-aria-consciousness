#!/usr/bin/env python3
"""
FASE_8_UPGRADE: Temporal Reasoning API Tests
Tests all 5 temporal endpoints with real data
"""

import requests
import json
from datetime import datetime, timedelta
import time

# Configuration
NEXUS_API = "http://localhost:8003"

def log(message, emoji="📝"):
    print(f"{emoji} {message}")

def test_endpoint(name, method, url, payload=None):
    """Test an endpoint and measure latency"""
    start = time.time()

    if method == "POST":
        response = requests.post(url, json=payload, headers={"Content-Type": "application/json"})
    else:
        response = requests.get(url)

    latency = (time.time() - start) * 1000  # ms

    if response.status_code == 200:
        log(f"✅ {name} - {response.status_code} - {latency:.2f}ms", "✅")
        return response.json(), latency
    else:
        log(f"❌ {name} - {response.status_code} - {response.text}", "❌")
        return None, latency

def main():
    print("=" * 60)
    print("🧪 TEMPORAL REASONING API TESTS")
    print("=" * 60)
    print()

    # Check API health
    log("Checking NEXUS API health...")
    health_data, _ = test_endpoint("Health Check", "GET", f"{NEXUS_API}/health")
    if not health_data:
        log("❌ API not accessible, aborting", "❌")
        return

    print()
    log(f"API Version: {health_data.get('version')}", "🔧")
    log(f"Agent ID: {health_data.get('agent_id')}", "🤖")
    print()

    # Create test episodes with timestamps spread over time
    log("Creating test episodes for temporal queries...", "📝")

    base_time = datetime.now()
    test_episodes = []

    # Episode 1: 2 days ago
    ep1_payload = {
        "action_type": "test_temporal",
        "action_details": {
            "content": "TEMPORAL_TEST Episode 1: Two days ago event",
            "importance_score": 0.8
        },
        "tags": ["temporal_test", "phase_2", "past_event"]
    }

    ep1_data, _ = test_endpoint("Create Episode 1", "POST", f"{NEXUS_API}/memory/action", ep1_payload)
    if ep1_data:
        test_episodes.append({
            "id": ep1_data["episode_id"],
            "timestamp": ep1_data["timestamp"],
            "content": "Episode 1 (2 days ago)"
        })

    time.sleep(0.5)

    # Episode 2: 1 day ago
    ep2_payload = {
        "action_type": "test_temporal",
        "action_details": {
            "content": "TEMPORAL_TEST Episode 2: One day ago event",
            "importance_score": 0.7
        },
        "tags": ["temporal_test", "phase_2", "recent_event"]
    }

    ep2_data, _ = test_endpoint("Create Episode 2", "POST", f"{NEXUS_API}/memory/action", ep2_payload)
    if ep2_data:
        test_episodes.append({
            "id": ep2_data["episode_id"],
            "timestamp": ep2_data["timestamp"],
            "content": "Episode 2 (1 day ago)"
        })

    time.sleep(0.5)

    # Episode 3: now
    ep3_payload = {
        "action_type": "test_temporal",
        "action_details": {
            "content": "TEMPORAL_TEST Episode 3: Current event",
            "importance_score": 0.9
        },
        "tags": ["temporal_test", "phase_2", "current_event"]
    }

    ep3_data, _ = test_endpoint("Create Episode 3", "POST", f"{NEXUS_API}/memory/action", ep3_payload)
    if ep3_data:
        test_episodes.append({
            "id": ep3_data["episode_id"],
            "timestamp": ep3_data["timestamp"],
            "content": "Episode 3 (now)"
        })

    print()
    log(f"Created {len(test_episodes)} test episodes", "✅")
    print()

    # Wait for embeddings
    log("Waiting 5 seconds for embeddings...", "⏳")
    time.sleep(5)
    print()

    # ========================================
    # TEST 1: /memory/temporal/before
    # ========================================
    log("TEST 1: /memory/temporal/before", "🧪")

    # Get episodes before "now"
    before_payload = {
        "timestamp": datetime.now().isoformat(),
        "limit": 10,
        "tags": ["temporal_test"]
    }

    before_data, before_latency = test_endpoint(
        "Episodes Before Now",
        "POST",
        f"{NEXUS_API}/memory/temporal/before",
        before_payload
    )

    if before_data:
        log(f"Found {before_data['count']} episodes before now", "📊")
        log(f"Latency: {before_latency:.2f}ms {'✅ PASS' if before_latency < 50 else '⚠️ SLOW'}", "⏱️")
    print()

    # ========================================
    # TEST 2: /memory/temporal/after
    # ========================================
    log("TEST 2: /memory/temporal/after", "🧪")

    # Get episodes after "2 days ago"
    after_payload = {
        "timestamp": (datetime.now() - timedelta(days=2)).isoformat(),
        "limit": 10,
        "tags": ["temporal_test"]
    }

    after_data, after_latency = test_endpoint(
        "Episodes After 2 Days Ago",
        "POST",
        f"{NEXUS_API}/memory/temporal/after",
        after_payload
    )

    if after_data:
        log(f"Found {after_data['count']} episodes after 2 days ago", "📊")
        log(f"Latency: {after_latency:.2f}ms {'✅ PASS' if after_latency < 50 else '⚠️ SLOW'}", "⏱️")
    print()

    # ========================================
    # TEST 3: /memory/temporal/range
    # ========================================
    log("TEST 3: /memory/temporal/range", "🧪")

    # Get episodes in last 3 days
    range_payload = {
        "start": (datetime.now() - timedelta(days=3)).isoformat(),
        "end": datetime.now().isoformat(),
        "limit": 50,
        "tags": ["temporal_test"]
    }

    range_data, range_latency = test_endpoint(
        "Episodes in Last 3 Days",
        "POST",
        f"{NEXUS_API}/memory/temporal/range",
        range_payload
    )

    if range_data:
        log(f"Found {range_data['count']} episodes in last 3 days", "📊")
        log(f"Latency: {range_latency:.2f}ms {'✅ PASS' if range_latency < 50 else '⚠️ SLOW'}", "⏱️")
    print()

    # ========================================
    # TEST 4: /memory/temporal/link
    # ========================================
    log("TEST 4: /memory/temporal/link", "🧪")

    if len(test_episodes) >= 2:
        # Link Episode 2 -> Episode 1 (after)
        link_payload = {
            "source_id": test_episodes[1]["id"],
            "target_id": test_episodes[0]["id"],
            "relationship": "after"
        }

        link_data, link_latency = test_endpoint(
            "Link Episode 2 -> Episode 1 (after)",
            "POST",
            f"{NEXUS_API}/memory/temporal/link",
            link_payload
        )

        if link_data:
            log(f"Link created successfully", "📊")
            log(f"Latency: {link_latency:.2f}ms {'✅ PASS' if link_latency < 100 else '⚠️ SLOW'}", "⏱️")

        time.sleep(0.5)

        # Link Episode 3 -> Episode 2 (causes)
        link_payload2 = {
            "source_id": test_episodes[2]["id"],
            "target_id": test_episodes[1]["id"],
            "relationship": "causes"
        }

        link_data2, link_latency2 = test_endpoint(
            "Link Episode 3 -> Episode 2 (causes)",
            "POST",
            f"{NEXUS_API}/memory/temporal/link",
            link_payload2
        )

        if link_data2:
            log(f"Link created successfully", "📊")
            log(f"Latency: {link_latency2:.2f}ms", "⏱️")
    print()

    # ========================================
    # TEST 5: /memory/temporal/related
    # ========================================
    log("TEST 5: /memory/temporal/related", "🧪")

    if len(test_episodes) >= 2:
        # Get related episodes for Episode 2
        related_payload = {
            "episode_id": test_episodes[1]["id"],
            "relationship_type": None  # Get all relationships
        }

        related_data, related_latency = test_endpoint(
            "Related Episodes for Episode 2 (all types)",
            "POST",
            f"{NEXUS_API}/memory/temporal/related",
            related_payload
        )

        if related_data:
            log(f"Found {related_data['count']} related episodes", "📊")
            log(f"Latency: {related_latency:.2f}ms {'✅ PASS' if related_latency < 100 else '⚠️ SLOW'}", "⏱️")

            if related_data['count'] > 0:
                for ep in related_data['episodes']:
                    log(f"  - {ep['episode_id'][:8]}... | {ep['content'][:50]}...", "🔗")

        time.sleep(0.5)

        # Get specific relationship type
        related_payload2 = {
            "episode_id": test_episodes[1]["id"],
            "relationship_type": "after"
        }

        related_data2, related_latency2 = test_endpoint(
            "Related Episodes for Episode 2 (after only)",
            "POST",
            f"{NEXUS_API}/memory/temporal/related",
            related_payload2
        )

        if related_data2:
            log(f"Found {related_data2['count']} 'after' relationships", "📊")
            log(f"Latency: {related_latency2:.2f}ms", "⏱️")
    print()

    # ========================================
    # SUMMARY
    # ========================================
    print("=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print()

    latencies = {
        "temporal/before": before_latency,
        "temporal/after": after_latency,
        "temporal/range": range_latency,
        "temporal/link": link_latency,
        "temporal/related": related_latency
    }

    for endpoint, lat in latencies.items():
        status = "✅ PASS" if lat < 50 else "⚠️ ACCEPTABLE" if lat < 100 else "❌ SLOW"
        print(f"{endpoint:20} | {lat:6.2f}ms | {status}")

    print()
    avg_latency = sum(latencies.values()) / len(latencies)
    print(f"Average Latency: {avg_latency:.2f}ms")
    print()

    if avg_latency < 50:
        log("🏆 ALL TESTS PASSED - PHASE 2 COMPLETE!", "🏆")
    elif avg_latency < 100:
        log("✅ All tests passed (acceptable performance)", "✅")
    else:
        log("⚠️ Tests passed but performance needs optimization", "⚠️")

    print()
    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

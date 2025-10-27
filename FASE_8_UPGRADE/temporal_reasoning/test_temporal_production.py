#!/usr/bin/env python3
"""
FASE_8_UPGRADE: Temporal Reasoning Production Testing
Tests temporal endpoints with real production data (543 episodes)
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
        return response.json(), latency, True
    else:
        log(f"❌ {name} - {response.status_code}", "❌")
        return None, latency, False

def main():
    print("=" * 80)
    print("🏭 TEMPORAL REASONING - PRODUCTION DATA TESTING")
    print("=" * 80)
    print()

    # Get stats
    stats_data, _, _ = test_endpoint("Stats", "GET", f"{NEXUS_API}/stats")
    if not stats_data:
        log("❌ Cannot get stats", "❌")
        return

    total_eps = stats_data["stats"]["total_episodes"]
    log(f"Total Episodes: {total_eps}", "📊")
    print()

    results = {}

    # ========================================
    # TEST 1: Temporal Range Performance
    # ========================================
    log("TEST 1: Temporal Range Queries (Different Time Windows)", "🧪")
    print()

    time_windows = [
        ("Last 24 hours", 1),
        ("Last 7 days", 7),
        ("Last 14 days", 14),
        ("Last 30 days", 30),
    ]

    for window_name, days in time_windows:
        start_time = datetime.now() - timedelta(days=days)
        end_time = datetime.now()

        payload = {
            "start": start_time.isoformat(),
            "end": end_time.isoformat(),
            "limit": 200
        }

        data, latency, success = test_endpoint(
            f"Range: {window_name}",
            "POST",
            f"{NEXUS_API}/memory/temporal/range",
            payload
        )

        if success and data:
            count = data["count"]
            log(f"  {window_name}: {count} episodes | {latency:.2f}ms {'✅' if latency < 50 else '⚠️'}", "📊")
            results[f"range_{days}d"] = {"count": count, "latency": latency}
        else:
            log(f"  {window_name}: FAILED", "❌")

    print()

    # ========================================
    # TEST 2: Tag Filtering Performance
    # ========================================
    log("TEST 2: Tag Filtering (milestone vs all)", "🧪")
    print()

    # Without tag filter
    payload_no_filter = {
        "start": (datetime.now() - timedelta(days=30)).isoformat(),
        "end": datetime.now().isoformat(),
        "limit": 200
    }

    data_no_filter, latency_no_filter, success = test_endpoint(
        "Range: No filter",
        "POST",
        f"{NEXUS_API}/memory/temporal/range",
        payload_no_filter
    )

    if success and data_no_filter:
        log(f"  No filter: {data_no_filter['count']} episodes | {latency_no_filter:.2f}ms", "📊")
        results["no_filter"] = {"count": data_no_filter["count"], "latency": latency_no_filter}

    # With tag filter (milestones)
    payload_with_filter = {
        "start": (datetime.now() - timedelta(days=30)).isoformat(),
        "end": datetime.now().isoformat(),
        "limit": 200,
        "tags": ["milestone"]
    }

    data_with_filter, latency_with_filter, success = test_endpoint(
        "Range: milestone filter",
        "POST",
        f"{NEXUS_API}/memory/temporal/range",
        payload_with_filter
    )

    if success and data_with_filter:
        log(f"  Milestone filter: {data_with_filter['count']} episodes | {latency_with_filter:.2f}ms", "📊")
        results["milestone_filter"] = {"count": data_with_filter["count"], "latency": latency_with_filter}

    print()

    # ========================================
    # TEST 3: Before/After Queries
    # ========================================
    log("TEST 3: Before/After Queries (Oct 18 spike: 261 episodes)", "🧪")
    print()

    # Oct 18 was the spike day (261 episodes)
    oct_18 = datetime(2025, 10, 18, 12, 0, 0)

    # Before Oct 18
    payload_before = {
        "timestamp": oct_18.isoformat(),
        "limit": 50
    }

    data_before, latency_before, success = test_endpoint(
        "Before Oct 18",
        "POST",
        f"{NEXUS_API}/memory/temporal/before",
        payload_before
    )

    if success and data_before:
        log(f"  Before Oct 18: {data_before['count']} episodes | {latency_before:.2f}ms", "📊")
        results["before_oct18"] = {"count": data_before["count"], "latency": latency_before}

    # After Oct 18
    payload_after = {
        "timestamp": oct_18.isoformat(),
        "limit": 50
    }

    data_after, latency_after, success = test_endpoint(
        "After Oct 18",
        "POST",
        f"{NEXUS_API}/memory/temporal/after",
        payload_after
    )

    if success and data_after:
        log(f"  After Oct 18: {data_after['count']} episodes | {latency_after:.2f}ms", "📊")
        results["after_oct18"] = {"count": data_after["count"], "latency": latency_after}

    print()

    # ========================================
    # TEST 4: Large Limit Performance
    # ========================================
    log("TEST 4: Large Limit Performance (100 vs 200 episodes)", "🧪")
    print()

    for limit in [100, 200]:
        payload = {
            "start": (datetime.now() - timedelta(days=30)).isoformat(),
            "end": datetime.now().isoformat(),
            "limit": limit
        }

        data, latency, success = test_endpoint(
            f"Limit {limit}",
            "POST",
            f"{NEXUS_API}/memory/temporal/range",
            payload
        )

        if success and data:
            log(f"  Limit {limit}: {data['count']} episodes | {latency:.2f}ms", "📊")
            results[f"limit_{limit}"] = {"count": data["count"], "latency": latency}

    print()

    # ========================================
    # TEST 5: Milestone Timeline
    # ========================================
    log("TEST 5: Milestone Timeline (Last 30 days)", "🧪")
    print()

    payload_milestones = {
        "start": (datetime.now() - timedelta(days=30)).isoformat(),
        "end": datetime.now().isoformat(),
        "limit": 50,
        "tags": ["milestone"]
    }

    data_milestones, latency_milestones, success = test_endpoint(
        "Milestone Timeline",
        "POST",
        f"{NEXUS_API}/memory/temporal/range",
        payload_milestones
    )

    if success and data_milestones:
        log(f"  Found {data_milestones['count']} milestones | {latency_milestones:.2f}ms", "📊")

        if data_milestones["count"] > 0:
            log(f"\n  Recent Milestones:", "🎯")
            for i, ep in enumerate(data_milestones["episodes"][:5]):
                created = ep["created_at"][:10]  # YYYY-MM-DD
                content_preview = ep["content"][:60]
                log(f"    {i+1}. [{created}] {content_preview}...", "  ")

    print()

    # ========================================
    # SUMMARY
    # ========================================
    print("=" * 80)
    print("📊 PRODUCTION TEST SUMMARY")
    print("=" * 80)
    print()

    all_latencies = [v["latency"] for v in results.values() if "latency" in v]

    if all_latencies:
        avg_latency = sum(all_latencies) / len(all_latencies)
        max_latency = max(all_latencies)
        min_latency = min(all_latencies)

        print(f"Average Latency: {avg_latency:.2f}ms")
        print(f"Min Latency:     {min_latency:.2f}ms")
        print(f"Max Latency:     {max_latency:.2f}ms")
        print()

        # Performance assessment
        if avg_latency < 20:
            log("🏆 EXCEPTIONAL - Average latency < 20ms", "🏆")
        elif avg_latency < 50:
            log("✅ EXCELLENT - Average latency < 50ms (target met)", "✅")
        elif avg_latency < 100:
            log("⚠️ ACCEPTABLE - Average latency < 100ms", "⚠️")
        else:
            log("❌ NEEDS OPTIMIZATION - Average latency > 100ms", "❌")

        print()
        print(f"Total Production Episodes: {total_eps}")
        print(f"Tests Run: {len(results)}")
        print()

    # ========================================
    # INDEX PERFORMANCE VALIDATION
    # ========================================
    log("INDEX VALIDATION", "🔍")
    print()

    # Check if latency scales linearly with result count
    range_tests = {k: v for k, v in results.items() if k.startswith("range_")}
    if len(range_tests) >= 2:
        latencies = [v["latency"] for v in range_tests.values()]
        counts = [v["count"] for v in range_tests.values()]

        # Calculate latency per episode
        latency_per_ep = [lat / max(cnt, 1) for lat, cnt in zip(latencies, counts)]
        avg_latency_per_ep = sum(latency_per_ep) / len(latency_per_ep)

        log(f"  Average latency per episode: {avg_latency_per_ep:.4f}ms", "📊")

        if avg_latency_per_ep < 0.1:
            log("  ✅ Index performance is excellent (sub-linear scaling)", "✅")
        else:
            log("  ⚠️ May benefit from index optimization", "⚠️")

    print()
    print("=" * 80)
    log("✅ Production testing complete!", "✅")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

#!/usr/bin/env python3
"""
Quick test script to populate A/B testing dashboard with sample data
"""

import requests
import random
import time
from datetime import datetime

API_URL = "http://localhost:8003"

def generate_control_metrics():
    """Generate realistic control (no LAB_005) metrics"""
    return {
        "variant": "control",
        "retrieval_time_ms": random.uniform(85, 110),  # Slower
        "cache_hit": random.random() < 0.12,  # ~12% hit rate
        "num_results": random.randint(2, 4),  # Fewer results
        "context_coherence": random.uniform(0.60, 0.72)  # Lower coherence
    }

def generate_treatment_metrics():
    """Generate realistic treatment (with LAB_005) metrics"""
    return {
        "variant": "treatment",
        "retrieval_time_ms": random.uniform(35, 55),  # Faster
        "cache_hit": random.random() < 0.45,  # ~45% hit rate
        "num_results": random.randint(5, 8),  # More results
        "context_coherence": random.uniform(0.82, 0.92),  # Higher coherence
        "primed_count": random.randint(3, 6)  # Primed episodes
    }

def record_metric(metric):
    """Record a metric via API"""
    try:
        response = requests.post(f"{API_URL}/ab-test/record", json=metric, timeout=5)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("🧪 A/B Testing Framework - Sample Data Generator")
    print("=" * 60)

    # Generate 50 samples for each variant
    samples_per_variant = 50

    print(f"\n📊 Generating {samples_per_variant} samples per variant...")

    control_success = 0
    treatment_success = 0

    for i in range(samples_per_variant):
        # Control
        control = generate_control_metrics()
        if record_metric(control):
            control_success += 1

        # Treatment
        treatment = generate_treatment_metrics()
        if record_metric(treatment):
            treatment_success += 1

        if (i + 1) % 10 == 0:
            print(f"  Progress: {i + 1}/{samples_per_variant} samples...")

        time.sleep(0.05)  # Small delay to spread timestamps

    print(f"\n✅ Completed!")
    print(f"   Control: {control_success}/{samples_per_variant} recorded")
    print(f"   Treatment: {treatment_success}/{samples_per_variant} recorded")

    # Fetch comparison
    print(f"\n📈 Fetching comparison...")
    try:
        response = requests.get(f"{API_URL}/ab-test/compare?hours_back=24", timeout=5)
        data = response.json()

        if data.get("success"):
            improvements = data.get("improvements", {})
            print(f"\n🎯 Results:")
            print(f"   Latency Reduction: {improvements.get('latency_reduction_percent', 0):.1f}%")
            print(f"   Cache Hit Rate: {improvements.get('cache_hit_rate_increase_percent', 0):.1f}%")
            print(f"   Coherence: {improvements.get('coherence_increase_percent', 0):.1f}%")
            print(f"   Primed Episodes: {improvements.get('avg_primed_episodes', 0):.1f}")
            print(f"\n   Recommendation: {data.get('recommendation')}")
        else:
            print(f"   ⚠️ {data.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"   ❌ Error fetching comparison: {e}")

    print(f"\n🌐 View dashboard: http://localhost:3000")
    print(f"   Navigate to '📊 Dashboard 2D' and scroll to A/B Testing section")

if __name__ == "__main__":
    main()

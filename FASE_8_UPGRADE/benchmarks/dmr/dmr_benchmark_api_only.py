#!/usr/bin/env python3
"""
DMR (Deep Memory Retrieval) Benchmark for NEXUS - API Only Version
Uses only NEXUS API instead of direct database access

Measures: How accurately NEXUS can retrieve specific information from episodic memory

Target: >94% accuracy (matching Zep state-of-the-art)
Baseline: MemGPT 93.4%
"""

import json
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import random
import time

# Configuration
NEXUS_API = "http://localhost:8003"

class DMRBenchmark:
    """Deep Memory Retrieval Benchmark - API Only"""

    def __init__(self):
        self.test_episodes = []
        self.queries = []
        self.results = {
            "total_queries": 0,
            "correct": 0,
            "incorrect": 0,
            "accuracy": 0.0,
            "details": []
        }

    def check_api_health(self):
        """Check if NEXUS API is accessible"""
        try:
            response = requests.get(f"{NEXUS_API}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ NEXUS API is healthy")
                print(f"   Version: {data.get('version', 'unknown')}")
                print(f"   Agent: {data.get('agent_id', 'unknown')}")
                return True
        except Exception as e:
            print(f"❌ NEXUS API not accessible: {e}")
            return False

    def generate_synthetic_dataset(self, num_episodes: int = 50):
        """
        Generate synthetic test dataset with guaranteed unique facts

        Uses sequential IDs to ensure each episode contains a completely unique fact
        """

        print(f"\n📝 Generating {num_episodes} synthetic test episodes with unique facts...")

        episodes = []
        base_time = datetime.now() - timedelta(days=30)

        for i in range(num_episodes):
            # Generate unique facts using sequential IDs
            # Each category gets a unique ID to prevent any overlap

            category = i % 5  # 5 categories

            if category == 0:  # Unique user stories
                user_id = f"user{i}"
                action_id = f"action{i}"
                content = f"DMR_TEST user_interaction: User {user_id} performed {action_id} successfully at timestamp {i}"
                tags = ["dmr_test", "user_interaction", user_id, action_id]

            elif category == 1:  # Unique system events
                service_id = f"service{i}"
                event_id = f"event{i}"
                content = f"DMR_TEST technical_event: Service {service_id} executed {event_id} at {base_time + timedelta(minutes=i*10)}"
                tags = ["dmr_test", "technical_event", service_id, event_id]

            elif category == 2:  # Unique project milestones
                project_id = f"project{i}"
                milestone_id = f"milestone{i}"
                content = f"DMR_TEST project_milestone: Project {project_id} reached {milestone_id} completion marker"
                tags = ["dmr_test", "project_milestone", project_id, milestone_id]

            elif category == 3:  # Unique error logs
                error_id = f"error{i}"
                user_id = f"user{i}_err"
                content = f"DMR_TEST error_log: Error {error_id} encountered by {user_id} during operation"
                tags = ["dmr_test", "error_log", error_id, user_id]

            else:  # Unique configurations
                config_id = f"config{i}"
                old_val = f"oldval{i}"
                new_val = f"newval{i}"
                content = f"DMR_TEST config_change: Configuration {config_id} changed from {old_val} to {new_val}"
                tags = ["dmr_test", "config_change", config_id]

            episodes.append({
                "content": content,
                "tags": tags,
                "importance": round(random.uniform(0.3, 1.0), 2),
                "timestamp_offset": i
            })

        self.test_episodes = episodes
        print(f"✅ Generated {len(episodes)} test episodes (all unique)")
        return episodes

    def insert_test_data(self):
        """Insert test episodes via NEXUS API"""
        print("\n📤 Inserting test data via NEXUS API...")

        inserted = 0
        failed = 0

        for i, episode in enumerate(self.test_episodes):
            try:
                payload = {
                    "action_type": "memory",
                    "action_details": {
                        "content": episode["content"],
                        "importance_score": episode["importance"]
                    },
                    "tags": episode["tags"]
                }

                response = requests.post(
                    f"{NEXUS_API}/memory/action",
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )

                if response.status_code == 200:
                    data = response.json()
                    episode["episode_id"] = data.get("episode_id")
                    inserted += 1
                    if (i + 1) % 20 == 0:
                        print(f"   Inserted {i+1}/{len(self.test_episodes)}...")
                else:
                    failed += 1
                    if failed <= 3:
                        print(f"   ❌ Failed to insert episode {i+1}: {response.status_code}")

                # Small delay to avoid overwhelming API
                time.sleep(0.05)

            except Exception as e:
                failed += 1
                if failed <= 3:
                    print(f"   ❌ Error inserting episode {i+1}: {e}")

        print(f"✅ Inserted {inserted}/{len(self.test_episodes)} episodes ({failed} failed)")
        return inserted > 0

    def generate_recall_queries(self, num_queries: int = 50):
        """Generate recall queries from test dataset"""
        print(f"\n❓ Generating {num_queries} recall queries...")

        queries = []

        # Use all episodes for queries (since they're all unique now)
        sampled = self.test_episodes[:min(num_queries, len(self.test_episodes))]

        for episode in sampled:
            content = episode["content"]

            # Parse content to create specific queries
            if "user_interaction:" in content:
                parts = content.split()
                user = parts[3]  # "User {user}"
                action = parts[5]  # "performed {action}"
                query = f"What action did {user} perform in DMR test?"
                expected = action

            elif "technical_event:" in content:
                parts = content.split()
                service = parts[3]  # "Service {service}"
                event = parts[5]  # "executed {event}"
                query = f"What event did {service} execute in DMR test?"
                expected = event

            elif "project_milestone:" in content:
                parts = content.split()
                project = parts[3]  # "Project {project}"
                milestone = parts[5]  # "reached {milestone}"
                query = f"What milestone did {project} reach in DMR test?"
                expected = milestone

            elif "error_log:" in content:
                parts = content.split()
                error = parts[3]  # "Error {error}"
                user = parts[6]  # "by {user}" - parts[6] not parts[7]!
                query = f"What error did {user} encounter in DMR test?"
                expected = error

            elif "config_change:" in content:
                parts = content.split()
                config = parts[3]  # "Configuration {config}"
                query = f"What configuration was {config} in DMR test?"
                expected = config

            else:
                continue

            queries.append({
                "query": query,
                "expected_answer": expected,
                "episode_id": episode.get("episode_id"),
                "full_content": content
            })

        self.queries = queries
        print(f"✅ Generated {len(queries)} queries")
        return queries

    def execute_query(self, query_text: str) -> str:
        """Execute semantic search query against NEXUS API"""
        try:
            response = requests.post(
                f"{NEXUS_API}/memory/search",
                json={"query": query_text, "limit": 3},
                headers={"Content-Type": "application/json"},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("results") and len(data["results"]) > 0:
                    return data["results"][0].get("content", "")

            return ""

        except Exception as e:
            print(f"❌ Query execution error: {e}")
            return ""

    def evaluate_answer(self, retrieved: str, expected: str) -> bool:
        """Evaluate if retrieved content contains expected answer"""
        return expected.lower() in retrieved.lower()

    def run_benchmark(self):
        """Run complete DMR benchmark"""
        print("\n" + "="*60)
        print("🚀 RUNNING DMR BENCHMARK")
        print("="*60 + "\n")

        correct = 0
        incorrect = 0
        details = []

        for i, query_item in enumerate(self.queries):
            query = query_item["query"]
            expected = query_item["expected_answer"]

            print(f"[{i+1}/{len(self.queries)}] {query}")

            # Execute query
            retrieved = self.execute_query(query)

            # Evaluate
            is_correct = self.evaluate_answer(retrieved, expected)

            if is_correct:
                correct += 1
                status = "✅"
            else:
                incorrect += 1
                status = "❌"

            print(f"           Expected: {expected} | Got: {retrieved[:60]}... {status}\n")

            details.append({
                "query": query,
                "expected": expected,
                "retrieved": retrieved[:200],
                "correct": is_correct
            })

        # Calculate accuracy
        total = len(self.queries)
        accuracy = (correct / total * 100) if total > 0 else 0

        self.results = {
            "total_queries": total,
            "correct": correct,
            "incorrect": incorrect,
            "accuracy": round(accuracy, 2),
            "timestamp": datetime.now().isoformat(),
            "details": details
        }

        return self.results

    def print_results(self):
        """Print benchmark results"""
        print("\n" + "="*60)
        print("📊 DMR BENCHMARK RESULTS")
        print("="*60 + "\n")

        r = self.results
        print(f"Total Queries:    {r['total_queries']}")
        print(f"Correct:          {r['correct']} ✅")
        print(f"Incorrect:        {r['incorrect']} ❌")
        print(f"\n🎯 ACCURACY:       {r['accuracy']}%\n")

        # Comparison with state-of-the-art
        print("Comparison with State-of-the-Art:")
        print(f"  Zep (SOTA 2025):  94.8%")
        print(f"  MemGPT (2023):    93.4%")
        print(f"  NEXUS (Today):    {r['accuracy']}%")

        if r['accuracy'] >= 94.8:
            print(f"\n🏆 NEXUS EXCEEDS STATE-OF-THE-ART! (+{r['accuracy'] - 94.8:.1f}%)")
        elif r['accuracy'] >= 93.4:
            print(f"\n✅ NEXUS MATCHES MemGPT BASELINE (+{r['accuracy'] - 93.4:.1f}%)")
        else:
            print(f"\n⚠️  NEXUS BELOW BASELINE (Gap: -{93.4 - r['accuracy']:.1f}%)")

        print("\n" + "="*60)

    def save_results(self, filepath: str):
        """Save results to JSON file"""
        with open(filepath, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\n💾 Results saved to: {filepath}")


def main():
    """Main execution"""
    benchmark = DMRBenchmark()

    print("="*60)
    print("DMR BENCHMARK FOR NEXUS - API ONLY VERSION")
    print("="*60)

    # 1. Check API health
    if not benchmark.check_api_health():
        print("\n❌ Cannot proceed without NEXUS API")
        return

    # 2. Generate synthetic dataset
    benchmark.generate_synthetic_dataset(num_episodes=50)

    # 3. Insert test data
    if not benchmark.insert_test_data():
        print("\n❌ Failed to insert test data")
        return

    # Wait for embeddings to be generated
    print("\n⏳ Waiting 20 seconds for embeddings to be generated...")
    time.sleep(20)  # 50 episodes @ ~3 sec/batch = ~20 sec total

    # 4. Generate queries
    benchmark.generate_recall_queries(num_queries=50)

    # 5. Run benchmark
    results = benchmark.run_benchmark()

    # 6. Print results
    benchmark.print_results()

    # 7. Save results
    results_file = f"dmr_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    benchmark.save_results(results_file)

    print("\n✅ DMR Benchmark complete!")
    print(f"📊 Accuracy: {results['accuracy']}%")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Benchmark interrupted by user")
    except Exception as e:
        print(f"\n❌ Benchmark failed: {e}")
        import traceback
        traceback.print_exc()

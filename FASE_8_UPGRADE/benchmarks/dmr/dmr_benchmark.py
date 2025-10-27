#!/usr/bin/env python3
"""
DMR (Deep Memory Retrieval) Benchmark for NEXUS
Based on MemGPT benchmark (arXiv:2310.08560)

Measures: How accurately NEXUS can retrieve specific information from episodic memory

Target: >94% accuracy (matching Zep state-of-the-art)
Baseline: MemGPT 93.4%
"""

import os
import json
import psycopg2
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import random

# Configuration
NEXUS_API = "http://localhost:8003"
DB_CONFIG = {
    "host": "localhost",
    "port": 5437,
    "database": "nexus_memory",
    "user": "nexus_superuser",
    "password": "RpKeuQhnwqMOA4iQPILQshWtwFj0P2hm"
}

class DMRBenchmark:
    """Deep Memory Retrieval Benchmark"""

    def __init__(self):
        self.db_conn = None
        self.test_episodes = []
        self.queries = []
        self.results = {
            "total_queries": 0,
            "correct": 0,
            "incorrect": 0,
            "accuracy": 0.0,
            "details": []
        }

    def connect_db(self):
        """Connect to NEXUS PostgreSQL database"""
        self.db_conn = psycopg2.connect(**DB_CONFIG)
        print("✅ Connected to NEXUS database")

    def generate_synthetic_dataset(self, num_episodes: int = 100):
        """
        Generate synthetic test dataset

        Categories:
        - User interactions (30%)
        - Technical events (25%)
        - Project milestones (20%)
        - Error logs (15%)
        - Configuration changes (10%)
        """

        print(f"📝 Generating {num_episodes} synthetic test episodes...")

        # User interactions
        users = ["ricardo", "diego_alcantara", "arlae_ortiz", "admin", "test_user"]
        actions = ["login", "logout", "create_project", "update_settings", "delete_item"]

        # Technical events
        services = ["nexus_api", "postgresql", "redis", "embeddings_worker", "grafana"]
        events = ["started", "stopped", "restarted", "crashed", "upgraded"]

        # Projects
        projects = ["biblioteca_moi", "central_power_solutions", "nexus_cerebro", "fase_8_upgrade"]
        milestones = ["started", "completed", "deployed", "tested", "documented"]

        # Errors
        error_types = ["authentication_failed", "database_timeout", "api_error", "memory_full", "connection_refused"]

        # Configurations
        config_items = ["cors_origin", "jwt_secret", "port", "host", "ssl_enabled"]

        episodes = []
        base_time = datetime.now() - timedelta(days=30)

        for i in range(num_episodes):
            # Randomize category
            category_roll = random.random()

            if category_roll < 0.30:  # User interactions (30%)
                user = random.choice(users)
                action = random.choice(actions)
                content = f"user_interaction: {user} performed {action}"
                tags = ["test_data", "user_interaction", user, action]

            elif category_roll < 0.55:  # Technical events (25%)
                service = random.choice(services)
                event = random.choice(events)
                content = f"technical_event: {service} {event} at {base_time + timedelta(minutes=i*10)}"
                tags = ["test_data", "technical_event", service, event]

            elif category_roll < 0.75:  # Project milestones (20%)
                project = random.choice(projects)
                milestone = random.choice(milestones)
                content = f"project_milestone: {project} {milestone}"
                tags = ["test_data", "project_milestone", project, milestone]

            elif category_roll < 0.90:  # Error logs (15%)
                error = random.choice(error_types)
                user = random.choice(users)
                content = f"error_log: {error} for user {user}"
                tags = ["test_data", "error_log", error, user]

            else:  # Configuration changes (10%)
                config = random.choice(config_items)
                old_val = f"old_value_{i}"
                new_val = f"new_value_{i}"
                content = f"config_change: {config} changed from {old_val} to {new_val}"
                tags = ["test_data", "config_change", config]

            episodes.append({
                "content": content,
                "tags": tags,
                "importance": round(random.uniform(0.3, 1.0), 2),
                "timestamp": (base_time + timedelta(minutes=i*10)).isoformat()
            })

        self.test_episodes = episodes
        print(f"✅ Generated {len(episodes)} test episodes")
        return episodes

    def insert_test_data(self):
        """Insert test episodes into database"""
        print("📤 Inserting test data into NEXUS memory...")

        cursor = self.db_conn.cursor()
        inserted = 0

        for episode in self.test_episodes:
            try:
                cursor.execute("""
                    INSERT INTO nexus_memory.zep_episodic_memory
                    (content, tags, importance_score, created_at, timestamp)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING episode_id
                """, (
                    episode["content"],
                    episode["tags"],
                    episode["importance"],
                    episode["timestamp"],
                    episode["timestamp"]
                ))
                episode_id = cursor.fetchone()[0]
                episode["episode_id"] = str(episode_id)
                inserted += 1
            except Exception as e:
                print(f"❌ Error inserting episode: {e}")

        self.db_conn.commit()
        print(f"✅ Inserted {inserted}/{len(self.test_episodes)} episodes")

    def generate_recall_queries(self, num_queries: int = 50):
        """
        Generate recall queries from test dataset
        Each query has an expected answer
        """
        print(f"❓ Generating {num_queries} recall queries...")

        queries = []

        # Sample random episodes for queries
        sampled = random.sample(self.test_episodes, min(num_queries, len(self.test_episodes)))

        for episode in sampled:
            content = episode["content"]

            # Parse content to create specific queries
            if "user_interaction:" in content:
                parts = content.split()
                user = parts[1]
                action = parts[3]
                query = f"What action did {user} perform?"
                expected = action

            elif "technical_event:" in content:
                parts = content.split()
                service = parts[1]
                event = parts[2]
                query = f"What event occurred with {service}?"
                expected = event

            elif "project_milestone:" in content:
                parts = content.split()
                project = parts[1]
                milestone = parts[2]
                query = f"What milestone was reached for project {project}?"
                expected = milestone

            elif "error_log:" in content:
                parts = content.split()
                error = parts[1]
                user = parts[4]
                query = f"What error did user {user} encounter?"
                expected = error

            elif "config_change:" in content:
                parts = content.split()
                config = parts[1]
                query = f"What configuration item was changed?"
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
                timeout=5
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("results") and len(data["results"]) > 0:
                    # Return top result content
                    return data["results"][0].get("content", "")

            return ""

        except Exception as e:
            print(f"❌ Query execution error: {e}")
            return ""

    def evaluate_answer(self, retrieved: str, expected: str) -> bool:
        """
        Evaluate if retrieved content contains expected answer
        Simple substring match (can be improved with LLM evaluation)
        """
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

            print(f"[{i+1}/{len(self.queries)}] Query: {query}")

            # Execute query
            retrieved = self.execute_query(query)

            # Evaluate
            is_correct = self.evaluate_answer(retrieved, expected)

            if is_correct:
                correct += 1
                status = "✅ CORRECT"
            else:
                incorrect += 1
                status = "❌ INCORRECT"

            print(f"           Expected: {expected}")
            print(f"           Retrieved: {retrieved[:100]}...")
            print(f"           {status}\n")

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
        print(f"  Zep (SOTA):     94.8%")
        print(f"  MemGPT:         93.4%")
        print(f"  NEXUS:          {r['accuracy']}%")

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

    def cleanup_test_data(self):
        """Remove test data from database"""
        print("\n🧹 Cleaning up test data...")
        cursor = self.db_conn.cursor()
        cursor.execute("""
            DELETE FROM nexus_memory.zep_episodic_memory
            WHERE 'test_data' = ANY(tags)
        """)
        deleted = cursor.rowcount
        self.db_conn.commit()
        print(f"✅ Deleted {deleted} test episodes")

    def close(self):
        """Close database connection"""
        if self.db_conn:
            self.db_conn.close()
            print("✅ Database connection closed")


def main():
    """Main execution"""
    benchmark = DMRBenchmark()

    try:
        # 1. Connect to database
        benchmark.connect_db()

        # 2. Generate synthetic dataset
        benchmark.generate_synthetic_dataset(num_episodes=100)

        # 3. Insert test data
        benchmark.insert_test_data()

        # 4. Generate queries
        benchmark.generate_recall_queries(num_queries=50)

        # 5. Run benchmark
        results = benchmark.run_benchmark()

        # 6. Print results
        benchmark.print_results()

        # 7. Save results
        results_file = f"dmr_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        benchmark.save_results(results_file)

        # 8. Cleanup (optional - comment out to keep test data)
        # benchmark.cleanup_test_data()

    except Exception as e:
        print(f"\n❌ Benchmark failed: {e}")
        import traceback
        traceback.print_exc()

    finally:
        benchmark.close()


if __name__ == "__main__":
    main()

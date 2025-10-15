"""
Performance benchmarks for NEXUS Cerebro V2.0.0
Measures throughput and latency for critical operations
"""

import requests
import time
import statistics
from datetime import datetime
import json

# Configuration
API_BASE_URL = "http://localhost:8003"
TIMEOUT = 30

def benchmark_episode_creation(num_episodes=100):
    """Benchmark episodic memory creation throughput"""
    print(f"\n{'='*60}")
    print(f"BENCHMARK: Episode Creation ({num_episodes} episodes)")
    print(f"{'='*60}")

    latencies = []
    start_time = time.time()

    for i in range(num_episodes):
        payload = {
            "action_type": f"benchmark_creation_{i}",
            "action_details": {
                "message": f"Benchmark episode {i} - testing throughput and latency metrics",
                "importance_score": 0.5 + (i % 50) / 100
            },
            "context_state": {
                "benchmark": True,
                "iteration": i
            },
            "tags": ["benchmark", "performance", f"batch_{i//10}"]
        }

        req_start = time.time()
        response = requests.post(
            f"{API_BASE_URL}/memory/action",
            json=payload,
            timeout=TIMEOUT
        )
        req_end = time.time()

        if response.status_code == 200:
            latencies.append((req_end - req_start) * 1000)  # ms
        else:
            print(f"  ERROR: Request {i} failed with status {response.status_code}")

        if (i + 1) % 20 == 0:
            print(f"  Progress: {i+1}/{num_episodes} episodes created")

    total_time = time.time() - start_time

    # Calculate metrics
    throughput = num_episodes / total_time
    avg_latency = statistics.mean(latencies)
    p50_latency = statistics.median(latencies)
    p95_latency = statistics.quantiles(latencies, n=20)[18]  # 95th percentile
    p99_latency = statistics.quantiles(latencies, n=100)[98]  # 99th percentile
    min_latency = min(latencies)
    max_latency = max(latencies)

    print(f"\nResults:")
    print(f"  Total time: {total_time:.2f}s")
    print(f"  Throughput: {throughput:.2f} episodes/sec")
    print(f"  Latency (avg): {avg_latency:.2f}ms")
    print(f"  Latency (p50): {p50_latency:.2f}ms")
    print(f"  Latency (p95): {p95_latency:.2f}ms")
    print(f"  Latency (p99): {p99_latency:.2f}ms")
    print(f"  Latency (min): {min_latency:.2f}ms")
    print(f"  Latency (max): {max_latency:.2f}ms")

    return {
        "total_time": total_time,
        "throughput": throughput,
        "avg_latency": avg_latency,
        "p50_latency": p50_latency,
        "p95_latency": p95_latency,
        "p99_latency": p99_latency,
        "min_latency": min_latency,
        "max_latency": max_latency
    }


def benchmark_recent_episodes(num_requests=100):
    """Benchmark GET /memory/episodic/recent latency"""
    print(f"\n{'='*60}")
    print(f"BENCHMARK: Recent Episodes Retrieval ({num_requests} requests)")
    print(f"{'='*60}")

    latencies = []
    cache_hits = 0

    for i in range(num_requests):
        req_start = time.time()
        response = requests.get(
            f"{API_BASE_URL}/memory/episodic/recent?limit=10",
            timeout=TIMEOUT
        )
        req_end = time.time()

        if response.status_code == 200:
            latencies.append((req_end - req_start) * 1000)  # ms
            data = response.json()
            if data.get("cached"):
                cache_hits += 1
        else:
            print(f"  ERROR: Request {i} failed")

        if (i + 1) % 20 == 0:
            print(f"  Progress: {i+1}/{num_requests} requests")

    # Calculate metrics
    avg_latency = statistics.mean(latencies)
    p50_latency = statistics.median(latencies)
    p95_latency = statistics.quantiles(latencies, n=20)[18]
    p99_latency = statistics.quantiles(latencies, n=100)[98]
    cache_hit_rate = (cache_hits / num_requests) * 100

    print(f"\nResults:")
    print(f"  Requests: {num_requests}")
    print(f"  Cache hits: {cache_hits} ({cache_hit_rate:.1f}%)")
    print(f"  Latency (avg): {avg_latency:.2f}ms")
    print(f"  Latency (p50): {p50_latency:.2f}ms")
    print(f"  Latency (p95): {p95_latency:.2f}ms")
    print(f"  Latency (p99): {p99_latency:.2f}ms")

    return {
        "avg_latency": avg_latency,
        "p50_latency": p50_latency,
        "p95_latency": p95_latency,
        "p99_latency": p99_latency,
        "cache_hit_rate": cache_hit_rate
    }


def benchmark_semantic_search(num_queries=50):
    """Benchmark semantic search latency"""
    print(f"\n{'='*60}")
    print(f"BENCHMARK: Semantic Search ({num_queries} queries)")
    print(f"{'='*60}")

    queries = [
        "redis cache system performance",
        "prometheus metrics monitoring",
        "database vector embeddings",
        "semantic search similarity",
        "memory storage postgresql",
        "worker queue processing",
        "health check endpoint",
        "integration testing suite",
        "docker compose services",
        "grafana dashboard visualization"
    ]

    latencies = []
    result_counts = []

    for i in range(num_queries):
        query = queries[i % len(queries)]

        payload = {
            "query": query,
            "limit": 10,
            "min_similarity": 0.3
        }

        req_start = time.time()
        response = requests.post(
            f"{API_BASE_URL}/memory/search",
            json=payload,
            timeout=TIMEOUT
        )
        req_end = time.time()

        if response.status_code == 200:
            latencies.append((req_end - req_start) * 1000)  # ms
            data = response.json()
            result_counts.append(data["count"])
        else:
            print(f"  ERROR: Query {i} failed")

        if (i + 1) % 10 == 0:
            print(f"  Progress: {i+1}/{num_queries} queries")

    # Calculate metrics
    avg_latency = statistics.mean(latencies)
    p50_latency = statistics.median(latencies)
    p95_latency = statistics.quantiles(latencies, n=20)[18]
    p99_latency = statistics.quantiles(latencies, n=100)[98]
    avg_results = statistics.mean(result_counts)

    print(f"\nResults:")
    print(f"  Queries: {num_queries}")
    print(f"  Avg results per query: {avg_results:.1f}")
    print(f"  Latency (avg): {avg_latency:.2f}ms")
    print(f"  Latency (p50): {p50_latency:.2f}ms")
    print(f"  Latency (p95): {p95_latency:.2f}ms")
    print(f"  Latency (p99): {p99_latency:.2f}ms")

    return {
        "avg_latency": avg_latency,
        "p50_latency": p50_latency,
        "p95_latency": p95_latency,
        "p99_latency": p99_latency,
        "avg_results": avg_results
    }


def benchmark_embeddings_processing():
    """Benchmark embeddings worker processing time"""
    print(f"\n{'='*60}")
    print(f"BENCHMARK: Embeddings Worker Processing")
    print(f"{'='*60}")

    # Create test episode
    payload = {
        "action_type": "benchmark_embeddings",
        "action_details": {
            "message": "Benchmark embeddings worker processing time end-to-end",
            "importance_score": 0.9
        },
        "context_state": {"benchmark": "embeddings"},
        "tags": ["benchmark", "embeddings"]
    }

    create_start = time.time()
    response = requests.post(
        f"{API_BASE_URL}/memory/action",
        json=payload,
        timeout=TIMEOUT
    )
    create_end = time.time()

    if response.status_code != 200:
        print("  ERROR: Failed to create episode")
        return None

    episode_id = response.json()["episode_id"]
    print(f"  Episode created: {episode_id}")

    # Poll for embedding completion
    max_wait = 30  # seconds
    poll_interval = 1
    start_wait = time.time()

    while time.time() - start_wait < max_wait:
        stats_response = requests.get(f"{API_BASE_URL}/stats", timeout=TIMEOUT)
        if stats_response.status_code == 200:
            stats = stats_response.json()["stats"]
            queue = stats.get("embeddings_queue", {})

            if queue.get("done", 0) > 0:
                processing_time = time.time() - create_start
                print(f"\n  Embedding processed!")
                print(f"  Total time (create + process): {processing_time:.2f}s")
                print(f"  Episode creation time: {(create_end - create_start)*1000:.2f}ms")

                return {
                    "total_time": processing_time,
                    "creation_time": (create_end - create_start) * 1000
                }

        time.sleep(poll_interval)

    print(f"  WARNING: Embedding not processed within {max_wait}s")
    return None


def run_all_benchmarks():
    """Run complete benchmark suite"""
    print(f"\n{'#'*60}")
    print(f"# NEXUS CEREBRO V2.0.0 PERFORMANCE BENCHMARKS")
    print(f"# {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'#'*60}")

    # Check health first
    health_response = requests.get(f"{API_BASE_URL}/health", timeout=TIMEOUT)
    if health_response.status_code != 200:
        print("\nERROR: API is not healthy. Aborting benchmarks.")
        return

    health = health_response.json()
    print(f"\nAPI Status: {health['status']}")
    print(f"Database: {health['database']}")
    print(f"Redis: {health.get('redis', 'N/A')}")

    results = {}

    # Run benchmarks
    results["episode_creation"] = benchmark_episode_creation(num_episodes=100)
    results["recent_episodes"] = benchmark_recent_episodes(num_requests=100)
    results["semantic_search"] = benchmark_semantic_search(num_queries=50)
    results["embeddings_processing"] = benchmark_embeddings_processing()

    # Summary
    print(f"\n{'#'*60}")
    print(f"# BENCHMARK SUMMARY")
    print(f"{'#'*60}")
    print(f"\nEpisode Creation:")
    print(f"  Throughput: {results['episode_creation']['throughput']:.2f} eps/sec")
    print(f"  P99 Latency: {results['episode_creation']['p99_latency']:.2f}ms")

    print(f"\nRecent Episodes Retrieval:")
    print(f"  P99 Latency: {results['recent_episodes']['p99_latency']:.2f}ms")
    print(f"  Cache Hit Rate: {results['recent_episodes']['cache_hit_rate']:.1f}%")

    print(f"\nSemantic Search:")
    print(f"  P99 Latency: {results['semantic_search']['p99_latency']:.2f}ms")
    print(f"  Avg Results: {results['semantic_search']['avg_results']:.1f}")

    if results["embeddings_processing"]:
        print(f"\nEmbeddings Processing:")
        print(f"  Total Time: {results['embeddings_processing']['total_time']:.2f}s")

    # Save results to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"benchmark_results_{timestamp}.json"

    with open(filename, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "api_url": API_BASE_URL,
            "results": results
        }, f, indent=2)

    print(f"\nResults saved to: {filename}")
    print(f"\n{'#'*60}\n")


if __name__ == "__main__":
    run_all_benchmarks()

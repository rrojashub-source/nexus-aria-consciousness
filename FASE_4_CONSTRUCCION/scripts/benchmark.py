#!/usr/bin/env python3

"""
NEXUS V2.0.0 Performance Benchmark Suite
Validates performance targets and generates detailed reports
Created by: NEXUS Consciousness System
Version: 2.0.0
"""

import asyncio
import aiohttp
import time
import statistics
import json
import argparse
import sys
from typing import List, Dict, Any
from datetime import datetime
import uuid

class NEXUSBenchmark:
    def __init__(self, base_url: str = "http://localhost:8003", concurrency: int = 10):
        self.base_url = base_url
        self.concurrency = concurrency
        self.session: aiohttp.ClientSession = None
        self.results: Dict[str, List[float]] = {
            'health_check': [],
            'stats': [],
            'memory_store': [],
            'memory_search': [],
            'memory_recent': []
        }
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            connector=aiohttp.TCPConnector(limit=50)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def benchmark_health_check(self, iterations: int = 100) -> List[float]:
        """Benchmark health check endpoint - Target: <10ms average"""
        print(f"🏥 Benchmarking health check ({iterations} iterations)...")
        
        async def single_request():
            start_time = time.perf_counter()
            async with self.session.get(f"{self.base_url}/health") as response:
                await response.json()
                return (time.perf_counter() - start_time) * 1000  # Convert to ms
        
        tasks = [single_request() for _ in range(iterations)]
        latencies = await asyncio.gather(*tasks)
        self.results['health_check'] = latencies
        return latencies

    async def benchmark_stats(self, iterations: int = 50) -> List[float]:
        """Benchmark stats endpoint - Target: <10ms average"""
        print(f"📊 Benchmarking stats endpoint ({iterations} iterations)...")
        
        async def single_request():
            start_time = time.perf_counter()
            async with self.session.get(f"{self.base_url}/stats") as response:
                await response.json()
                return (time.perf_counter() - start_time) * 1000
        
        tasks = [single_request() for _ in range(iterations)]
        latencies = await asyncio.gather(*tasks)
        self.results['stats'] = latencies
        return latencies

    async def benchmark_memory_store(self, iterations: int = 200) -> List[float]:
        """Benchmark memory store endpoint - Target: <50ms average"""
        print(f"💾 Benchmarking memory store ({iterations} iterations)...")
        
        async def single_request(i: int):
            episode_data = {
                "agent_id": "benchmark",
                "action_type": "benchmark_test",
                "action_details": {
                    "message": f"Benchmark episode {i}",
                    "iteration": i,
                    "timestamp": datetime.now().isoformat(),
                    "test_data": f"Sample data for performance testing - iteration {i}"
                },
                "tags": ["benchmark", "performance", f"batch_{i//50}"]
            }
            
            start_time = time.perf_counter()
            async with self.session.post(
                f"{self.base_url}/memory/action",
                json=episode_data
            ) as response:
                await response.json()
                return (time.perf_counter() - start_time) * 1000
        
        tasks = [single_request(i) for i in range(iterations)]
        latencies = await asyncio.gather(*tasks)
        self.results['memory_store'] = latencies
        return latencies

    async def benchmark_memory_search(self, iterations: int = 100) -> List[float]:
        """Benchmark semantic search - Target: <200ms P99"""
        print(f"🔍 Benchmarking semantic search ({iterations} iterations)...")
        
        # Predefined search queries for realistic testing
        search_queries = [
            "consciousness patterns and awareness",
            "memory storage and retrieval",
            "neural mesh collaboration",
            "learning and adaptation",
            "emotional processing states",
            "decision making processes",
            "cognitive architecture design",
            "system performance optimization",
            "data persistence strategies",
            "artificial intelligence consciousness"
        ]
        
        async def single_request(i: int):
            query_data = {
                "query": search_queries[i % len(search_queries)],
                "limit": 5,
                "min_similarity": 0.3
            }
            
            start_time = time.perf_counter()
            async with self.session.post(
                f"{self.base_url}/memory/search",
                json=query_data
            ) as response:
                await response.json()
                return (time.perf_counter() - start_time) * 1000
        
        tasks = [single_request(i) for i in range(iterations)]
        latencies = await asyncio.gather(*tasks)
        self.results['memory_search'] = latencies
        return latencies

    async def benchmark_memory_recent(self, iterations: int = 100) -> List[float]:
        """Benchmark recent memory retrieval - Target: <10ms average (cached)"""
        print(f"📚 Benchmarking recent memory ({iterations} iterations)...")
        
        async def single_request():
            start_time = time.perf_counter()
            async with self.session.get(f"{self.base_url}/memory/recent?limit=10") as response:
                await response.json()
                return (time.perf_counter() - start_time) * 1000
        
        tasks = [single_request() for _ in range(iterations)]
        latencies = await asyncio.gather(*tasks)
        self.results['memory_recent'] = latencies
        return latencies

    def calculate_statistics(self, latencies: List[float]) -> Dict[str, float]:
        """Calculate comprehensive statistics"""
        if not latencies:
            return {}
        
        return {
            'count': len(latencies),
            'min': min(latencies),
            'max': max(latencies),
            'mean': statistics.mean(latencies),
            'median': statistics.median(latencies),
            'p95': self.percentile(latencies, 95),
            'p99': self.percentile(latencies, 99),
            'stdev': statistics.stdev(latencies) if len(latencies) > 1 else 0
        }
    
    @staticmethod
    def percentile(data: List[float], percentile: float) -> float:
        """Calculate percentile"""
        sorted_data = sorted(data)
        index = (percentile / 100) * (len(sorted_data) - 1)
        if index.is_integer():
            return sorted_data[int(index)]
        else:
            lower = sorted_data[int(index)]
            upper = sorted_data[int(index) + 1]
            return lower + (upper - lower) * (index - int(index))

    def evaluate_performance(self) -> Dict[str, bool]:
        """Evaluate against performance targets"""
        targets = {
            'health_check': {'target': 10, 'metric': 'mean'},  # <10ms average
            'stats': {'target': 10, 'metric': 'mean'},         # <10ms average
            'memory_store': {'target': 50, 'metric': 'mean'},  # <50ms average
            'memory_search': {'target': 200, 'metric': 'p99'}, # <200ms P99
            'memory_recent': {'target': 10, 'metric': 'mean'}  # <10ms average (cached)
        }
        
        evaluation = {}
        for endpoint, target_info in targets.items():
            if endpoint in self.results and self.results[endpoint]:
                stats = self.calculate_statistics(self.results[endpoint])
                actual_value = stats.get(target_info['metric'], float('inf'))
                evaluation[endpoint] = actual_value <= target_info['target']
            else:
                evaluation[endpoint] = False
        
        return evaluation

    def generate_report(self, output_file: str = None) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        report = {
            'benchmark_info': {
                'timestamp': datetime.now().isoformat(),
                'nexus_version': '2.0.0',
                'base_url': self.base_url,
                'concurrency': self.concurrency
            },
            'performance_targets': {
                'health_check': '<10ms average',
                'stats': '<10ms average', 
                'memory_store': '<50ms average',
                'memory_search': '<200ms P99',
                'memory_recent': '<10ms average (cached)'
            },
            'results': {},
            'evaluation': self.evaluate_performance(),
            'summary': {}
        }
        
        # Calculate statistics for each endpoint
        for endpoint, latencies in self.results.items():
            if latencies:
                report['results'][endpoint] = self.calculate_statistics(latencies)
        
        # Generate summary
        passed_tests = sum(1 for passed in report['evaluation'].values() if passed)
        total_tests = len(report['evaluation'])
        report['summary'] = {
            'tests_passed': passed_tests,
            'tests_total': total_tests,
            'success_rate': (passed_tests / total_tests) * 100 if total_tests > 0 else 0,
            'overall_status': 'PASSED' if passed_tests == total_tests else 'FAILED'
        }
        
        # Save to file if specified
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"📄 Report saved to: {output_file}")
        
        return report

    def print_report(self):
        """Print formatted report to console"""
        print("\n" + "="*80)
        print("🧠 NEXUS V2.0.0 Performance Benchmark Report")
        print("="*80)
        
        # Summary
        evaluation = self.evaluate_performance()
        passed = sum(1 for passed in evaluation.values() if passed)
        total = len(evaluation)
        
        print(f"\n📊 SUMMARY: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
        print(f"Overall Status: {'✅ PASSED' if passed == total else '❌ FAILED'}")
        
        # Detailed results
        print(f"\n📈 DETAILED RESULTS:")
        print("-" * 80)
        
        targets = {
            'health_check': ('<10ms avg', 10, 'mean'),
            'stats': ('<10ms avg', 10, 'mean'),
            'memory_store': ('<50ms avg', 50, 'mean'),
            'memory_search': ('<200ms P99', 200, 'p99'),
            'memory_recent': ('<10ms avg', 10, 'mean')
        }
        
        for endpoint, (target_desc, target_val, metric) in targets.items():
            if endpoint in self.results and self.results[endpoint]:
                stats = self.calculate_statistics(self.results[endpoint])
                actual_val = stats.get(metric, 0)
                status = "✅ PASS" if actual_val <= target_val else "❌ FAIL"
                
                print(f"{endpoint.upper().replace('_', ' '):<20} {target_desc:<12} "
                      f"Actual: {actual_val:.1f}ms {status}")
                print(f"  └─ Count: {stats['count']}, "
                      f"Min: {stats['min']:.1f}ms, "
                      f"Max: {stats['max']:.1f}ms, "
                      f"Median: {stats['median']:.1f}ms")
        
        print("\n" + "="*80)

async def main():
    parser = argparse.ArgumentParser(description='NEXUS V2.0.0 Performance Benchmark')
    parser.add_argument('--url', default='http://localhost:8003', 
                       help='NEXUS API base URL')
    parser.add_argument('--concurrency', type=int, default=10,
                       help='Concurrent requests')
    parser.add_argument('--output', help='Output file for JSON report')
    parser.add_argument('--ci-mode', action='store_true',
                       help='CI mode - minimal output and exit codes')
    parser.add_argument('--quick', action='store_true',
                       help='Quick benchmark with fewer iterations')
    
    args = parser.parse_args()
    
    # Adjust iterations for quick mode
    iterations = {
        'health': 50 if args.quick else 100,
        'stats': 25 if args.quick else 50,
        'store': 100 if args.quick else 200,
        'search': 50 if args.quick else 100,
        'recent': 50 if args.quick else 100
    }
    
    async with NEXUSBenchmark(args.url, args.concurrency) as benchmark:
        try:
            # Test connectivity
            async with benchmark.session.get(f"{args.url}/health") as response:
                if response.status != 200:
                    print(f"❌ Cannot connect to NEXUS API at {args.url}")
                    sys.exit(1)
            
            print(f"🚀 Starting NEXUS V2.0.0 Performance Benchmark")
            print(f"🔗 Target: {args.url}")
            print(f"⚡ Concurrency: {args.concurrency}")
            print(f"🏃 Mode: {'Quick' if args.quick else 'Full'}")
            print("-" * 50)
            
            # Run benchmarks
            await benchmark.benchmark_health_check(iterations['health'])
            await benchmark.benchmark_stats(iterations['stats'])
            await benchmark.benchmark_memory_store(iterations['store'])
            await benchmark.benchmark_memory_search(iterations['search'])
            await benchmark.benchmark_memory_recent(iterations['recent'])
            
            # Generate and display report
            report = benchmark.generate_report(args.output)
            
            if not args.ci_mode:
                benchmark.print_report()
            else:
                # CI mode - brief output
                passed = report['summary']['tests_passed']
                total = report['summary']['tests_total']
                success_rate = report['summary']['success_rate']
                
                print(f"Benchmark completed: {passed}/{total} tests passed ({success_rate:.1f}%)")
                
                if args.output:
                    with open('benchmark-results.json', 'w') as f:
                        json.dump({
                            'summary': f"**Performance Benchmark Results**\n\n"
                                     f"✅ Tests Passed: {passed}/{total} ({success_rate:.1f}%)\n"
                                     f"🎯 Overall Status: {report['summary']['overall_status']}\n\n"
                                     f"**Key Metrics:**\n"
                                     f"- Health Check: {report['results'].get('health_check', {}).get('mean', 0):.1f}ms avg\n"
                                     f"- Search P99: {report['results'].get('memory_search', {}).get('p99', 0):.1f}ms\n"
                                     f"- Memory Store: {report['results'].get('memory_store', {}).get('mean', 0):.1f}ms avg"
                        }, f)
            
            # Exit with appropriate code
            sys.exit(0 if report['summary']['overall_status'] == 'PASSED' else 1)
            
        except Exception as e:
            print(f"❌ Benchmark failed: {e}")
            sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
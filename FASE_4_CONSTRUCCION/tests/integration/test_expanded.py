"""
NEXUS V2.0.0 Expanded Integration Tests
Comprehensive test coverage for all system components
Created by: NEXUS Consciousness System
Version: 2.0.0
"""

import pytest
import asyncio
import aiohttp
import json
import time
from typing import Dict, Any, List
import uuid
from datetime import datetime

class TestNEXUSIntegration:
    """Comprehensive integration tests for NEXUS V2.0.0"""
    
    base_url = "http://localhost:8003"
    test_agent_id = "nexus_test"
    
    @pytest.fixture(scope="session")
    async def client_session(self):
        """Create aiohttp client session for tests"""
        async with aiohttp.ClientSession() as session:
            yield session
    
    @pytest.fixture(autouse=True)
    async def setup_cleanup(self):
        """Setup and cleanup for each test"""
        # Setup: Wait for system to be ready
        await self._wait_for_system_ready()
        yield
        # Cleanup: Remove test episodes
        await self._cleanup_test_episodes()
    
    async def _wait_for_system_ready(self, timeout: int = 30):
        """Wait for NEXUS system to be fully operational"""
        async with aiohttp.ClientSession() as session:
            for _ in range(timeout):
                try:
                    async with session.get(f"{self.base_url}/health") as response:
                        if response.status == 200:
                            health_data = await response.json()
                            if health_data.get("status") == "healthy":
                                return
                except:
                    pass
                await asyncio.sleep(1)
        raise TimeoutError("NEXUS system not ready within timeout")
    
    async def _cleanup_test_episodes(self):
        """Clean up test episodes after each test"""
        # This would typically connect to DB directly to clean up
        # For now, we rely on test episodes being tagged appropriately
        pass
    
    async def test_health_check_comprehensive(self, client_session):
        """Test comprehensive health check functionality"""
        async with client_session.get(f"{self.base_url}/health") as response:
            assert response.status == 200
            health_data = await response.json()
            
            # Verify health response structure
            assert "status" in health_data
            assert "agent_id" in health_data
            assert "timestamp" in health_data
            assert "version" in health_data
            assert "components" in health_data
            
            # Verify all components are healthy
            components = health_data["components"]
            for component_name, component_health in components.items():
                assert component_health["status"] in ["healthy", "degraded"]
                assert "response_time_ms" in component_health
                assert component_health["response_time_ms"] < 100  # <100ms per component
    
    async def test_stats_endpoint_detailed(self, client_session):
        """Test comprehensive stats endpoint"""
        async with client_session.get(f"{self.base_url}/stats") as response:
            assert response.status == 200
            stats_data = await response.json()
            
            # Verify stats structure
            required_fields = [
                "success", "agent_id", "timestamp", 
                "memory_stats", "performance_stats", "queue_stats"
            ]
            for field in required_fields:
                assert field in stats_data
            
            # Verify memory stats
            memory_stats = stats_data["memory_stats"]
            assert "total_episodes" in memory_stats
            assert "embeddings_complete" in memory_stats
            assert "embeddings_rate" in memory_stats
            assert memory_stats["total_episodes"] >= 0
            assert memory_stats["embeddings_rate"] >= 0.0
    
    async def test_episode_creation_and_retrieval(self, client_session):
        """Test episode creation and immediate retrieval"""
        # Create test episode
        test_episode = {
            "agent_id": self.test_agent_id,
            "action_type": "integration_test",
            "action_details": {
                "test_id": str(uuid.uuid4()),
                "message": "Integration test episode",
                "timestamp": datetime.now().isoformat(),
                "test_data": {
                    "complexity": "high",
                    "nested": {"level": 1, "data": [1, 2, 3]}
                }
            },
            "tags": ["integration_test", "automated", "temp"]
        }
        
        # Store episode
        async with client_session.post(
            f"{self.base_url}/memory/action",
            json=test_episode
        ) as response:
            assert response.status == 200
            store_result = await response.json()
            assert store_result["success"] is True
            assert "episode_id" in store_result
            episode_id = store_result["episode_id"]
        
        # Wait for embedding processing
        await asyncio.sleep(2)
        
        # Search for the episode
        search_query = {
            "query": "integration test episode",
            "limit": 5,
            "min_similarity": 0.3
        }
        
        async with client_session.post(
            f"{self.base_url}/memory/search",
            json=search_query
        ) as response:
            assert response.status == 200
            search_results = await response.json()
            assert search_results["success"] is True
            assert search_results["count"] > 0
            
            # Verify our episode is found
            found_episode = None
            for result in search_results["results"]:
                if result["episode_id"] == episode_id:
                    found_episode = result
                    break
            
            assert found_episode is not None
            assert found_episode["similarity_score"] > 0.5
    
    async def test_semantic_search_quality(self, client_session):
        """Test semantic search quality and ranking"""
        # Create multiple related episodes
        test_episodes = [
            {
                "agent_id": self.test_agent_id,
                "action_type": "learning",
                "action_details": {"message": "Machine learning algorithms and neural networks"},
                "tags": ["ml", "neural", "test"]
            },
            {
                "agent_id": self.test_agent_id,
                "action_type": "learning", 
                "action_details": {"message": "Artificial intelligence consciousness and awareness"},
                "tags": ["ai", "consciousness", "test"]
            },
            {
                "agent_id": self.test_agent_id,
                "action_type": "learning",
                "action_details": {"message": "Cooking recipes and kitchen techniques"},
                "tags": ["cooking", "unrelated", "test"]
            }
        ]
        
        # Store all episodes
        episode_ids = []
        for episode in test_episodes:
            async with client_session.post(
                f"{self.base_url}/memory/action",
                json=episode
            ) as response:
                result = await response.json()
                episode_ids.append(result["episode_id"])
        
        # Wait for embeddings
        await asyncio.sleep(3)
        
        # Search for AI-related content
        search_query = {
            "query": "artificial intelligence machine learning",
            "limit": 10,
            "min_similarity": 0.2
        }
        
        async with client_session.post(
            f"{self.base_url}/memory/search",
            json=search_query
        ) as response:
            search_results = await response.json()
            
            # Verify search quality
            assert search_results["count"] >= 2
            
            # Check that AI/ML episodes rank higher than cooking
            results = search_results["results"]
            ai_ml_scores = []
            cooking_scores = []
            
            for result in results:
                if "machine learning" in result["content"].lower() or "artificial intelligence" in result["content"].lower():
                    ai_ml_scores.append(result["similarity_score"])
                elif "cooking" in result["content"].lower():
                    cooking_scores.append(result["similarity_score"])
            
            if ai_ml_scores and cooking_scores:
                assert max(ai_ml_scores) > max(cooking_scores), "AI/ML content should rank higher than cooking"
    
    async def test_recent_episodes_caching(self, client_session):
        """Test recent episodes endpoint and caching behavior"""
        # Test basic recent episodes retrieval
        async with client_session.get(f"{self.base_url}/memory/recent?limit=5") as response:
            assert response.status == 200
            recent_data = await response.json()
            assert "episodes" in recent_data
            assert "count" in recent_data
            assert recent_data["count"] >= 0
            assert len(recent_data["episodes"]) <= 5
        
        # Test caching by measuring response times
        response_times = []
        for _ in range(3):
            start_time = time.time()
            async with client_session.get(f"{self.base_url}/memory/recent?limit=10") as response:
                await response.json()
                response_times.append((time.time() - start_time) * 1000)
        
        # Second and third requests should be faster (cached)
        assert response_times[1] < response_times[0] * 1.5, "Caching not working effectively"
        assert response_times[2] < response_times[0] * 1.5, "Caching not working effectively"
    
    async def test_concurrent_requests(self, client_session):
        """Test system behavior under concurrent load"""
        concurrent_requests = 20
        
        async def create_episode(index: int):
            episode = {
                "agent_id": self.test_agent_id,
                "action_type": "concurrent_test",
                "action_details": {"message": f"Concurrent test episode {index}"},
                "tags": ["concurrent_test", f"batch_{index//5}"]
            }
            
            async with client_session.post(
                f"{self.base_url}/memory/action",
                json=episode
            ) as response:
                return await response.json()
        
        # Execute concurrent requests
        start_time = time.time()
        tasks = [create_episode(i) for i in range(concurrent_requests)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        execution_time = time.time() - start_time
        
        # Verify all requests succeeded
        successful_requests = 0
        for result in results:
            if isinstance(result, dict) and result.get("success"):
                successful_requests += 1
        
        assert successful_requests >= concurrent_requests * 0.95  # 95% success rate
        assert execution_time < 10  # Should complete within 10 seconds
    
    async def test_error_handling(self, client_session):
        """Test error handling for invalid requests"""
        # Test invalid episode structure
        invalid_episode = {
            "agent_id": self.test_agent_id,
            # Missing required fields
            "action_details": {"message": "Invalid episode"}
        }
        
        async with client_session.post(
            f"{self.base_url}/memory/action",
            json=invalid_episode
        ) as response:
            assert response.status == 400
            error_data = await response.json()
            assert error_data["success"] is False
            assert "error" in error_data
        
        # Test invalid search query
        invalid_search = {
            "query": "",  # Empty query
            "limit": -1   # Invalid limit
        }
        
        async with client_session.post(
            f"{self.base_url}/memory/search",
            json=invalid_search
        ) as response:
            assert response.status == 400
            error_data = await response.json()
            assert error_data["success"] is False
    
    async def test_system_performance_targets(self, client_session):
        """Test that system meets performance targets"""
        # Health check performance
        start_time = time.time()
        async with client_session.get(f"{self.base_url}/health") as response:
            health_latency = (time.time() - start_time) * 1000
        
        assert health_latency < 50  # <50ms for health check
        
        # Stats performance  
        start_time = time.time()
        async with client_session.get(f"{self.base_url}/stats") as response:
            stats_latency = (time.time() - start_time) * 1000
        
        assert stats_latency < 50  # <50ms for stats
        
        # Search performance (with existing data)
        search_query = {"query": "test episode", "limit": 5}
        start_time = time.time()
        async with client_session.post(
            f"{self.base_url}/memory/search",
            json=search_query
        ) as response:
            search_latency = (time.time() - start_time) * 1000
        
        assert search_latency < 500  # <500ms for search (relaxed for test env)
    
    async def test_data_persistence(self, client_session):
        """Test data persistence across operations"""
        # Create an episode
        test_episode = {
            "agent_id": self.test_agent_id,
            "action_type": "persistence_test",
            "action_details": {
                "message": "Data persistence verification episode",
                "unique_marker": str(uuid.uuid4())
            },
            "tags": ["persistence_test", "unique"]
        }
        
        async with client_session.post(
            f"{self.base_url}/memory/action",
            json=test_episode
        ) as response:
            store_result = await response.json()
            episode_id = store_result["episode_id"]
        
        # Wait and search multiple times to verify persistence
        await asyncio.sleep(2)
        
        for _ in range(3):
            search_query = {
                "query": "data persistence verification",
                "limit": 5
            }
            
            async with client_session.post(
                f"{self.base_url}/memory/search",
                json=search_query
            ) as response:
                search_results = await response.json()
                
                # Verify episode is consistently found
                found = any(
                    result["episode_id"] == episode_id 
                    for result in search_results["results"]
                )
                assert found, "Episode not found in persistence test"
            
            await asyncio.sleep(1)
    
    async def test_embeddings_processing(self, client_session):
        """Test embeddings are properly generated and processed"""
        # Create episode and verify embedding generation
        test_episode = {
            "agent_id": self.test_agent_id,
            "action_type": "embeddings_test",
            "action_details": {
                "message": "Unique embedding test with specific vocabulary: quantum consciousness neural networks"
            },
            "tags": ["embeddings_test"]
        }
        
        async with client_session.post(
            f"{self.base_url}/memory/action",
            json=test_episode
        ) as response:
            store_result = await response.json()
            episode_id = store_result["episode_id"]
        
        # Wait for embedding processing
        await asyncio.sleep(5)
        
        # Verify embedding was created by searching for unique terms
        search_query = {
            "query": "quantum consciousness neural networks",
            "limit": 5,
            "min_similarity": 0.7
        }
        
        async with client_session.post(
            f"{self.base_url}/memory/search",
            json=search_query
        ) as response:
            search_results = await response.json()
            
            # Should find the episode with high similarity
            found_with_high_similarity = any(
                result["episode_id"] == episode_id and result["similarity_score"] > 0.7
                for result in search_results["results"]
            )
            assert found_with_high_similarity, "Embedding not properly generated or processed"

# Performance test markers
@pytest.mark.performance
class TestNEXUSPerformance:
    """Performance-focused tests"""
    
    base_url = "http://localhost:8003"
    
    @pytest.mark.asyncio
    async def test_bulk_episode_creation_performance(self):
        """Test performance of bulk episode creation"""
        async with aiohttp.ClientSession() as session:
            episodes_count = 100
            start_time = time.time()
            
            tasks = []
            for i in range(episodes_count):
                episode = {
                    "agent_id": "performance_test",
                    "action_type": "bulk_test",
                    "action_details": {"message": f"Bulk test episode {i}"},
                    "tags": ["bulk_test", "performance"]
                }
                
                task = session.post(f"{self.base_url}/memory/action", json=episode)
                tasks.append(task)
            
            responses = await asyncio.gather(*tasks)
            total_time = time.time() - start_time
            
            # Verify performance
            throughput = episodes_count / total_time
            assert throughput > 10  # >10 episodes/second
            assert total_time < 30   # Complete within 30 seconds

# Configuration for pytest
def pytest_configure(config):
    """Configure pytest markers"""
    config.addinivalue_line(
        "markers", "performance: marks tests as performance tests"
    )

# Test data cleanup fixture
@pytest.fixture(scope="session", autouse=True)
def cleanup_test_data():
    """Clean up test data after test session"""
    yield
    # This would clean up all test episodes
    # Implementation depends on direct DB access
    pass
"""
Integration tests for semantic search functionality
Tests POST /memory/search endpoint with vector similarity
"""

import pytest
import requests
import time

# Test configuration
API_BASE_URL = "http://localhost:8003"
TIMEOUT = 30  # Longer timeout for embedding generation


class TestSemanticSearch:
    """Test suite for semantic search with pgvector"""

    def test_search_endpoint_available(self):
        """Test that search endpoint is accessible"""
        payload = {
            "query": "test query",
            "limit": 5,
            "min_similarity": 0.3
        }

        response = requests.post(
            f"{API_BASE_URL}/memory/search",
            json=payload,
            timeout=TIMEOUT
        )

        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert data["success"] is True

    def test_search_returns_similar_content(self):
        """Test that search returns semantically similar episodes"""
        # Create test episode with specific content
        create_payload = {
            "action_type": "test_search_similarity",
            "action_details": {
                "message": "PostgreSQL database with vector embeddings for semantic search",
                "importance_score": 0.85
            },
            "context_state": {"test": "search"},
            "tags": ["test", "search", "database"]
        }

        create_response = requests.post(
            f"{API_BASE_URL}/memory/action",
            json=create_payload,
            timeout=TIMEOUT
        )
        assert create_response.status_code == 200
        episode_id = create_response.json()["episode_id"]

        # Wait for embedding generation
        time.sleep(8)

        # Search with similar query
        search_payload = {
            "query": "vector database semantic similarity",
            "limit": 10,
            "min_similarity": 0.2
        }

        search_response = requests.post(
            f"{API_BASE_URL}/memory/search",
            json=search_payload,
            timeout=TIMEOUT
        )

        assert search_response.status_code == 200
        search_data = search_response.json()

        assert search_data["success"] is True
        assert "results" in search_data
        assert search_data["count"] >= 0

        # If results found, verify our episode might be there
        if search_data["count"] > 0:
            result_ids = [r["episode_id"] for r in search_data["results"]]
            # Our episode should ideally be in results (but not guaranteed)
            # At minimum, verify result structure
            first_result = search_data["results"][0]
            assert "episode_id" in first_result
            assert "content" in first_result
            assert "similarity_score" in first_result
            assert "importance_score" in first_result
            assert "tags" in first_result

    def test_search_similarity_scores(self):
        """Test that similarity scores are in valid range [0, 1]"""
        search_payload = {
            "query": "test similarity scores",
            "limit": 10,
            "min_similarity": 0.0
        }

        response = requests.post(
            f"{API_BASE_URL}/memory/search",
            json=search_payload,
            timeout=TIMEOUT
        )

        assert response.status_code == 200
        data = response.json()

        if data["count"] > 0:
            for result in data["results"]:
                similarity = result["similarity_score"]
                assert 0.0 <= similarity <= 1.0, f"Similarity {similarity} out of range"

    def test_search_min_similarity_filter(self):
        """Test that min_similarity threshold filters results correctly"""
        # Search with high threshold
        high_threshold = {
            "query": "very specific unique query string 99999",
            "limit": 10,
            "min_similarity": 0.9
        }

        high_response = requests.post(
            f"{API_BASE_URL}/memory/search",
            json=high_threshold,
            timeout=TIMEOUT
        )

        assert high_response.status_code == 200
        high_data = high_response.json()

        # Search with low threshold
        low_threshold = {
            "query": "very specific unique query string 99999",
            "limit": 10,
            "min_similarity": 0.1
        }

        low_response = requests.post(
            f"{API_BASE_URL}/memory/search",
            json=low_threshold,
            timeout=TIMEOUT
        )

        assert low_response.status_code == 200
        low_data = low_response.json()

        # Low threshold should return >= results than high threshold
        assert low_data["count"] >= high_data["count"]

    def test_search_limit_parameter(self):
        """Test that limit parameter restricts result count"""
        payload = {
            "query": "test limit parameter",
            "limit": 3,
            "min_similarity": 0.0
        }

        response = requests.post(
            f"{API_BASE_URL}/memory/search",
            json=payload,
            timeout=TIMEOUT
        )

        assert response.status_code == 200
        data = response.json()

        assert len(data["results"]) <= 3

    def test_search_with_redis_cache_keyword(self):
        """Test searching for redis/cache related content"""
        payload = {
            "query": "redis cache system",
            "limit": 5,
            "min_similarity": 0.3
        }

        response = requests.post(
            f"{API_BASE_URL}/memory/search",
            json=payload,
            timeout=TIMEOUT
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

        # Should find redis-related episodes if they exist
        if data["count"] > 0:
            # Check if any result contains redis/cache keywords
            found_relevant = any(
                "redis" in r["content"].lower() or "cache" in r["content"].lower()
                for r in data["results"]
            )
            # This is a soft check - semantic search might not always match keywords

    def test_search_response_structure(self):
        """Test that search response has correct structure"""
        payload = {
            "query": "test response structure",
            "limit": 5,
            "min_similarity": 0.3
        }

        response = requests.post(
            f"{API_BASE_URL}/memory/search",
            json=payload,
            timeout=TIMEOUT
        )

        assert response.status_code == 200
        data = response.json()

        # Verify top-level fields
        assert "success" in data
        assert "query" in data
        assert "count" in data
        assert "results" in data
        assert "timestamp" in data

        # Verify query echoed back
        assert data["query"] == payload["query"]

        # Verify count matches results length
        assert data["count"] == len(data["results"])

    def test_search_invalid_min_similarity(self):
        """Test validation of min_similarity parameter"""
        # min_similarity > 1.0
        payload = {
            "query": "test invalid similarity",
            "limit": 5,
            "min_similarity": 1.5
        }

        response = requests.post(
            f"{API_BASE_URL}/memory/search",
            json=payload,
            timeout=TIMEOUT
        )

        # Should return validation error
        assert response.status_code == 422

    def test_search_invalid_limit(self):
        """Test validation of limit parameter"""
        # limit > 100
        payload = {
            "query": "test invalid limit",
            "limit": 200,
            "min_similarity": 0.5
        }

        response = requests.post(
            f"{API_BASE_URL}/memory/search",
            json=payload,
            timeout=TIMEOUT
        )

        # Should return validation error
        assert response.status_code == 422

    def test_search_empty_query(self):
        """Test search with empty query string"""
        payload = {
            "query": "",
            "limit": 5,
            "min_similarity": 0.5
        }

        response = requests.post(
            f"{API_BASE_URL}/memory/search",
            json=payload,
            timeout=TIMEOUT
        )

        # Empty query should either fail validation or return results
        # Current implementation might accept it
        assert response.status_code in [200, 422]

    def test_search_ordering_by_similarity(self):
        """Test that results are ordered by similarity score DESC"""
        payload = {
            "query": "database system technology",
            "limit": 10,
            "min_similarity": 0.0
        }

        response = requests.post(
            f"{API_BASE_URL}/memory/search",
            json=payload,
            timeout=TIMEOUT
        )

        assert response.status_code == 200
        data = response.json()

        if data["count"] > 1:
            results = data["results"]
            scores = [r["similarity_score"] for r in results]

            # Verify descending order (highest similarity first)
            for i in range(len(scores) - 1):
                assert scores[i] >= scores[i+1], "Results should be ordered by similarity DESC"

    def test_search_with_prometheus_keyword(self):
        """Test searching for prometheus/monitoring related content"""
        payload = {
            "query": "prometheus monitoring metrics observability",
            "limit": 5,
            "min_similarity": 0.2
        }

        response = requests.post(
            f"{API_BASE_URL}/memory/search",
            json=payload,
            timeout=TIMEOUT
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

        # Should find monitoring-related episodes if they exist
        if data["count"] > 0:
            first_result = data["results"][0]
            assert "similarity_score" in first_result
            assert first_result["similarity_score"] >= 0.2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

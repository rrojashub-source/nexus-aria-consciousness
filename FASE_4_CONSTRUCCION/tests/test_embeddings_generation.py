"""
Integration tests for embeddings generation system
Tests automatic embedding generation via worker
"""

import pytest
import requests
import time
import psycopg

# Test configuration
API_BASE_URL = "http://localhost:8003"
DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "nexus_memory"
DB_USER = "nexus_app"
DB_PASSWORD_FILE = "D:/01_PROYECTOS_ACTIVOS/CEREBRO_MASTER_NEXUS_001/FASE_4_CONSTRUCCION/secrets/pg_app_password.txt"

TIMEOUT = 10
WORKER_POLL_INTERVAL = 5  # seconds
MAX_WAIT_TIME = 30  # seconds


class TestEmbeddingsGeneration:
    """Test suite for automatic embeddings generation"""

    @pytest.fixture
    def db_connection(self):
        """Create database connection for direct queries"""
        try:
            with open(DB_PASSWORD_FILE, 'r') as f:
                password = f.read().strip()
        except FileNotFoundError:
            pytest.skip("Database password file not found")

        conn = psycopg.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=password
        )
        yield conn
        conn.close()

    def test_embedding_queued_on_insert(self, db_connection):
        """Test that INSERT triggers embeddings queue entry"""
        # Create episode
        payload = {
            "action_type": "test_embedding_queue",
            "action_details": {
                "message": "Test automatic embedding queue insertion",
                "importance_score": 0.7
            },
            "context_state": {"test": "queue"},
            "tags": ["test", "embeddings", "queue"]
        }

        response = requests.post(
            f"{API_BASE_URL}/memory/action",
            json=payload,
            timeout=TIMEOUT
        )

        assert response.status_code == 200
        episode_id = response.json()["episode_id"]

        # Wait briefly for trigger to fire
        time.sleep(1)

        # Check queue has entry for this episode
        with db_connection.cursor() as cur:
            cur.execute("""
                SELECT state, retry_count
                FROM memory_system.embeddings_queue
                WHERE episode_id = %s
            """, (episode_id,))
            result = cur.fetchone()

        assert result is not None, "Episode should be in embeddings queue"
        state, retry_count = result
        assert state in ["pending", "processing", "done"]
        assert retry_count >= 0

    def test_worker_processes_queue(self, db_connection):
        """Test that worker processes pending queue items"""
        # Create episode
        payload = {
            "action_type": "test_worker_processing",
            "action_details": {
                "message": "Test worker processes embeddings queue automatically",
                "importance_score": 0.8
            },
            "context_state": {"test": "worker"},
            "tags": ["test", "embeddings", "worker"]
        }

        response = requests.post(
            f"{API_BASE_URL}/memory/action",
            json=payload,
            timeout=TIMEOUT
        )

        assert response.status_code == 200
        episode_id = response.json()["episode_id"]

        # Wait for worker to process (max 30 seconds)
        start_time = time.time()
        processed = False

        while time.time() - start_time < MAX_WAIT_TIME:
            with db_connection.cursor() as cur:
                cur.execute("""
                    SELECT state, embedding IS NOT NULL as has_embedding
                    FROM memory_system.embeddings_queue eq
                    JOIN nexus_memory.zep_episodic_memory em
                        ON eq.episode_id = em.episode_id
                    WHERE eq.episode_id = %s
                """, (episode_id,))
                result = cur.fetchone()

            if result:
                state, has_embedding = result
                if state == "done" and has_embedding:
                    processed = True
                    break

            time.sleep(WORKER_POLL_INTERVAL)

        assert processed, f"Worker did not process episode within {MAX_WAIT_TIME}s"

    def test_embedding_vector_dimensions(self, db_connection):
        """Test that generated embeddings have correct dimensions (384)"""
        # Find any episode with embedding
        with db_connection.cursor() as cur:
            cur.execute("""
                SELECT episode_id, embedding
                FROM nexus_memory.zep_episodic_memory
                WHERE embedding IS NOT NULL
                LIMIT 1
            """)
            result = cur.fetchone()

        if result is None:
            pytest.skip("No episodes with embeddings found")

        episode_id, embedding = result

        # Verify embedding dimensions
        # pgvector returns as list
        assert len(embedding) == 384, "Embeddings should have 384 dimensions"

        # Verify all values are floats in reasonable range
        for val in embedding:
            assert isinstance(val, float)
            assert -10.0 < val < 10.0  # Embeddings typically normalized

    def test_queue_idempotency(self, db_connection):
        """Test that duplicate content doesn't create duplicate queue entries"""
        content = "Idempotency test content - unique string 12345"

        # Create first episode
        payload1 = {
            "action_type": "test_idempotency_1",
            "action_details": {
                "message": content,
                "importance_score": 0.6
            },
            "context_state": {"test": "idempotency"},
            "tags": ["test", "idempotency"]
        }

        response1 = requests.post(
            f"{API_BASE_URL}/memory/action",
            json=payload1,
            timeout=TIMEOUT
        )
        episode_id1 = response1.json()["episode_id"]

        # Wait for processing
        time.sleep(WORKER_POLL_INTERVAL + 2)

        # Create second episode with same content
        payload2 = {
            "action_type": "test_idempotency_2",
            "action_details": {
                "message": content,
                "importance_score": 0.6
            },
            "context_state": {"test": "idempotency"},
            "tags": ["test", "idempotency"]
        }

        response2 = requests.post(
            f"{API_BASE_URL}/memory/action",
            json=payload2,
            timeout=TIMEOUT
        )
        episode_id2 = response2.json()["episode_id"]

        # Wait for processing
        time.sleep(WORKER_POLL_INTERVAL + 2)

        # Both should be processed (no deduplication by content)
        # Queue deduplication is by episode_id, not content
        with db_connection.cursor() as cur:
            cur.execute("""
                SELECT COUNT(*)
                FROM memory_system.embeddings_queue
                WHERE episode_id IN (%s, %s)
                    AND state = 'done'
            """, (episode_id1, episode_id2))
            count = cur.fetchone()[0]

        assert count == 2, "Both episodes should be processed independently"

    def test_stats_endpoint_embeddings_count(self):
        """Test that /stats endpoint reports embeddings count correctly"""
        response = requests.get(
            f"{API_BASE_URL}/stats",
            timeout=TIMEOUT
        )

        assert response.status_code == 200
        data = response.json()

        assert "stats" in data
        stats = data["stats"]

        assert "total_episodes" in stats
        assert "episodes_with_embeddings" in stats
        assert "embeddings_queue" in stats

        # Verify counts are consistent
        assert stats["episodes_with_embeddings"] <= stats["total_episodes"]

    def test_embeddings_queue_states(self, db_connection):
        """Test that queue tracks different states correctly"""
        with db_connection.cursor() as cur:
            cur.execute("""
                SELECT state, COUNT(*)
                FROM memory_system.embeddings_queue
                GROUP BY state
            """)
            results = cur.fetchall()

        # Verify valid states
        valid_states = {"pending", "processing", "done", "dead"}
        for state, count in results:
            assert state in valid_states
            assert count > 0

    def test_embedding_not_null_after_processing(self, db_connection):
        """Test that episodes have non-null embeddings after processing"""
        # Get done queue items
        with db_connection.cursor() as cur:
            cur.execute("""
                SELECT em.episode_id, em.embedding IS NOT NULL as has_embedding
                FROM memory_system.embeddings_queue eq
                JOIN nexus_memory.zep_episodic_memory em
                    ON eq.episode_id = em.episode_id
                WHERE eq.state = 'done'
                LIMIT 5
            """)
            results = cur.fetchall()

        if not results:
            pytest.skip("No processed episodes found")

        # All done items should have embeddings
        for episode_id, has_embedding in results:
            assert has_embedding, f"Episode {episode_id} marked done but has null embedding"

    def test_worker_retry_mechanism(self, db_connection):
        """Test that queue tracks retry_count"""
        with db_connection.cursor() as cur:
            cur.execute("""
                SELECT episode_id, retry_count, state
                FROM memory_system.embeddings_queue
                ORDER BY retry_count DESC
                LIMIT 1
            """)
            result = cur.fetchone()

        if result is None:
            pytest.skip("No queue items found")

        episode_id, retry_count, state = result
        assert retry_count >= 0
        assert retry_count < 10  # Should not have excessive retries


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

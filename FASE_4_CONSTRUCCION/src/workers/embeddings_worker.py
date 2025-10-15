"""
NEXUS Cerebro - Embeddings Worker V2.0.0
Background worker for automatic embeddings generation
DÍA 5 FASE 4 - Base Implementation
"""

import os
import time
import logging
from datetime import datetime
import psycopg
from sentence_transformers import SentenceTransformer

# ============================================
# Configuration
# ============================================
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "nexus_postgresql")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
POSTGRES_DB = os.getenv("POSTGRES_DB", "nexus_memory")
POSTGRES_USER = os.getenv("POSTGRES_USER", "nexus_worker")

# Read password from Docker Secret
POSTGRES_PASSWORD_FILE = os.getenv("POSTGRES_PASSWORD_FILE", "/run/secrets/pg_worker_password")
try:
    with open(POSTGRES_PASSWORD_FILE, 'r') as f:
        POSTGRES_PASSWORD = f.read().strip()
except FileNotFoundError:
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "default_password")

# Worker configuration
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "5"))  # seconds
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "10"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "5"))
EMBEDDINGS_MODEL = os.getenv("EMBEDDINGS_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
EMBEDDING_VERSION = "miniLM-384-chunked@v2"

# Database connection string
DB_CONN_STRING = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

# ============================================
# Logging Setup
# ============================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("embeddings_worker")

# ============================================
# Embeddings Worker Class
# ============================================
class EmbeddingsWorker:
    def __init__(self):
        self.model = None
        self.conn = None
        self.running = True

    def initialize(self):
        """Initialize model and database connection"""
        try:
            logger.info(f"Loading embeddings model: {EMBEDDINGS_MODEL}")
            self.model = SentenceTransformer(EMBEDDINGS_MODEL)
            logger.info("✓ Model loaded successfully")

            logger.info("Connecting to database...")
            self.conn = psycopg.connect(DB_CONN_STRING)
            logger.info("✓ Database connected")

            return True
        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            return False

    def get_pending_items(self):
        """Get pending items from embeddings_queue"""
        try:
            with self.conn.cursor() as cur:
                # Atomic claim with SKIP LOCKED
                cur.execute("""
                    UPDATE memory_system.embeddings_queue
                    SET state = 'processing'
                    WHERE episode_id IN (
                        SELECT episode_id
                        FROM memory_system.embeddings_queue
                        WHERE state = 'pending'
                        ORDER BY priority DESC, enqueued_at ASC
                        LIMIT %s
                        FOR UPDATE SKIP LOCKED
                    )
                    RETURNING episode_id
                """, (BATCH_SIZE,))

                episode_ids = [row[0] for row in cur.fetchall()]

            self.conn.commit()

            if episode_ids:
                # Fetch content for these episodes
                with self.conn.cursor() as cur:
                    cur.execute("""
                        SELECT episode_id, content
                        FROM nexus_memory.zep_episodic_memory
                        WHERE episode_id = ANY(%s)
                    """, (episode_ids,))

                    items = cur.fetchall()

                return items
            return []

        except Exception as e:
            logger.error(f"Error fetching pending items: {e}")
            self.conn.rollback()
            return []

    def generate_embedding(self, text: str):
        """Generate embedding for text"""
        try:
            # Truncate to 4000 chars (matches trigger checksum)
            text_truncated = text[:4000] if len(text) > 4000 else text

            # Generate embedding
            embedding = self.model.encode(text_truncated)

            return embedding.tolist()

        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return None

    def process_item(self, episode_id, content):
        """Process single item"""
        try:
            # Generate embedding
            embedding = self.generate_embedding(content)

            if embedding is None:
                raise Exception("Embedding generation failed")

            # Update episode with embedding
            with self.conn.cursor() as cur:
                cur.execute("""
                    UPDATE nexus_memory.zep_episodic_memory
                    SET embedding = %s::vector,
                        embedding_version = %s
                    WHERE episode_id = %s
                """, (embedding, EMBEDDING_VERSION, episode_id))

            # Mark as done in queue
            with self.conn.cursor() as cur:
                cur.execute("""
                    UPDATE memory_system.embeddings_queue
                    SET state = 'done',
                        processed_at = NOW()
                    WHERE episode_id = %s
                """, (episode_id,))

            self.conn.commit()

            logger.info(f"✓ Processed episode {episode_id}")
            return True

        except Exception as e:
            logger.error(f"Error processing episode {episode_id}: {e}")
            self.conn.rollback()

            # Increment retry count
            try:
                with self.conn.cursor() as cur:
                    cur.execute("""
                        UPDATE memory_system.embeddings_queue
                        SET state = CASE
                                WHEN retry_count + 1 >= %s THEN 'dead'
                                ELSE 'pending'
                            END,
                            retry_count = retry_count + 1,
                            last_error = %s
                        WHERE episode_id = %s
                    """, (MAX_RETRIES, str(e), episode_id))

                self.conn.commit()
            except Exception as retry_error:
                logger.error(f"Error updating retry count: {retry_error}")
                self.conn.rollback()

            return False

    def run(self):
        """Main worker loop"""
        logger.info("=" * 60)
        logger.info("NEXUS Embeddings Worker V2.0.0 - Starting")
        logger.info("=" * 60)

        if not self.initialize():
            logger.error("Worker initialization failed. Exiting.")
            return

        logger.info(f"Worker configuration:")
        logger.info(f"  - Poll interval: {POLL_INTERVAL}s")
        logger.info(f"  - Batch size: {BATCH_SIZE}")
        logger.info(f"  - Max retries: {MAX_RETRIES}")
        logger.info(f"  - Model: {EMBEDDINGS_MODEL}")
        logger.info("=" * 60)
        logger.info("Worker ready. Polling for pending items...")

        while self.running:
            try:
                # Get pending items
                items = self.get_pending_items()

                if items:
                    logger.info(f"Processing {len(items)} items...")

                    for episode_id, content in items:
                        self.process_item(episode_id, content)

                    logger.info(f"✓ Batch processed ({len(items)} items)")
                else:
                    # No items, sleep
                    time.sleep(POLL_INTERVAL)

            except KeyboardInterrupt:
                logger.info("Shutdown signal received")
                self.running = False
            except Exception as e:
                logger.error(f"Worker error: {e}")
                time.sleep(POLL_INTERVAL * 2)  # Back off on error

        # Cleanup
        if self.conn:
            self.conn.close()

        logger.info("Worker stopped")

# ============================================
# Main
# ============================================
if __name__ == "__main__":
    worker = EmbeddingsWorker()
    worker.run()

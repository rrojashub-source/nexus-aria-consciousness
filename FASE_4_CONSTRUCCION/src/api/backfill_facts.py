#!/usr/bin/env python3
"""
NEXUS Hybrid Memory - Fact Backfill Script
===========================================
Extract facts from all existing episodes and update metadata

Created: October 27, 2025
Phase: FASE_8_UPGRADE Session 5
"""

import psycopg
from psycopg.types.json import Json
import os
import sys
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fact_extractor import extract_facts_from_content

# ============================================================
# Configuration
# ============================================================

POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "5437"))
POSTGRES_DB = os.getenv("POSTGRES_DB", "nexus_memory")
POSTGRES_USER = os.getenv("POSTGRES_USER", "nexus_superuser")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "RpKeuQhnwqMOA4iQPILQshWtwFj0P2hm")

# Batch size for processing
BATCH_SIZE = 100


# ============================================================
# Main Backfill Logic
# ============================================================

def backfill_facts():
    """
    Backfill facts for all existing episodes
    """
    print("=" * 70)
    print("NEXUS Hybrid Memory - Fact Backfill")
    print("=" * 70)
    print()

    # Connect to database
    print(f"Connecting to PostgreSQL at {POSTGRES_HOST}:{POSTGRES_PORT}...")
    conn_string = f"host={POSTGRES_HOST} port={POSTGRES_PORT} dbname={POSTGRES_DB} user={POSTGRES_USER} password={POSTGRES_PASSWORD}"

    try:
        with psycopg.connect(conn_string) as conn:
            with conn.cursor() as cur:
                # Count total episodes
                cur.execute("SELECT COUNT(*) FROM nexus_memory.zep_episodic_memory")
                total_episodes = cur.fetchone()[0]

                print(f"✅ Connected successfully")
                print(f"📊 Total episodes to process: {total_episodes}")
                print()

                # Count episodes that already have facts
                cur.execute("""
                    SELECT COUNT(*)
                    FROM nexus_memory.zep_episodic_memory
                    WHERE metadata->'facts' IS NOT NULL
                """)
                existing_facts = cur.fetchone()[0]

                print(f"📋 Episodes with existing facts: {existing_facts}")
                print(f"📋 Episodes needing extraction: {total_episodes - existing_facts}")
                print()

                # Process in batches
                processed = 0
                facts_extracted = 0
                failed = 0

                print(f"Starting batch processing (batch size: {BATCH_SIZE})...")
                print()

                offset = 0
                while offset < total_episodes:
                    # Fetch batch
                    cur.execute("""
                        SELECT episode_id, content, metadata, tags
                        FROM nexus_memory.zep_episodic_memory
                        ORDER BY created_at ASC
                        LIMIT %s OFFSET %s
                    """, (BATCH_SIZE, offset))

                    batch = cur.fetchall()

                    if not batch:
                        break

                    # Process each episode in batch
                    for row in batch:
                        episode_id = row[0]
                        content = row[1]
                        metadata = row[2] or {}
                        tags = row[3]

                        processed += 1

                        # Skip if already has facts (unless we want to re-extract)
                        if metadata.get("facts") is not None:
                            continue

                        try:
                            # Extract facts
                            facts = extract_facts_from_content(content, tags)

                            if facts:
                                # Update metadata with facts
                                metadata["facts"] = facts

                                # Update episode in database
                                cur.execute("""
                                    UPDATE nexus_memory.zep_episodic_memory
                                    SET metadata = %s
                                    WHERE episode_id = %s
                                """, (Json(metadata), episode_id))

                                facts_extracted += 1

                                # Print progress every 50 episodes
                                if facts_extracted % 50 == 0:
                                    print(f"  ✅ Processed {processed}/{total_episodes} episodes, extracted facts from {facts_extracted}")

                        except Exception as e:
                            failed += 1
                            print(f"  ❌ Error processing episode {episode_id}: {str(e)}")

                    # Commit batch
                    conn.commit()

                    offset += BATCH_SIZE

                print()
                print("=" * 70)
                print("BACKFILL COMPLETE")
                print("=" * 70)
                print(f"✅ Total episodes processed: {processed}")
                print(f"✅ Facts extracted: {facts_extracted}")
                print(f"❌ Failed: {failed}")
                print(f"📊 Success rate: {(facts_extracted/processed*100):.1f}%")
                print()

                # Final statistics
                cur.execute("""
                    SELECT COUNT(*)
                    FROM nexus_memory.zep_episodic_memory
                    WHERE metadata->'facts' IS NOT NULL
                """)
                final_with_facts = cur.fetchone()[0]

                print(f"📊 Final stats:")
                print(f"   - Total episodes: {total_episodes}")
                print(f"   - Episodes with facts: {final_with_facts} ({final_with_facts/total_episodes*100:.1f}%)")
                print()

                # Show sample of extracted facts
                print("Sample of extracted facts:")
                print("-" * 70)

                cur.execute("""
                    SELECT episode_id, metadata->'facts' as facts
                    FROM nexus_memory.zep_episodic_memory
                    WHERE metadata->'facts' IS NOT NULL
                    ORDER BY created_at DESC
                    LIMIT 5
                """)

                samples = cur.fetchall()
                for i, (ep_id, facts) in enumerate(samples, 1):
                    print(f"\n{i}. Episode {ep_id}:")
                    if isinstance(facts, dict):
                        for key, value in facts.items():
                            if key not in ["extraction_method", "extraction_confidence", "last_updated"]:
                                print(f"   - {key}: {value}")

                print()

    except Exception as e:
        print(f"❌ Error connecting to database: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    start_time = datetime.now()
    backfill_facts()
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    print(f"⏱️  Total time: {duration:.2f} seconds")
    print()

"""
NEXUS Cerebro API V2.0.0
FastAPI Application - Core Endpoints
DÍA 5 FASE 4 - Base Implementation
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import os
import psycopg
from psycopg.types.json import Json
from contextlib import asynccontextmanager
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response
import time
import redis
import json as json_module
from sentence_transformers import SentenceTransformer

# FASE_8_UPGRADE: Hybrid Memory System
import sys
import os
# Add current directory to Python path for hybrid memory modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fact_extractor import extract_facts_from_content
from fact_schemas import FactQueryRequest, FactQueryResponse, HybridQueryRequest, HybridQueryResponse

# ============================================
# Configuration
# ============================================
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "nexus_postgresql")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
POSTGRES_DB = os.getenv("POSTGRES_DB", "nexus_memory")
POSTGRES_USER = os.getenv("POSTGRES_USER", "nexus_superuser")

# Read password from Docker Secret
POSTGRES_PASSWORD_FILE = os.getenv("POSTGRES_PASSWORD_FILE", "/run/secrets/pg_superuser_password")
try:
    with open(POSTGRES_PASSWORD_FILE, 'r') as f:
        POSTGRES_PASSWORD = f.read().strip()
except FileNotFoundError:
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "default_password")

# ============================================
# Prometheus Metrics
# ============================================

# API Metrics
api_requests_total = Counter(
    'nexus_api_requests_total',
    'Total API requests',
    ['method', 'endpoint', 'status']
)

api_request_duration_seconds = Histogram(
    'nexus_api_request_duration_seconds',
    'API request duration in seconds',
    ['method', 'endpoint']
)

# Memory Metrics
episodes_created_total = Counter(
    'nexus_episodes_created_total',
    'Total episodes created'
)

episodes_total = Gauge(
    'nexus_episodes_total',
    'Total episodes in database'
)

episodes_with_embeddings = Gauge(
    'nexus_episodes_with_embeddings',
    'Total episodes with embeddings generated'
)

embeddings_queue_depth = Gauge(
    'nexus_embeddings_queue_depth',
    'Current depth of embeddings queue',
    ['state']
)

# ============================================
# Database Connection
# ============================================
DB_CONN_STRING = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

# ============================================
# Redis Configuration
# ============================================
REDIS_HOST = os.getenv("REDIS_HOST", "nexus_redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
REDIS_CACHE_TTL = int(os.getenv("REDIS_CACHE_TTL", "300"))  # 5 minutes

# Read Redis password from Docker Secret
REDIS_PASSWORD_FILE = os.getenv("REDIS_PASSWORD_FILE", "/run/secrets/redis_password")
try:
    with open(REDIS_PASSWORD_FILE, 'r') as f:
        REDIS_PASSWORD = f.read().strip()
except FileNotFoundError:
    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")

# ============================================
# Embeddings Model Configuration
# ============================================
EMBEDDINGS_MODEL = os.getenv("EMBEDDINGS_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

# Global model instance (loaded in lifespan)
embeddings_model = None

# ============================================
# Pydantic Models
# ============================================
class MemoryActionRequest(BaseModel):
    action_type: str = Field(..., description="Type of action to perform")
    action_details: Dict[str, Any] = Field(default_factory=dict)
    context_state: Optional[Dict[str, Any]] = Field(default_factory=dict)
    tags: Optional[List[str]] = Field(default_factory=list)

class MemoryActionResponse(BaseModel):
    success: bool
    episode_id: Optional[str] = None
    timestamp: datetime
    message: str

class HealthResponse(BaseModel):
    status: str
    version: str
    agent_id: str
    database: str
    redis: Optional[str] = None
    queue_depth: Optional[int] = None
    timestamp: datetime

class SearchRequest(BaseModel):
    query: str = Field(..., description="Search query text")
    limit: int = Field(default=10, ge=1, le=100, description="Maximum number of results")
    min_similarity: float = Field(default=0.5, ge=0.0, le=1.0, description="Minimum similarity threshold (0-1)")

class SearchResult(BaseModel):
    episode_id: str
    content: str
    similarity_score: float
    importance_score: float
    tags: List[str]
    created_at: datetime

class SearchResponse(BaseModel):
    success: bool
    query: str
    count: int
    results: List[SearchResult]
    timestamp: datetime

# ============================================
# FASE_8_UPGRADE: Temporal Reasoning Models
# ============================================
class TemporalBeforeRequest(BaseModel):
    timestamp: datetime = Field(..., description="Get episodes before this timestamp")
    limit: int = Field(default=10, ge=1, le=100, description="Maximum number of results")
    tags: Optional[List[str]] = Field(default=None, description="Optional: filter by tags")

class TemporalAfterRequest(BaseModel):
    timestamp: datetime = Field(..., description="Get episodes after this timestamp")
    limit: int = Field(default=10, ge=1, le=100, description="Maximum number of results")
    tags: Optional[List[str]] = Field(default=None, description="Optional: filter by tags")

class TemporalRangeRequest(BaseModel):
    start: datetime = Field(..., description="Start of time range")
    end: datetime = Field(..., description="End of time range")
    limit: int = Field(default=50, ge=1, le=200, description="Maximum number of results")
    tags: Optional[List[str]] = Field(default=None, description="Optional: filter by tags")

class TemporalRelatedRequest(BaseModel):
    episode_id: str = Field(..., description="Episode UUID to find related episodes")
    relationship_type: Optional[str] = Field(default=None, description="Type: 'before', 'after', 'causes', 'effects', or None for all")

class TemporalLinkRequest(BaseModel):
    source_id: str = Field(..., description="Source episode UUID")
    target_id: str = Field(..., description="Target episode UUID")
    relationship: str = Field(..., description="Relationship type: 'before', 'after', 'causes', 'effects'")

class TemporalEpisode(BaseModel):
    episode_id: str
    content: str
    importance_score: float
    tags: List[str]
    created_at: datetime

class TemporalResponse(BaseModel):
    success: bool
    count: int
    episodes: List[TemporalEpisode]
    timestamp: datetime

# ============================================
# Lifespan Context Manager
# ============================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    global embeddings_model

    # Startup - Initialize Redis connection
    try:
        app.state.redis_client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            password=REDIS_PASSWORD if REDIS_PASSWORD else None,
            decode_responses=True,
            socket_connect_timeout=5
        )
        # Test connection
        app.state.redis_client.ping()
        print(f"✓ Redis connected: {REDIS_HOST}:{REDIS_PORT}")
    except Exception as e:
        print(f"⚠ Redis connection failed: {e}")
        app.state.redis_client = None

    # Startup - Load embeddings model
    try:
        print(f"Loading embeddings model: {EMBEDDINGS_MODEL}")
        embeddings_model = SentenceTransformer(EMBEDDINGS_MODEL)
        print(f"✓ Embeddings model loaded successfully")
    except Exception as e:
        print(f"⚠ Embeddings model loading failed: {e}")
        embeddings_model = None

    yield

    # Shutdown - Close Redis connection
    if app.state.redis_client:
        app.state.redis_client.close()

# ============================================
# FastAPI App
# ============================================
app = FastAPI(
    title="NEXUS Cerebro API",
    description="Memory System API - V2.0.0",
    version="2.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus Middleware for automatic tracking
@app.middleware("http")
async def prometheus_middleware(request, call_next):
    """Track all HTTP requests with Prometheus metrics"""
    start_time = time.time()

    # Execute request
    response = await call_next(request)

    # Calculate duration
    duration = time.time() - start_time

    # Record metrics
    endpoint = request.url.path
    method = request.method
    status_code = str(response.status_code)

    api_requests_total.labels(method=method, endpoint=endpoint, status=status_code).inc()
    api_request_duration_seconds.labels(method=method, endpoint=endpoint).observe(duration)

    return response

# ============================================
# Helper Functions
# ============================================
def get_db_connection():
    """Get database connection"""
    try:
        conn = psycopg.connect(DB_CONN_STRING)
        return conn
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection failed: {str(e)}"
        )

def get_redis_client():
    """Get Redis client from app state"""
    return app.state.redis_client if hasattr(app.state, 'redis_client') else None

def cache_get(key: str):
    """Get value from Redis cache"""
    try:
        redis_client = get_redis_client()
        if redis_client:
            value = redis_client.get(key)
            if value:
                return json_module.loads(value)
    except Exception as e:
        print(f"Cache get error: {e}")
    return None

def cache_set(key: str, value: any, ttl: int = REDIS_CACHE_TTL):
    """Set value in Redis cache with TTL"""
    try:
        redis_client = get_redis_client()
        if redis_client:
            redis_client.setex(
                key,
                ttl,
                json_module.dumps(value, default=str)
            )
    except Exception as e:
        print(f"Cache set error: {e}")

def cache_invalidate(pattern: str):
    """Invalidate cache keys matching pattern"""
    try:
        redis_client = get_redis_client()
        if redis_client:
            keys = redis_client.keys(pattern)
            if keys:
                redis_client.delete(*keys)
    except Exception as e:
        print(f"Cache invalidate error: {e}")

def generate_query_embedding(text: str):
    """Generate embedding for search query"""
    global embeddings_model

    if embeddings_model is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Embeddings model not loaded"
        )

    try:
        # Truncate to 4000 chars (same as worker)
        text_truncated = text[:4000] if len(text) > 4000 else text

        # Generate embedding
        embedding = embeddings_model.encode(text_truncated)

        return embedding.tolist()

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating embedding: {str(e)}"
        )

# ============================================
# Endpoints
# ============================================

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "service": "NEXUS Cerebro API",
        "version": "2.0.0",
        "status": "operational",
        "docs": "/docs"
    }

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Advanced health check endpoint - checks PostgreSQL, Redis, and Queue depth"""
    db_status = "unknown"
    redis_status = "unknown"
    queue_depth = None
    overall_status = "healthy"

    # Check PostgreSQL
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
            result = cur.fetchone()

            # Get queue depth
            cur.execute("""
                SELECT COUNT(*)
                FROM memory_system.embeddings_queue
                WHERE state IN ('pending', 'processing')
            """)
            queue_depth = cur.fetchone()[0]

        conn.close()
        db_status = "connected" if result else "disconnected"
    except Exception as e:
        db_status = f"error: {str(e)[:100]}"
        overall_status = "unhealthy"

    # Check Redis
    try:
        redis_client = get_redis_client()
        if redis_client:
            redis_client.ping()
            redis_status = "connected"
        else:
            redis_status = "not_initialized"
    except Exception as e:
        redis_status = f"error: {str(e)[:100]}"
        overall_status = "degraded"  # Redis failure is degraded, not unhealthy

    # Overall status evaluation
    if queue_depth and queue_depth > 1000:
        overall_status = "degraded"  # High queue depth is warning

    return HealthResponse(
        status=overall_status,
        version="2.0.0",
        agent_id="nexus",
        database=db_status,
        redis=redis_status,
        queue_depth=queue_depth,
        timestamp=datetime.now()
        )

@app.post("/memory/action", response_model=MemoryActionResponse, tags=["Memory"])
async def memory_action(request: MemoryActionRequest):
    """
    Create episodic memory entry
    Automatically triggers embeddings generation via database trigger
    """
    try:
        conn = get_db_connection()

        # Prepare content from action_details
        # FIXED: Use actual content field if exists, otherwise serialize full details
        if "content" in request.action_details:
            # Use explicit content field
            content = request.action_details["content"]
        elif request.action_details:
            # Serialize full action_details as JSON string for embeddings
            content = json_module.dumps(request.action_details, indent=2, default=str)
        else:
            # Fallback to action_type only
            content = request.action_type

        # Calculate importance_score (default 0.5, can be customized)
        importance_score = request.action_details.get("importance_score", 0.5) if request.action_details else 0.5

        # Insert into episodic memory
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO nexus_memory.zep_episodic_memory
                (content, importance_score, tags, metadata)
                VALUES (%s, %s, %s, %s)
                RETURNING episode_id, created_at
            """, (
                content,
                importance_score,
                request.tags or [],
                Json({
                    "action_type": request.action_type,
                    "action_details": request.action_details,
                    "context_state": request.context_state
                })
            ))

            result = cur.fetchone()
            episode_id = str(result[0])
            created_at = result[1]

        conn.commit()
        conn.close()

        # Invalidate episodes cache
        cache_invalidate("episodes:recent:*")

        # Increment Prometheus counter
        episodes_created_total.inc()

        return MemoryActionResponse(
            success=True,
            episode_id=episode_id,
            timestamp=created_at,
            message="Acción registrada exitosamente"
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating memory: {str(e)}"
        )

@app.get("/memory/episodic/recent", tags=["Memory"])
async def get_recent_episodes(limit: int = 10):
    """Get recent episodic memories with Redis cache"""
    try:
        # Try cache first
        cache_key = f"episodes:recent:{limit}"
        cached_data = cache_get(cache_key)
        if cached_data:
            cached_data["cached"] = True
            return cached_data

        # Cache miss - query database
        conn = get_db_connection()

        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    episode_id,
                    content,
                    importance_score,
                    tags,
                    created_at,
                    embedding IS NOT NULL as has_embedding
                FROM nexus_memory.zep_episodic_memory
                ORDER BY created_at DESC
                LIMIT %s
            """, (limit,))

            results = cur.fetchall()

        conn.close()

        episodes = []
        for row in results:
            episodes.append({
                "episode_id": str(row[0]),
                "content": row[1],
                "importance_score": row[2],
                "tags": row[3] or [],
                "created_at": row[4].isoformat(),
                "has_embedding": row[5]
            })

        response = {
            "success": True,
            "count": len(episodes),
            "episodes": episodes,
            "cached": False
        }

        # Store in cache
        cache_set(cache_key, response)

        return response

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching episodes: {str(e)}"
        )

@app.post("/memory/search", response_model=SearchResponse, tags=["Memory"])
async def search_memories(request: SearchRequest):
    """
    Semantic search using vector embeddings
    Uses cosine similarity with pgvector to find most relevant episodes
    """
    try:
        # Generate embedding for search query
        query_embedding = generate_query_embedding(request.query)

        # Perform vector similarity search
        conn = get_db_connection()

        with conn.cursor() as cur:
            # Cosine similarity search using pgvector <=> operator
            # Lower distance = higher similarity
            # Convert distance to similarity score (1 - distance)
            cur.execute("""
                SELECT
                    episode_id,
                    content,
                    importance_score,
                    tags,
                    created_at,
                    1 - (embedding <=> %s::vector) as similarity_score
                FROM nexus_memory.zep_episodic_memory
                WHERE embedding IS NOT NULL
                    AND 1 - (embedding <=> %s::vector) >= %s
                ORDER BY embedding <=> %s::vector
                LIMIT %s
            """, (
                query_embedding,
                query_embedding,
                request.min_similarity,
                query_embedding,
                request.limit
            ))

            results = cur.fetchall()

        # Track access for retrieved episodes (intelligent decay feature)
        if results:
            episode_ids = [str(row[0]) for row in results]
            for ep_id in episode_ids:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT nexus_memory.update_access_tracking(%s::uuid)
                    """, (ep_id,))
            conn.commit()

        conn.close()

        # Build search results
        search_results = []
        for row in results:
            search_results.append(SearchResult(
                episode_id=str(row[0]),
                content=row[1],
                similarity_score=float(row[5]),
                importance_score=float(row[2]),
                tags=row[3] or [],
                created_at=row[4]
            ))

        return SearchResponse(
            success=True,
            query=request.query,
            count=len(search_results),
            results=search_results,
            timestamp=datetime.now()
        )

    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error performing search: {str(e)}"
        )

@app.get("/stats", tags=["Stats"])
async def get_stats():
    """Get database statistics and update Prometheus gauges"""
    try:
        conn = get_db_connection()

        with conn.cursor() as cur:
            # Count episodic memories
            cur.execute("SELECT COUNT(*) FROM nexus_memory.zep_episodic_memory")
            total_episodes = cur.fetchone()[0]

            # Count embeddings queue
            cur.execute("SELECT state, COUNT(*) FROM memory_system.embeddings_queue GROUP BY state")
            queue_stats = {row[0]: row[1] for row in cur.fetchall()}

            # Count with embeddings
            cur.execute("SELECT COUNT(*) FROM nexus_memory.zep_episodic_memory WHERE embedding IS NOT NULL")
            total_with_embeddings = cur.fetchone()[0]

        conn.close()

        # Update Prometheus gauges
        episodes_total.set(total_episodes)
        episodes_with_embeddings.set(total_with_embeddings)

        # Update queue depth metrics
        for state in ['pending', 'processing', 'done', 'dead']:
            count = queue_stats.get(state, 0)
            embeddings_queue_depth.labels(state=state).set(count)

        return {
            "success": True,
            "agent_id": "nexus",
            "stats": {
                "total_episodes": total_episodes,
                "episodes_with_embeddings": total_with_embeddings,
                "embeddings_queue": queue_stats
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching stats: {str(e)}"
        )

# ============================================
# FASE_8_UPGRADE: Temporal Reasoning Endpoints
# ============================================

@app.post("/memory/temporal/before", response_model=TemporalResponse, tags=["Temporal"])
async def get_episodes_before(request: TemporalBeforeRequest):
    """
    Get episodes that occurred before a specific timestamp
    Ordered by timestamp DESC (most recent first)
    """
    try:
        conn = get_db_connection()

        with conn.cursor() as cur:
            # Base query
            query = """
                SELECT episode_id, content, importance_score, tags, created_at
                FROM nexus_memory.zep_episodic_memory
                WHERE created_at < %s
            """
            params = [request.timestamp]

            # Optional: filter by tags
            if request.tags:
                query += " AND tags && %s"
                params.append(request.tags)

            query += " ORDER BY created_at DESC LIMIT %s"
            params.append(request.limit)

            cur.execute(query, params)
            results = cur.fetchall()

        conn.close()

        # Build response
        episodes = []
        for row in results:
            episodes.append(TemporalEpisode(
                episode_id=str(row[0]),
                content=row[1],
                importance_score=float(row[2]),
                tags=row[3] or [],
                created_at=row[4]
            ))

        return TemporalResponse(
            success=True,
            count=len(episodes),
            episodes=episodes,
            timestamp=datetime.now()
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching episodes before timestamp: {str(e)}"
        )

@app.post("/memory/temporal/after", response_model=TemporalResponse, tags=["Temporal"])
async def get_episodes_after(request: TemporalAfterRequest):
    """
    Get episodes that occurred after a specific timestamp
    Ordered by timestamp ASC (oldest first)
    """
    try:
        conn = get_db_connection()

        with conn.cursor() as cur:
            # Base query
            query = """
                SELECT episode_id, content, importance_score, tags, created_at
                FROM nexus_memory.zep_episodic_memory
                WHERE created_at > %s
            """
            params = [request.timestamp]

            # Optional: filter by tags
            if request.tags:
                query += " AND tags && %s"
                params.append(request.tags)

            query += " ORDER BY created_at ASC LIMIT %s"
            params.append(request.limit)

            cur.execute(query, params)
            results = cur.fetchall()

        conn.close()

        # Build response
        episodes = []
        for row in results:
            episodes.append(TemporalEpisode(
                episode_id=str(row[0]),
                content=row[1],
                importance_score=float(row[2]),
                tags=row[3] or [],
                created_at=row[4]
            ))

        return TemporalResponse(
            success=True,
            count=len(episodes),
            episodes=episodes,
            timestamp=datetime.now()
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching episodes after timestamp: {str(e)}"
        )

@app.post("/memory/temporal/range", response_model=TemporalResponse, tags=["Temporal"])
async def get_episodes_in_range(request: TemporalRangeRequest):
    """
    Get episodes that occurred between two timestamps
    Ordered by timestamp ASC (chronological order)
    """
    try:
        conn = get_db_connection()

        with conn.cursor() as cur:
            # Base query
            query = """
                SELECT episode_id, content, importance_score, tags, created_at
                FROM nexus_memory.zep_episodic_memory
                WHERE created_at BETWEEN %s AND %s
            """
            params = [request.start, request.end]

            # Optional: filter by tags
            if request.tags:
                query += " AND tags && %s"
                params.append(request.tags)

            query += " ORDER BY created_at ASC LIMIT %s"
            params.append(request.limit)

            cur.execute(query, params)
            results = cur.fetchall()

        # Track access for retrieved episodes
        if results:
            episode_ids = [str(row[0]) for row in results]
            for ep_id in episode_ids:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT nexus_memory.update_access_tracking(%s::uuid)
                    """, (ep_id,))
            conn.commit()

        conn.close()

        # Build response
        episodes = []
        for row in results:
            episodes.append(TemporalEpisode(
                episode_id=str(row[0]),
                content=row[1],
                importance_score=float(row[2]),
                tags=row[3] or [],
                created_at=row[4]
            ))

        return TemporalResponse(
            success=True,
            count=len(episodes),
            episodes=episodes,
            timestamp=datetime.now()
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching episodes in range: {str(e)}"
        )

@app.post("/memory/temporal/related", response_model=TemporalResponse, tags=["Temporal"])
async def get_temporally_related(request: TemporalRelatedRequest):
    """
    Get episodes linked via temporal_refs metadata
    Uses PostgreSQL function get_temporal_refs() from Phase 1
    """
    try:
        conn = get_db_connection()

        with conn.cursor() as cur:
            # Use Phase 1 SQL function to get temporal refs
            if request.relationship_type:
                # Get specific relationship type
                cur.execute("""
                    SELECT ref_episode_id
                    FROM nexus_memory.get_temporal_refs(%s::uuid, %s)
                """, (request.episode_id, request.relationship_type))
            else:
                # Get all relationships
                cur.execute("""
                    SELECT ref_episode_id
                    FROM nexus_memory.get_temporal_refs(%s::uuid)
                """, (request.episode_id,))

            ref_ids = [row[0] for row in cur.fetchall()]

            # If no references found, return empty
            if not ref_ids:
                conn.close()
                return TemporalResponse(
                    success=True,
                    count=0,
                    episodes=[],
                    timestamp=datetime.now()
                )

            # Fetch full episode data for referenced episodes
            cur.execute("""
                SELECT episode_id, content, importance_score, tags, created_at
                FROM nexus_memory.zep_episodic_memory
                WHERE episode_id = ANY(%s)
                ORDER BY created_at DESC
            """, (ref_ids,))

            results = cur.fetchall()

        conn.close()

        # Build response
        episodes = []
        for row in results:
            episodes.append(TemporalEpisode(
                episode_id=str(row[0]),
                content=row[1],
                importance_score=float(row[2]),
                tags=row[3] or [],
                created_at=row[4]
            ))

        return TemporalResponse(
            success=True,
            count=len(episodes),
            episodes=episodes,
            timestamp=datetime.now()
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching related episodes: {str(e)}"
        )

@app.post("/memory/temporal/link", tags=["Temporal"])
async def link_episodes_temporally(request: TemporalLinkRequest):
    """
    Create temporal relationship between two episodes
    Uses PostgreSQL function add_temporal_ref() from Phase 1
    """
    try:
        # Validate relationship type
        valid_types = ['before', 'after', 'causes', 'effects']
        if request.relationship not in valid_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid relationship type. Must be one of: {valid_types}"
            )

        conn = get_db_connection()

        with conn.cursor() as cur:
            # Use Phase 1 SQL function to add temporal reference
            cur.execute("""
                SELECT nexus_memory.add_temporal_ref(%s::uuid, %s::uuid, %s)
            """, (request.source_id, request.target_id, request.relationship))

        conn.commit()
        conn.close()

        # Invalidate cache (if temporal queries are cached in future)
        cache_invalidate(f"temporal:related:{request.source_id}")

        return {
            "success": True,
            "message": f"Temporal link created: {request.source_id} --{request.relationship}--> {request.target_id}",
            "timestamp": datetime.now()
        }

    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating temporal link: {str(e)}"
        )

# ============================================
# FASE_8_UPGRADE: Consciousness Integration
# ============================================

class ConsciousnessUpdateRequest(BaseModel):
    state_type: str = Field(..., description="Type: 'emotional' or 'somatic'")
    state_data: Dict[str, Any] = Field(..., description="State values (e.g., joy, trust, valence, arousal)")
    importance: float = Field(default=0.7, ge=0.0, le=1.0)
    tags: Optional[List[str]] = Field(default_factory=list)
    auto_link_previous: bool = Field(default=True, description="Automatically link to previous state")

class ConsciousnessUpdateResponse(BaseModel):
    success: bool
    episode_id: str
    linked_to_previous: Optional[str] = None
    temporal_chain_length: int = 0
    timestamp: datetime

# ============================================
# Intelligent Decay Models
# ============================================
class DecayAnalysisRequest(BaseModel):
    limit: int = Field(default=100, ge=1, le=1000, description="Max episodes to analyze")
    min_age_days: int = Field(default=30, ge=0, description="Only analyze episodes older than this")

class DecayScoreDistribution(BaseModel):
    score_category: str
    episode_count: int
    avg_score: float

class DecayAnalysisResponse(BaseModel):
    success: bool
    total_analyzed: int
    distribution: List[DecayScoreDistribution]
    low_value_count: int  # decay_score < 0.2
    high_value_count: int  # decay_score > 0.7
    timestamp: datetime

class PruningPreviewRequest(BaseModel):
    min_score_threshold: float = Field(default=0.2, ge=0.0, le=1.0)
    min_age_days: int = Field(default=90, ge=30)
    max_prune_count: int = Field(default=100, ge=1, le=500)

class PruningCandidate(BaseModel):
    episode_id: str
    content_preview: str
    decay_score: float
    importance_score: float
    age_days: int
    tags: List[str]

class PruningPreviewResponse(BaseModel):
    success: bool
    candidate_count: int
    candidates: List[PruningCandidate]
    would_prune: int
    protected_count: int
    timestamp: datetime

class PruningExecuteRequest(BaseModel):
    min_score_threshold: float = Field(default=0.2, ge=0.0, le=1.0)
    min_age_days: int = Field(default=90, ge=30)
    max_prune_count: int = Field(default=100, ge=1, le=500)
    dry_run: bool = Field(default=True, description="Safety: default to dry-run mode")

class PruningExecuteResponse(BaseModel):
    success: bool
    pruned_count: int
    dry_run: bool
    timestamp: datetime

@app.post("/memory/consciousness/update", response_model=ConsciousnessUpdateResponse, tags=["Consciousness"])
async def update_consciousness_state(request: ConsciousnessUpdateRequest):
    """
    Update consciousness state (emotional or somatic) with automatic temporal linking

    Automatically links to the previous state of the same type, creating temporal chains
    that track consciousness evolution over time.
    """
    try:
        # Validate state type
        if request.state_type not in ["emotional", "somatic"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="state_type must be 'emotional' or 'somatic'"
            )

        # Build tags
        tags = request.tags.copy()
        tags.extend(["consciousness", f"{request.state_type}_state"])

        # Create episode content
        content = f"Consciousness {request.state_type} state update: {json_module.dumps(request.state_data, indent=2)}"

        # Get database connection
        conn = get_db_connection()

        previous_episode_id = None
        chain_length = 0

        # Find previous state of same type (if auto_link enabled)
        if request.auto_link_previous:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT episode_id, metadata
                    FROM nexus_memory.zep_episodic_memory
                    WHERE %s = ANY(tags)
                    ORDER BY created_at DESC
                    LIMIT 1
                """, (f"{request.state_type}_state",))

                previous = cur.fetchone()
                if previous:
                    previous_episode_id = str(previous[0])

                    # Calculate chain length from previous state
                    prev_metadata = previous[1] or {}
                    prev_chain_length = prev_metadata.get("temporal_chain_length", 0)
                    chain_length = prev_chain_length + 1

        # Create new episode
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO nexus_memory.zep_episodic_memory
                (content, importance_score, tags, metadata)
                VALUES (%s, %s, %s, %s)
                RETURNING episode_id, created_at
            """, (
                content,
                request.importance,
                tags,
                Json({
                    "state_type": request.state_type,
                    "state_data": request.state_data,
                    "temporal_chain_length": chain_length
                })
            ))

            result = cur.fetchone()
            new_episode_id = str(result[0])
            created_at = result[1]

        # Create temporal link if previous exists
        if previous_episode_id and request.auto_link_previous:
            with conn.cursor() as cur:
                # Link: new_episode --after--> previous_episode
                cur.execute("""
                    SELECT nexus_memory.add_temporal_ref(%s::uuid, %s::uuid, 'after')
                """, (new_episode_id, previous_episode_id))

        conn.commit()
        conn.close()

        # Invalidate cache
        cache_invalidate("consciousness:*")

        # Increment metrics
        episodes_created_total.inc()

        return ConsciousnessUpdateResponse(
            success=True,
            episode_id=new_episode_id,
            linked_to_previous=previous_episode_id,
            temporal_chain_length=chain_length,
            timestamp=created_at
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating consciousness state: {str(e)}"
        )

# ============================================
# Intelligent Decay Endpoints
# ============================================

@app.post("/memory/analysis/decay-scores", response_model=DecayAnalysisResponse, tags=["Intelligent Decay"])
async def analyze_decay_scores(request: DecayAnalysisRequest):
    """
    Analyze decay score distribution across episodic memory

    Calculates decay scores using the intelligent decay algorithm:
    - Importance factor (50%): Original importance_score
    - Recency factor (30%): Exponential decay based on age
    - Access factor (20%): Frequency + recency of access

    Returns distribution by score category and counts
    """
    try:
        conn = get_db_connection()

        with conn.cursor() as cur:
            # Calculate decay scores and distribution
            cur.execute("""
                WITH decay_scores AS (
                    SELECT
                        episode_id,
                        nexus_memory.calculate_decay_score(
                            importance_score,
                            created_at,
                            metadata
                        ) as decay_score,
                        EXTRACT(EPOCH FROM (NOW() - created_at)) / 86400.0 as age_days
                    FROM nexus_memory.zep_episodic_memory
                    WHERE EXTRACT(EPOCH FROM (NOW() - created_at)) / 86400.0 >= %s
                    LIMIT %s
                )
                SELECT
                    CASE
                        WHEN decay_score >= 0.8 THEN 'Very High (0.8-1.0)'
                        WHEN decay_score >= 0.6 THEN 'High (0.6-0.8)'
                        WHEN decay_score >= 0.4 THEN 'Medium (0.4-0.6)'
                        WHEN decay_score >= 0.2 THEN 'Low (0.2-0.4)'
                        ELSE 'Very Low (0.0-0.2)'
                    END as score_category,
                    COUNT(*) as episode_count,
                    ROUND(AVG(decay_score)::NUMERIC, 3) as avg_score
                FROM decay_scores
                GROUP BY CASE
                    WHEN decay_score >= 0.8 THEN 'Very High (0.8-1.0)'
                    WHEN decay_score >= 0.6 THEN 'High (0.6-0.8)'
                    WHEN decay_score >= 0.4 THEN 'Medium (0.4-0.6)'
                    WHEN decay_score >= 0.2 THEN 'Low (0.2-0.4)'
                    ELSE 'Very Low (0.0-0.2)'
                END
                ORDER BY MIN(decay_score) DESC
            """, (request.min_age_days, request.limit))

            distribution_rows = cur.fetchall()

            # Count low/high value episodes
            cur.execute("""
                WITH decay_scores AS (
                    SELECT
                        nexus_memory.calculate_decay_score(
                            importance_score,
                            created_at,
                            metadata
                        ) as decay_score
                    FROM nexus_memory.zep_episodic_memory
                    WHERE EXTRACT(EPOCH FROM (NOW() - created_at)) / 86400.0 >= %s
                    LIMIT %s
                )
                SELECT
                    SUM(CASE WHEN decay_score < 0.2 THEN 1 ELSE 0 END) as low_value_count,
                    SUM(CASE WHEN decay_score > 0.7 THEN 1 ELSE 0 END) as high_value_count,
                    COUNT(*) as total_count
                FROM decay_scores
            """, (request.min_age_days, request.limit))

            counts = cur.fetchone()

        conn.close()

        # Build distribution
        distribution = []
        for row in distribution_rows:
            distribution.append(DecayScoreDistribution(
                score_category=row[0],
                episode_count=row[1],
                avg_score=float(row[2])
            ))

        return DecayAnalysisResponse(
            success=True,
            total_analyzed=counts[2],
            distribution=distribution,
            low_value_count=counts[0],
            high_value_count=counts[1],
            timestamp=datetime.now()
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing decay scores: {str(e)}"
        )

@app.post("/memory/pruning/preview", response_model=PruningPreviewResponse, tags=["Intelligent Decay"])
async def preview_pruning(request: PruningPreviewRequest):
    """
    Preview episodes that would be pruned based on decay scores

    Safety rules (never prune):
    - Episodes with importance_score > 0.8
    - Episodes with protected tags: milestone, critical, protected, consciousness
    - Episodes younger than min_age_days
    - Episodes accessed in last 7 days

    Returns list of pruning candidates for review
    """
    try:
        conn = get_db_connection()

        protected_tags = ['milestone', 'critical', 'protected', 'consciousness']

        with conn.cursor() as cur:
            # Find pruning candidates
            cur.execute("""
                WITH decay_scores AS (
                    SELECT
                        episode_id,
                        content,
                        importance_score,
                        tags,
                        created_at,
                        metadata,
                        nexus_memory.calculate_decay_score(
                            importance_score,
                            created_at,
                            metadata
                        ) as decay_score,
                        EXTRACT(EPOCH FROM (NOW() - created_at)) / 86400.0 as age_days,
                        CASE
                            WHEN metadata->'access_tracking'->>'last_accessed' IS NOT NULL THEN
                                EXTRACT(EPOCH FROM (NOW() - (metadata->'access_tracking'->>'last_accessed')::TIMESTAMPTZ)) / 86400.0
                            ELSE
                                999999  -- Never accessed
                        END as last_accessed_days
                    FROM nexus_memory.zep_episodic_memory
                )
                SELECT
                    episode_id,
                    LEFT(content, 100) as content_preview,
                    decay_score,
                    importance_score,
                    age_days,
                    tags,
                    CASE
                        WHEN importance_score > 0.8 THEN 1
                        WHEN tags && %s THEN 1
                        WHEN age_days < %s THEN 1
                        WHEN last_accessed_days < 7 THEN 1
                        ELSE 0
                    END as is_protected
                FROM decay_scores
                WHERE decay_score < %s
                    AND age_days >= %s
                ORDER BY decay_score ASC
                LIMIT %s
            """, (protected_tags, request.min_age_days, request.min_score_threshold,
                  request.min_age_days, request.max_prune_count))

            candidates_rows = cur.fetchall()

        conn.close()

        # Build candidate list
        candidates = []
        protected_count = 0
        would_prune = 0

        for row in candidates_rows:
            is_protected = row[6]

            if is_protected:
                protected_count += 1
            else:
                would_prune += 1

            candidates.append(PruningCandidate(
                episode_id=str(row[0]),
                content_preview=row[1],
                decay_score=float(row[2]),
                importance_score=float(row[3]),
                age_days=int(row[4]),
                tags=row[5] or []
            ))

        return PruningPreviewResponse(
            success=True,
            candidate_count=len(candidates),
            candidates=candidates,
            would_prune=would_prune,
            protected_count=protected_count,
            timestamp=datetime.now()
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error previewing pruning: {str(e)}"
        )

@app.post("/memory/pruning/execute", response_model=PruningExecuteResponse, tags=["Intelligent Decay"])
async def execute_pruning(request: PruningExecuteRequest):
    """
    Execute memory pruning based on decay scores

    **IMPORTANT:** Defaults to dry_run=True for safety

    Safety mechanisms:
    - Never prunes importance_score > 0.8
    - Never prunes protected tags
    - Never prunes episodes < min_age_days old
    - Never prunes recently accessed episodes
    - Caps at max_prune_count per operation

    Pruned episodes are soft-deleted (moved to archive table, not lost)
    """
    try:
        if request.dry_run:
            # Dry run mode: just count what would be pruned
            conn = get_db_connection()

            protected_tags = ['milestone', 'critical', 'protected', 'consciousness']

            with conn.cursor() as cur:
                cur.execute("""
                    WITH decay_scores AS (
                        SELECT
                            episode_id,
                            nexus_memory.calculate_decay_score(
                                importance_score,
                                created_at,
                                metadata
                            ) as decay_score,
                            importance_score,
                            EXTRACT(EPOCH FROM (NOW() - created_at)) / 86400.0 as age_days,
                            tags,
                            CASE
                                WHEN metadata->'access_tracking'->>'last_accessed' IS NOT NULL THEN
                                    EXTRACT(EPOCH FROM (NOW() - (metadata->'access_tracking'->>'last_accessed')::TIMESTAMPTZ)) / 86400.0
                                ELSE
                                    999999
                            END as last_accessed_days
                        FROM nexus_memory.zep_episodic_memory
                    )
                    SELECT COUNT(*)
                    FROM decay_scores
                    WHERE decay_score < %s
                        AND age_days >= %s
                        AND importance_score <= 0.8
                        AND NOT (tags && %s)
                        AND last_accessed_days >= 7
                    LIMIT %s
                """, (request.min_score_threshold, request.min_age_days,
                      protected_tags, request.max_prune_count))

                would_prune_count = cur.fetchone()[0]

            conn.close()

            return PruningExecuteResponse(
                success=True,
                pruned_count=would_prune_count,
                dry_run=True,
                timestamp=datetime.now()
            )
        else:
            # ACTUAL PRUNING - NOT IMPLEMENTED YET
            # TODO: Implement archive table and soft delete logic
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="Actual pruning not yet implemented. Create archive table first."
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error executing pruning: {str(e)}"
        )

@app.get("/metrics", tags=["Monitoring"])
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

# ============================================
# FASE_8_UPGRADE: Hybrid Memory Endpoints
# ============================================

@app.post("/memory/facts", response_model=FactQueryResponse, tags=["Hybrid Memory"])
async def query_facts(request: FactQueryRequest):
    """
    Query extracted facts directly from episode metadata

    Fast fact retrieval without semantic search (< 5ms)
    """
    start_time = time.time()

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Build query
                query_parts = ["SELECT episode_id, content, metadata, created_at, tags FROM nexus_memory.zep_episodic_memory"]
                where_clauses = []
                params = []

                # Filter by tags if specified
                if request.filter_tags:
                    where_clauses.append("tags && %s")
                    params.append(request.filter_tags)

                # Filter by time range
                if request.after:
                    where_clauses.append("created_at > %s")
                    params.append(request.after)

                if request.before:
                    where_clauses.append("created_at < %s")
                    params.append(request.before)

                # Filter by episodes that have the requested fact
                where_clauses.append(f"metadata->'facts'->'{request.fact_type}' IS NOT NULL")

                # Combine WHERE clauses
                if where_clauses:
                    query_parts.append("WHERE " + " AND ".join(where_clauses))

                # Order by timestamp
                order = "DESC" if request.order == "desc" else "ASC"
                query_parts.append(f"ORDER BY created_at {order}")

                # Limit
                query_parts.append(f"LIMIT {request.limit}")

                query = " ".join(query_parts)

                cur.execute(query, params)
                rows = cur.fetchall()

                if not rows:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"No facts found for type: {request.fact_type}"
                    )

                # Get first result
                row = rows[0]
                episode_id = row[0]
                metadata = row[2]
                created_at = row[3]

                # Extract fact value
                facts = metadata.get("facts", {})
                fact_value = facts.get(request.fact_type)

                if fact_value is None:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Fact type '{request.fact_type}' not found"
                    )

                # Get confidence
                confidence = facts.get("extraction_confidence", 0.8)

                query_time_ms = (time.time() - start_time) * 1000

                return FactQueryResponse(
                    success=True,
                    fact_type=request.fact_type,
                    value=fact_value,
                    source_episode_id=str(episode_id),
                    confidence=confidence,
                    timestamp=created_at,
                    additional_context={"query_time_ms": query_time_ms}
                )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error querying facts: {str(e)}"
        )


@app.post("/memory/hybrid", response_model=HybridQueryResponse, tags=["Hybrid Memory"])
async def hybrid_query(request: HybridQueryRequest):
    """
    Intelligent hybrid query: tries fact extraction first, falls back to semantic search

    Best-of-both-worlds memory retrieval
    """
    start_time = time.time()

    # Detect if query is fact-seekable
    fact_patterns = {
        "version": ["version", "v2", "v1", "release"],
        "accuracy": ["accuracy", "correct", "score", "percentage"],
        "latency": ["latency", "speed", "ms", "milliseconds", "performance"],
        "episode_count": ["episodes", "how many", "total", "count"],
        "status": ["status", "state", "complete", "progress"],
    }

    query_lower = request.query.lower()
    detected_fact_type = None

    # Try to detect fact type from query
    for fact_type, keywords in fact_patterns.items():
        if any(keyword in query_lower for keyword in keywords):
            detected_fact_type = fact_type
            break

    # Strategy 1: Try fact query if prefer=fact or auto + detected
    if request.prefer == "fact" or (request.prefer == "auto" and detected_fact_type):
        if detected_fact_type:
            try:
                fact_request = FactQueryRequest(
                    fact_type=detected_fact_type,
                    filter_tags=request.tags,
                    limit=1
                )
                fact_result = await query_facts(fact_request)

                query_time_ms = (time.time() - start_time) * 1000

                return HybridQueryResponse(
                    success=True,
                    answer=fact_result.value,
                    source="fact",
                    episode_id=str(fact_result.source_episode_id),
                    confidence=fact_result.confidence,
                    query_time_ms=query_time_ms
                )
            except HTTPException:
                # Fact query failed, fall through to semantic search
                pass

    # Strategy 2: Semantic search (narrative)
    try:
        # Use existing /memory/search endpoint logic
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Generate embedding
                embedding = model.encode(request.query).tolist()

                # Build query
                query_parts = [
                    "SELECT episode_id, content, tags, created_at,",
                    "1 - (embedding <=> %s::vector) as similarity",
                    "FROM nexus_memory.zep_episodic_memory"
                ]
                params = [embedding]

                where_clauses = []

                if request.tags:
                    where_clauses.append("tags && %s")
                    params.append(request.tags)

                if where_clauses:
                    query_parts.append("WHERE " + " AND ".join(where_clauses))

                query_parts.append("ORDER BY similarity DESC")
                query_parts.append(f"LIMIT {request.limit}")

                query = " ".join(query_parts)

                cur.execute(query, params)
                rows = cur.fetchall()

                if not rows:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="No relevant episodes found"
                    )

                # Get best match
                row = rows[0]
                episode_id = row[0]
                content = row[1]
                similarity = row[4]

                query_time_ms = (time.time() - start_time) * 1000

                return HybridQueryResponse(
                    success=True,
                    answer=content,
                    source="narrative",
                    episode_id=str(episode_id),
                    confidence=float(similarity),
                    query_time_ms=query_time_ms
                )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in hybrid query: {str(e)}"
        )


# ============================================
# Main
# ============================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)

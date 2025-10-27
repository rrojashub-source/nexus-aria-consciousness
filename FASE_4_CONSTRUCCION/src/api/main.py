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

@app.get("/metrics", tags=["Monitoring"])
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

# ============================================
# Main
# ============================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)

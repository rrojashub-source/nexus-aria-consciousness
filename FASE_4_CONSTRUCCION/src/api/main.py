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
# Database Connection
# ============================================
DB_CONN_STRING = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

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
    database: str
    timestamp: datetime

# ============================================
# Lifespan Context Manager
# ============================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    app.state.db_conn = None
    yield
    # Shutdown
    if app.state.db_conn:
        app.state.db_conn.close()

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
    """Health check endpoint"""
    try:
        # Test database connection
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
            result = cur.fetchone()
        conn.close()

        db_status = "connected" if result else "disconnected"

        return HealthResponse(
            status="healthy",
            version="2.0.0",
            database=db_status,
            timestamp=datetime.now()
        )
    except Exception as e:
        return HealthResponse(
            status="unhealthy",
            version="2.0.0",
            database=f"error: {str(e)}",
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
        content = f"{request.action_type}: {request.action_details}"

        # Calculate importance_score (default 0.5, can be customized)
        importance_score = request.action_details.get("importance_score", 0.5)

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
    """Get recent episodic memories"""
    try:
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

        return {
            "success": True,
            "count": len(episodes),
            "episodes": episodes
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching episodes: {str(e)}"
        )

@app.get("/stats", tags=["Stats"])
async def get_stats():
    """Get database statistics"""
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
            episodes_with_embeddings = cur.fetchone()[0]

        conn.close()

        return {
            "success": True,
            "stats": {
                "total_episodes": total_episodes,
                "episodes_with_embeddings": episodes_with_embeddings,
                "embeddings_queue": queue_stats
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching stats: {str(e)}"
        )

# ============================================
# Main
# ============================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)

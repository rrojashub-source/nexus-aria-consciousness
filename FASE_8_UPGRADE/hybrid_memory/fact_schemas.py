"""
NEXUS Hybrid Memory - Fact Schemas
====================================
Pydantic models for structured fact storage in episode metadata

Created: October 27, 2025
Phase: FASE_8_UPGRADE Session 5
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class EpisodeFacts(BaseModel):
    """
    Structured facts extracted from episode content

    Stored in metadata.facts for fast retrieval
    """

    # ============================================================
    # VERSIONING
    # ============================================================

    nexus_version: Optional[str] = Field(
        None,
        description="NEXUS version (e.g., '2.0.0')",
        example="2.0.0"
    )

    api_version: Optional[str] = Field(
        None,
        description="API version if different from NEXUS version"
    )

    # ============================================================
    # METRICS
    # ============================================================

    accuracy_percent: Optional[float] = Field(
        None,
        description="Accuracy percentage (0-100)",
        ge=0.0,
        le=100.0,
        example=100.0
    )

    latency_ms: Optional[float] = Field(
        None,
        description="Latency in milliseconds",
        ge=0.0,
        example=10.63
    )

    episode_count: Optional[int] = Field(
        None,
        description="Number of episodes",
        ge=0,
        example=553
    )

    query_count: Optional[int] = Field(
        None,
        description="Number of queries"
    )

    test_count: Optional[int] = Field(
        None,
        description="Number of tests"
    )

    success_rate: Optional[float] = Field(
        None,
        description="Success rate (0-100)",
        ge=0.0,
        le=100.0
    )

    # ============================================================
    # STATUS & PROGRESS
    # ============================================================

    status: Optional[str] = Field(
        None,
        description="Status: COMPLETE, IN_PROGRESS, PENDING, FAILED",
        example="COMPLETE"
    )

    phase_number: Optional[int] = Field(
        None,
        description="Phase number (e.g., Phase 1, Phase 2)",
        ge=1,
        example=4
    )

    session_number: Optional[int] = Field(
        None,
        description="Session number",
        ge=1,
        example=2
    )

    completion_percent: Optional[float] = Field(
        None,
        description="Completion percentage (0-100)",
        ge=0.0,
        le=100.0
    )

    # ============================================================
    # FEATURES & IMPLEMENTATION
    # ============================================================

    feature_name: Optional[str] = Field(
        None,
        description="Feature or component name",
        example="Temporal Reasoning"
    )

    implementation_time_hours: Optional[float] = Field(
        None,
        description="Implementation time in hours",
        ge=0.0
    )

    lines_of_code: Optional[int] = Field(
        None,
        description="Lines of code added/modified",
        ge=0
    )

    files_created: Optional[int] = Field(
        None,
        description="Number of files created"
    )

    files_modified: Optional[int] = Field(
        None,
        description="Number of files modified"
    )

    # ============================================================
    # DECAY & MEMORY
    # ============================================================

    decay_score: Optional[float] = Field(
        None,
        description="Decay score (0.0-1.0)",
        ge=0.0,
        le=1.0
    )

    importance_override: Optional[float] = Field(
        None,
        description="Manual importance override (0.0-1.0)",
        ge=0.0,
        le=1.0
    )

    # ============================================================
    # BENCHMARKS
    # ============================================================

    benchmark_name: Optional[str] = Field(
        None,
        description="Benchmark name",
        example="DMR Benchmark"
    )

    benchmark_score: Optional[float] = Field(
        None,
        description="Benchmark score/accuracy"
    )

    baseline_score: Optional[float] = Field(
        None,
        description="Baseline or competitor score to compare against"
    )

    # ============================================================
    # ERRORS & BUGS
    # ============================================================

    bug_count: Optional[int] = Field(
        None,
        description="Number of bugs found/fixed",
        ge=0
    )

    error_count: Optional[int] = Field(
        None,
        description="Number of errors encountered",
        ge=0
    )

    # ============================================================
    # TEMPORAL
    # ============================================================

    duration_hours: Optional[float] = Field(
        None,
        description="Duration in hours",
        ge=0.0
    )

    start_date: Optional[str] = Field(
        None,
        description="Start date (ISO format)"
    )

    end_date: Optional[str] = Field(
        None,
        description="End date (ISO format)"
    )

    # ============================================================
    # GITHUB
    # ============================================================

    commit_hash: Optional[str] = Field(
        None,
        description="Git commit hash",
        example="abc123def456"
    )

    pull_request_number: Optional[int] = Field(
        None,
        description="GitHub Pull Request number"
    )

    # ============================================================
    # CUSTOM EXTENSIBLE FACTS
    # ============================================================

    custom: Optional[Dict[str, Any]] = Field(
        None,
        description="Custom facts not covered by schema"
    )

    # ============================================================
    # METADATA
    # ============================================================

    extraction_method: Optional[str] = Field(
        None,
        description="How facts were extracted: auto, manual, llm",
        example="auto"
    )

    extraction_confidence: Optional[float] = Field(
        None,
        description="Confidence in extraction (0.0-1.0)",
        ge=0.0,
        le=1.0
    )

    last_updated: Optional[datetime] = Field(
        None,
        description="Last time facts were updated"
    )


class FactQueryRequest(BaseModel):
    """Request model for /memory/facts endpoint"""

    fact_type: str = Field(
        ...,
        description="Type of fact to query (matches EpisodeFacts field name)",
        example="nexus_version"
    )

    filter_tags: Optional[List[str]] = Field(
        None,
        description="Filter by tags",
        example=["milestone", "fase_8_upgrade"]
    )

    after: Optional[datetime] = Field(
        None,
        description="Only consider episodes after this timestamp"
    )

    before: Optional[datetime] = Field(
        None,
        description="Only consider episodes before this timestamp"
    )

    limit: int = Field(
        1,
        description="Maximum number of results",
        ge=1,
        le=100
    )

    order: str = Field(
        "desc",
        description="Sort order: 'desc' (newest first) or 'asc' (oldest first)"
    )


class FactQueryResponse(BaseModel):
    """Response model for /memory/facts endpoint"""

    success: bool = True
    fact_type: str
    value: Any
    source_episode_id: Optional[str] = None
    confidence: float = Field(..., ge=0.0, le=1.0)
    timestamp: Optional[datetime] = None
    additional_context: Optional[Dict[str, Any]] = None


class HybridQueryRequest(BaseModel):
    """Request model for /memory/hybrid endpoint"""

    query: str = Field(
        ...,
        description="Natural language query",
        example="What is NEXUS version?"
    )

    prefer: str = Field(
        "auto",
        description="Preferred query mode: 'fact', 'narrative', or 'auto'"
    )

    tags: Optional[List[str]] = Field(
        None,
        description="Filter by tags"
    )

    limit: int = Field(
        5,
        description="Maximum number of results for narrative search",
        ge=1,
        le=100
    )


class HybridQueryResponse(BaseModel):
    """Response model for /memory/hybrid endpoint"""

    success: bool = True
    answer: Any
    source: str = Field(
        ...,
        description="'fact' or 'narrative'"
    )
    episode_id: Optional[str] = None
    confidence: float = Field(..., ge=0.0, le=1.0)
    query_time_ms: Optional[float] = None

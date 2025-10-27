"""
NEXUS Hybrid Memory - Fact Extraction Engine
==============================================
Automatic extraction of structured facts from episodic narrative content

Created: October 27, 2025
Phase: FASE_8_UPGRADE Session 5
"""

import re
from typing import Dict, Any, Optional, List
from datetime import datetime
from fact_schemas import EpisodeFacts


# ============================================================
# EXTRACTION PATTERNS
# ============================================================

# Regex patterns for common fact types
FACT_PATTERNS = {
    # Versioning
    "nexus_version": [
        r"(?:NEXUS|version|v)[\s:v]*(\d+\.\d+\.\d+)",
        r"V(\d+\.\d+\.\d+)",
        r"Cerebro\s+V(\d+\.\d+\.\d+)",
    ],

    # Metrics - Accuracy
    "accuracy_percent": [
        r"(\d+(?:\.\d+)?)\s*%\s*(?:accuracy|correct|success)",
        r"(?:accuracy|correct|success)[:\s]+(\d+(?:\.\d+)?)\s*%",
        r"Accuracy:\s+(\d+(?:\.\d+)?)\s*%",
    ],

    # Metrics - Latency
    "latency_ms": [
        r"(\d+(?:\.\d+)?)\s*ms\s*(?:latency|avg|average)",
        r"(?:latency|avg|average)[:\s]+(\d+(?:\.\d+)?)\s*ms",
        r"latency:\s+(\d+(?:\.\d+)?)\s*ms",
    ],

    # Counts
    "episode_count": [
        r"(\d+)\s+(?:total\s+)?episodes",
        r"(?:total\s+)?episodes:\s*(\d+)",
        r"episodes.*?(\d+)",
    ],

    "query_count": [
        r"(\d+)\s+queries",
        r"queries:\s*(\d+)",
    ],

    "test_count": [
        r"(\d+)\s+tests?",
        r"tests?:\s*(\d+)",
    ],

    # Status
    "status": [
        r"(?:Status|STATE):\s*(\w+)",
        r"(\w+)\s+COMPLETE",
        r"Implementation:\s*(\w+)",
    ],

    # Phase & Session
    "phase_number": [
        r"[Pp]hase\s+(\d+)",
        r"Phase\s+(\d+)",
        r"P(\d+):",
    ],

    "session_number": [
        r"[Ss]ession\s+(\d+)",
        r"Session\s+(\d+)",
        r"S(\d+):",
    ],

    # Features
    "feature_name": [
        r"Feature:\s*([^\n]+)",
        r"Implementing:\s*([^\n]+)",
        r"([A-Z][a-z]+\s+[A-Z][a-z]+)(?:\s+Feature|\s+Implementation)",
    ],

    # Implementation metrics
    "implementation_time_hours": [
        r"(\d+(?:\.\d+)?)\s+hours?",
        r"Duration:\s+(\d+(?:\.\d+)?)\s+hours?",
        r"Time:\s+(\d+(?:\.\d+)?)\s*h",
    ],

    "lines_of_code": [
        r"(\d+)\s+lines?(?:\s+of\s+code)?",
        r"LOC:\s*(\d+)",
        r"(\d+)\s+LOC",
    ],

    # Benchmarks
    "benchmark_name": [
        r"([A-Z]+)\s+Benchmark",
        r"Benchmark:\s*([^\n]+)",
    ],

    "benchmark_score": [
        r"Benchmark.*?(\d+(?:\.\d+)?)\s*%",
        r"Score:\s+(\d+(?:\.\d+)?)",
    ],

    "baseline_score": [
        r"(?:Baseline|SOTA|Target).*?(\d+(?:\.\d+)?)\s*%",
        r"vs\.?\s+(\d+(?:\.\d+)?)\s*%",
    ],

    # Errors & Bugs
    "bug_count": [
        r"(\d+)\s+bugs?",
        r"bugs?.*?(\d+)",
    ],

    "error_count": [
        r"(\d+)\s+errors?",
        r"errors?.*?(\d+)",
    ],

    # GitHub
    "commit_hash": [
        r"commit:\s*([a-f0-9]{7,40})",
        r"([a-f0-9]{40})",
    ],

    # Decay
    "decay_score": [
        r"decay[_\s]score:\s*(\d+\.\d+)",
        r"decay:\s*(\d+\.\d+)",
    ],
}


# ============================================================
# EXTRACTION FUNCTIONS
# ============================================================

def extract_with_pattern(content: str, patterns: List[str]) -> Optional[str]:
    """
    Try multiple patterns to extract a value

    Args:
        content: Episode content text
        patterns: List of regex patterns to try

    Returns:
        First matched value or None
    """
    for pattern in patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None


def extract_numeric(value: Optional[str]) -> Optional[float]:
    """
    Convert extracted string to numeric value

    Args:
        value: Extracted string value

    Returns:
        Float value or None
    """
    if value is None:
        return None

    try:
        # Remove commas and convert
        clean = value.replace(",", "")
        return float(clean)
    except (ValueError, AttributeError):
        return None


def extract_integer(value: Optional[str]) -> Optional[int]:
    """
    Convert extracted string to integer

    Args:
        value: Extracted string value

    Returns:
        Integer value or None
    """
    if value is None:
        return None

    try:
        # Remove commas and convert
        clean = value.replace(",", "")
        return int(float(clean))
    except (ValueError, AttributeError):
        return None


def normalize_status(status: Optional[str]) -> Optional[str]:
    """
    Normalize status values to standard forms

    Args:
        status: Raw status string

    Returns:
        Normalized status: COMPLETE, IN_PROGRESS, PENDING, FAILED, or None
    """
    if not status:
        return None

    status_upper = status.upper()

    # Complete variations
    if any(x in status_upper for x in ["COMPLETE", "DONE", "FINISHED", "SUCCESS"]):
        return "COMPLETE"

    # In progress variations
    if any(x in status_upper for x in ["PROGRESS", "ONGOING", "ACTIVE", "WORKING"]):
        return "IN_PROGRESS"

    # Pending variations
    if any(x in status_upper for x in ["PENDING", "PLANNED", "TODO", "UPCOMING"]):
        return "PENDING"

    # Failed variations
    if any(x in status_upper for x in ["FAILED", "ERROR", "BROKEN"]):
        return "FAILED"

    return status_upper


def extract_facts_from_content(content: str, tags: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Extract all facts from episode content

    Args:
        content: Episode narrative content
        tags: Episode tags (for context-aware extraction)

    Returns:
        Dictionary of extracted facts
    """
    facts = {}

    # Extract version
    version = extract_with_pattern(content, FACT_PATTERNS["nexus_version"])
    if version:
        facts["nexus_version"] = version

    # Extract metrics
    accuracy = extract_with_pattern(content, FACT_PATTERNS["accuracy_percent"])
    if accuracy:
        facts["accuracy_percent"] = extract_numeric(accuracy)

    latency = extract_with_pattern(content, FACT_PATTERNS["latency_ms"])
    if latency:
        facts["latency_ms"] = extract_numeric(latency)

    # Extract counts
    episode_count = extract_with_pattern(content, FACT_PATTERNS["episode_count"])
    if episode_count:
        facts["episode_count"] = extract_integer(episode_count)

    query_count = extract_with_pattern(content, FACT_PATTERNS["query_count"])
    if query_count:
        facts["query_count"] = extract_integer(query_count)

    test_count = extract_with_pattern(content, FACT_PATTERNS["test_count"])
    if test_count:
        facts["test_count"] = extract_integer(test_count)

    # Extract status
    status = extract_with_pattern(content, FACT_PATTERNS["status"])
    if status:
        facts["status"] = normalize_status(status)

    # Extract phase & session
    phase = extract_with_pattern(content, FACT_PATTERNS["phase_number"])
    if phase:
        facts["phase_number"] = extract_integer(phase)

    session = extract_with_pattern(content, FACT_PATTERNS["session_number"])
    if session:
        facts["session_number"] = extract_integer(session)

    # Extract feature name
    feature = extract_with_pattern(content, FACT_PATTERNS["feature_name"])
    if feature:
        # Clean up feature name (remove trailing punctuation, etc.)
        facts["feature_name"] = feature.rstrip(".:,;")

    # Extract implementation metrics
    impl_time = extract_with_pattern(content, FACT_PATTERNS["implementation_time_hours"])
    if impl_time:
        facts["implementation_time_hours"] = extract_numeric(impl_time)

    loc = extract_with_pattern(content, FACT_PATTERNS["lines_of_code"])
    if loc:
        facts["lines_of_code"] = extract_integer(loc)

    # Extract benchmark info
    benchmark_name = extract_with_pattern(content, FACT_PATTERNS["benchmark_name"])
    if benchmark_name:
        facts["benchmark_name"] = benchmark_name

    benchmark_score = extract_with_pattern(content, FACT_PATTERNS["benchmark_score"])
    if benchmark_score:
        facts["benchmark_score"] = extract_numeric(benchmark_score)

    baseline = extract_with_pattern(content, FACT_PATTERNS["baseline_score"])
    if baseline:
        facts["baseline_score"] = extract_numeric(baseline)

    # Extract bugs/errors
    bugs = extract_with_pattern(content, FACT_PATTERNS["bug_count"])
    if bugs:
        facts["bug_count"] = extract_integer(bugs)

    errors = extract_with_pattern(content, FACT_PATTERNS["error_count"])
    if errors:
        facts["error_count"] = extract_integer(errors)

    # Extract GitHub info
    commit = extract_with_pattern(content, FACT_PATTERNS["commit_hash"])
    if commit:
        facts["commit_hash"] = commit

    # Extract decay
    decay = extract_with_pattern(content, FACT_PATTERNS["decay_score"])
    if decay:
        facts["decay_score"] = extract_numeric(decay)

    # Add metadata
    if facts:
        facts["extraction_method"] = "auto"
        facts["extraction_confidence"] = calculate_extraction_confidence(facts, content)
        facts["last_updated"] = datetime.now().isoformat()

    return facts


def calculate_extraction_confidence(facts: Dict[str, Any], content: str) -> float:
    """
    Calculate confidence score for extracted facts

    Args:
        facts: Extracted facts dictionary
        content: Original content

    Returns:
        Confidence score 0.0-1.0
    """
    # Base confidence on number of facts extracted
    num_facts = len([k for k in facts.keys() if k not in ["extraction_method", "last_updated"]])

    if num_facts == 0:
        return 0.0

    # More facts = higher confidence (up to a point)
    fact_confidence = min(num_facts / 10.0, 0.8)

    # Boost confidence if content is structured (has headings, etc.)
    structure_boost = 0.0
    if any(marker in content for marker in ["###", "##", "**", "---", "===", "```"]):
        structure_boost = 0.1

    # Boost confidence if content has explicit fact markers
    explicit_boost = 0.0
    if any(marker in content.lower() for marker in [":", "=", "version", "accuracy", "status"]):
        explicit_boost = 0.1

    total_confidence = min(fact_confidence + structure_boost + explicit_boost, 1.0)

    return round(total_confidence, 2)


def create_episode_facts_model(facts: Dict[str, Any]) -> Optional[EpisodeFacts]:
    """
    Create validated EpisodeFacts Pydantic model from extracted facts

    Args:
        facts: Dictionary of extracted facts

    Returns:
        EpisodeFacts model or None if validation fails
    """
    try:
        return EpisodeFacts(**facts)
    except Exception as e:
        print(f"Fact validation error: {e}")
        return None


# ============================================================
# TESTING & VALIDATION
# ============================================================

def test_fact_extraction():
    """Test fact extraction on sample content"""

    sample_content = """
    FASE_8_UPGRADE Session 2 COMPLETE - Temporal Reasoning Feature 100% Functional

    Version: NEXUS V2.0.0
    Status: COMPLETE
    Session: 2
    Phase: 4

    Achievements:
    - DMR Accuracy: 100.0% (50/50 queries)
    - Temporal Reasoning Latency: 10.63ms avg
    - Total Episodes: 553
    - Implementation Time: 4.5 hours
    - Lines of Code: 539 lines

    Benchmark Results:
    - DMR Benchmark: 100% accuracy
    - Baseline (Zep SOTA): 94.8%
    - Bugs Found: 3
    - Tests: 10 passed

    Commit: abc123def456
    """

    facts = extract_facts_from_content(sample_content)

    print("Extracted Facts:")
    print("=" * 60)
    for key, value in facts.items():
        print(f"{key:30s}: {value}")
    print("=" * 60)

    # Create validated model
    model = create_episode_facts_model(facts)
    if model:
        print("\n✅ Facts validated successfully!")
        print(f"Extraction confidence: {facts.get('extraction_confidence', 0.0)}")
    else:
        print("\n❌ Fact validation failed")

    return facts, model


if __name__ == "__main__":
    # Run test
    test_fact_extraction()

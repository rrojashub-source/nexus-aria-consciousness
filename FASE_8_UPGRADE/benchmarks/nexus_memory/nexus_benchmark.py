#!/usr/bin/env python3
"""
NEXUS Memory Benchmark - Evaluation Engine
============================================
Created: October 27, 2025
Phase: FASE_8_UPGRADE Week 6-7

Purpose: Execute 50 questions against NEXUS API and evaluate results
         using automatic metrics (no external LLM dependencies)

Usage:
    python3 nexus_benchmark.py

Output:
    - Console report with category scores
    - results.json with detailed results
"""

import json
import requests
import sys
from datetime import datetime
from typing import Dict, List, Any
from collections import defaultdict

# ============================================================
# CONFIGURATION
# ============================================================

NEXUS_API = "http://localhost:8003"
QUESTIONS_FILE = "questions.json"
RESULTS_FILE = "results.json"

# Similarity threshold for abstention detection
ABSTENTION_THRESHOLD = 0.7

# ============================================================
# EVALUATION METRICS
# ============================================================

def exact_match(predicted: str, expected: str) -> float:
    """
    Exact Match metric (binary: 1.0 or 0.0)

    Args:
        predicted: Predicted answer string
        expected: Expected answer string

    Returns:
        1.0 if exact match (case-insensitive), 0.0 otherwise
    """
    pred_clean = predicted.strip().lower()
    exp_clean = expected.strip().lower()
    return 1.0 if pred_clean == exp_clean else 0.0


def f1_score(predicted: str, expected: str) -> float:
    """
    Token-level F1 Score

    Calculates precision and recall over word tokens

    Args:
        predicted: Predicted answer string
        expected: Expected answer string

    Returns:
        F1 score (0.0-1.0)
    """
    pred_tokens = set(predicted.lower().split())
    exp_tokens = set(expected.lower().split())

    if len(pred_tokens) == 0 and len(exp_tokens) == 0:
        return 1.0  # Both empty = perfect match

    if len(pred_tokens) == 0 or len(exp_tokens) == 0:
        return 0.0  # One empty, one not = no match

    common = pred_tokens & exp_tokens
    precision = len(common) / len(pred_tokens)
    recall = len(common) / len(exp_tokens)

    if precision + recall == 0:
        return 0.0

    return 2 * (precision * recall) / (precision + recall)


def temporal_accuracy(predicted: Dict, expected: str) -> float:
    """
    Temporal Accuracy metric

    Checks if temporal relationship is correct AND data is correct

    Args:
        predicted: Dictionary with temporal query results
        expected: Expected answer string

    Returns:
        1.0 if temporal relationship correct and F1 > 0.7, else 0.0
    """
    # Extract relevant content from predicted temporal results
    # This will depend on the structure returned by NEXUS API

    if 'results' not in predicted or len(predicted['results']) == 0:
        return 0.0

    # Get content from first result
    first_result = predicted['results'][0]
    predicted_content = first_result.get('content', '')

    # Use F1 to check data correctness
    data_f1 = f1_score(predicted_content, expected)

    return 1.0 if data_f1 > 0.7 else 0.0


def abstention_correct(predicted: Any, expected: str) -> float:
    """
    Abstention correctness metric

    Checks if system correctly abstained when it should have

    Args:
        predicted: Predicted result (can be dict or string)
        expected: Expected answer (should be "UNCERTAIN" for abstention cases)

    Returns:
        1.0 if abstention handling correct, 0.0 otherwise
    """
    should_abstain = expected.upper() == "UNCERTAIN"

    # Check if system abstained (empty results or low similarity)
    if isinstance(predicted, dict):
        results = predicted.get('results', [])

        if len(results) == 0:
            # No results found
            did_abstain = True
        else:
            # Check similarity score
            max_similarity = max([r.get('similarity_score', 0.0) for r in results])
            did_abstain = max_similarity < ABSTENTION_THRESHOLD
    else:
        # String response
        did_abstain = "UNCERTAIN" in str(predicted).upper() or len(str(predicted)) == 0

    # Correct if both should and did match
    return 1.0 if should_abstain == did_abstain else 0.0


# ============================================================
# QUERY EXECUTORS
# ============================================================

def execute_semantic_search(params: Dict) -> Dict:
    """Execute semantic search query"""
    try:
        response = requests.post(
            f"{NEXUS_API}/memory/search",
            json={
                "query": params.get("query", ""),
                "limit": params.get("limit", 5),
                "tags": params.get("tags", None)
            },
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e), "results": []}


def execute_temporal_before(params: Dict) -> Dict:
    """Execute temporal before query"""
    try:
        # First search for reference episode
        ref_search = requests.post(
            f"{NEXUS_API}/memory/search",
            json={"query": params.get("reference_content", ""), "limit": 1},
            timeout=10
        )
        ref_search.raise_for_status()
        ref_results = ref_search.json().get("results", [])

        if len(ref_results) == 0:
            return {"results": []}

        ref_timestamp = ref_results[0].get("created_at")

        # Now query before that timestamp
        response = requests.post(
            f"{NEXUS_API}/memory/temporal/before",
            json={
                "timestamp": ref_timestamp,
                "limit": params.get("limit", 5),
                "tags": params.get("tags", None)
            },
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e), "results": []}


def execute_temporal_after(params: Dict) -> Dict:
    """Execute temporal after query"""
    try:
        # First search for reference episode
        ref_search = requests.post(
            f"{NEXUS_API}/memory/search",
            json={"query": params.get("reference_content", ""), "limit": 1},
            timeout=10
        )
        ref_search.raise_for_status()
        ref_results = ref_search.json().get("results", [])

        if len(ref_results) == 0:
            return {"results": []}

        ref_timestamp = ref_results[0].get("created_at")

        # Now query after that timestamp
        response = requests.post(
            f"{NEXUS_API}/memory/temporal/after",
            json={
                "timestamp": ref_timestamp,
                "limit": params.get("limit", 5),
                "tags": params.get("tags", None)
            },
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e), "results": []}


def execute_temporal_range(params: Dict) -> Dict:
    """Execute temporal range query"""
    try:
        response = requests.post(
            f"{NEXUS_API}/memory/temporal/range",
            json={
                "start_time": params.get("start_time"),
                "end_time": params.get("end_time"),
                "limit": params.get("limit", 100),
                "tags": params.get("tags", None)
            },
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e), "results": []}


def execute_api_stats(params: Dict) -> Dict:
    """Execute API stats query"""
    try:
        response = requests.get(f"{NEXUS_API}/stats", timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def execute_decay_analysis(params: Dict) -> Dict:
    """Execute decay analysis query"""
    try:
        response = requests.post(
            f"{NEXUS_API}/memory/analysis/decay-scores",
            json={},
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def execute_fact_query(params: Dict) -> Dict:
    """Execute fact query using hybrid memory system"""
    try:
        response = requests.post(
            f"{NEXUS_API}/memory/facts",
            json={
                "fact_type": params.get("fact_type"),
                "filter_tags": params.get("filter_tags", None),
                "limit": params.get("limit", 1),
                "order": params.get("order", "desc")
            },
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e), "success": False}


# Query type to executor mapping
QUERY_EXECUTORS = {
    "semantic_search": execute_semantic_search,
    "temporal_before": execute_temporal_before,
    "temporal_after": execute_temporal_after,
    "temporal_range": execute_temporal_range,
    "api_stats": execute_api_stats,
    "decay_analysis": execute_decay_analysis,
    "fact_query": execute_fact_query,
}


# ============================================================
# ANSWER EXTRACTION
# ============================================================

def extract_answer(result: Dict, question: Dict) -> str:
    """
    Extract answer from API result based on question type

    Args:
        result: API response dictionary
        question: Question dictionary with metadata

    Returns:
        Extracted answer as string
    """
    query_type = question["query_type"]

    # Handle errors
    if "error" in result:
        return ""

    # API stats queries
    if query_type == "api_stats":
        stat_key = question["query_params"].get("stat_key", "total_episodes")
        stats = result.get("stats", {})
        return str(stats.get(stat_key, ""))

    # Decay analysis queries
    if query_type == "decay_analysis":
        # Extract specific info from decay distribution
        # This depends on what the question asks for
        return json.dumps(result)  # Return full result for now

    # Fact queries (hybrid memory system)
    if query_type == "fact_query":
        if result.get("success", False):
            # Extract the fact value
            value = result.get("value")
            if value is not None:
                return str(value)
        return ""

    # Temporal/semantic search queries
    results = result.get("results", [])

    if len(results) == 0:
        return ""

    # For most queries, return content of first result
    if len(results) > 0:
        return results[0].get("content", "")

    return ""


# ============================================================
# EVALUATION ENGINE
# ============================================================

def evaluate_question(question: Dict) -> Dict:
    """
    Evaluate a single question

    Args:
        question: Question dictionary

    Returns:
        Result dictionary with score and details
    """
    # Execute query
    query_type = question["query_type"]
    params = question["query_params"]

    executor = QUERY_EXECUTORS.get(query_type)
    if executor is None:
        return {
            "id": question["id"],
            "category": question["category"],
            "difficulty": question.get("difficulty", "medium"),
            "question": question["question"],
            "expected_answer": question["expected_answer"],
            "predicted_answer": "",
            "score": 0.0,
            "metric": question["evaluation_metric"],
            "query_type": query_type,
            "error": f"Unknown query type: {query_type}"
        }

    result = executor(params)

    # Extract answer
    predicted_answer = extract_answer(result, question)
    expected_answer = question["expected_answer"]

    # Evaluate based on metric
    metric = question["evaluation_metric"]

    if metric == "exact_match":
        score = exact_match(predicted_answer, expected_answer)
    elif metric == "f1_score":
        score = f1_score(predicted_answer, expected_answer)
    elif metric == "temporal_accuracy":
        score = temporal_accuracy(result, expected_answer)
    elif metric == "update_accuracy":
        score = exact_match(predicted_answer, expected_answer)  # Same as exact match
    elif metric == "abstention_correct":
        score = abstention_correct(result, expected_answer)
    else:
        score = 0.0

    return {
        "id": question["id"],
        "category": question["category"],
        "difficulty": question.get("difficulty", "medium"),
        "question": question["question"],
        "expected_answer": expected_answer,
        "predicted_answer": predicted_answer,
        "score": score,
        "metric": metric,
        "query_type": query_type
    }


def run_benchmark(questions_file: str) -> Dict:
    """
    Run full benchmark evaluation

    Args:
        questions_file: Path to questions JSON file

    Returns:
        Results dictionary with scores and analysis
    """
    # Load questions
    print(f"Loading questions from {questions_file}...")
    with open(questions_file, 'r') as f:
        data = json.load(f)

    questions = data["questions"]
    metadata = data["metadata"]

    print(f"Loaded {len(questions)} questions across {metadata['categories']} categories")
    print(f"Memory size at benchmark creation: {metadata['memory_size_at_creation']} episodes")
    print()

    # Check NEXUS API health
    print("Checking NEXUS API health...")
    try:
        response = requests.get(f"{NEXUS_API}/health", timeout=5)
        response.raise_for_status()
        health = response.json()
        print(f"✅ NEXUS API healthy (version: {health.get('version', 'unknown')})")
        print()
    except Exception as e:
        print(f"❌ NEXUS API not accessible: {e}")
        print("Please ensure NEXUS API is running on port 8003")
        sys.exit(1)

    # Run evaluation
    print("="*60)
    print("STARTING BENCHMARK EVALUATION")
    print("="*60)
    print()

    results = []
    category_scores = defaultdict(list)

    for i, question in enumerate(questions, 1):
        print(f"[{i}/{len(questions)}] Evaluating {question['id']}...")

        result = evaluate_question(question)
        results.append(result)

        category_scores[result["category"]].append(result["score"])

        # Print result
        status = "✅" if result["score"] > 0.7 else "❌"
        print(f"  {status} Score: {result['score']:.2f} ({result['metric']})")
        print(f"  Q: {question['question']}")
        print(f"  Expected: {result['expected_answer']}")
        print(f"  Predicted: {result['predicted_answer']}")
        print()

    # Calculate aggregate scores
    print("="*60)
    print("BENCHMARK RESULTS")
    print("="*60)
    print()

    # Overall score
    all_scores = [r["score"] for r in results]
    overall_score = sum(all_scores) / len(all_scores) if all_scores else 0.0

    print(f"Overall Accuracy: {overall_score:.1%} ({overall_score:.3f})")
    print()

    # Category breakdown
    print("Category Breakdown:")
    print("-" * 60)

    category_results = {}
    for category, scores in sorted(category_scores.items()):
        avg_score = sum(scores) / len(scores) if scores else 0.0
        category_results[category] = {
            "accuracy": avg_score,
            "total_questions": len(scores),
            "correct": sum(1 for s in scores if s > 0.7)
        }

        print(f"  {category:30s}: {avg_score:.1%} ({category_results[category]['correct']}/{len(scores)})")

    print()

    # Difficulty breakdown
    print("Difficulty Breakdown:")
    print("-" * 60)

    difficulty_scores = defaultdict(list)
    for result in results:
        difficulty_scores[result["difficulty"]].append(result["score"])

    for difficulty in ["easy", "medium", "hard"]:
        if difficulty in difficulty_scores:
            scores = difficulty_scores[difficulty]
            avg_score = sum(scores) / len(scores) if scores else 0.0
            correct = sum(1 for s in scores if s > 0.7)
            print(f"  {difficulty.capitalize():10s}: {avg_score:.1%} ({correct}/{len(scores)})")

    print()

    # Performance targets
    print("Performance vs Targets:")
    print("-" * 60)

    targets = {
        "information_extraction": 0.90,
        "multi_session_reasoning": 0.80,
        "temporal_reasoning": 0.85,
        "knowledge_updates": 0.75,
        "abstention": 0.70
    }

    for category, target in targets.items():
        if category in category_results:
            actual = category_results[category]["accuracy"]
            diff = actual - target
            status = "✅" if actual >= target else "❌"
            print(f"  {status} {category:30s}: {actual:.1%} (target: {target:.1%}, diff: {diff:+.1%})")

    overall_target = 0.80
    overall_diff = overall_score - overall_target
    status = "✅" if overall_score >= overall_target else "❌"
    print(f"  {status} {'Overall':30s}: {overall_score:.1%} (target: {overall_target:.1%}, diff: {overall_diff:+.1%})")

    print()
    print("="*60)

    # Build final results
    final_results = {
        "metadata": {
            **metadata,
            "evaluation_date": datetime.now().isoformat(),
            "nexus_api": NEXUS_API
        },
        "overall_score": overall_score,
        "category_scores": category_results,
        "difficulty_scores": {k: sum(v)/len(v) for k, v in difficulty_scores.items()},
        "targets": targets,
        "individual_results": results
    }

    return final_results


# ============================================================
# MAIN
# ============================================================

def main():
    """Main entry point"""
    print()
    print("=" * 60)
    print("NEXUS MEMORY BENCHMARK - Evaluation Engine v1.0")
    print("=" * 60)
    print()

    # Run benchmark
    results = run_benchmark(QUESTIONS_FILE)

    # Save results
    print(f"Saving results to {RESULTS_FILE}...")
    with open(RESULTS_FILE, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"✅ Results saved to {RESULTS_FILE}")
    print()

    # Success criteria check
    print("Success Criteria Check:")
    print("-" * 60)

    success = True

    # 1. Benchmark completes successfully
    print("✅ 1. Benchmark completed successfully (no crashes)")

    # 2. All 5 categories tested
    tested_categories = len(results["category_scores"])
    if tested_categories == 5:
        print(f"✅ 2. All 5 categories tested ({tested_categories}/5)")
    else:
        print(f"❌ 2. Not all categories tested ({tested_categories}/5)")
        success = False

    # 3. Overall accuracy >80%
    overall = results["overall_score"]
    if overall >= 0.80:
        print(f"✅ 3. Overall accuracy >80% ({overall:.1%})")
    else:
        print(f"❌ 3. Overall accuracy <80% ({overall:.1%})")
        success = False

    # 4. No category falls below 60%
    min_category = min(results["category_scores"].values(), key=lambda x: x["accuracy"])
    min_score = min_category["accuracy"]
    if min_score >= 0.60:
        print(f"✅ 4. No category below 60% (min: {min_score:.1%})")
    else:
        print(f"❌ 4. Category below 60% (min: {min_score:.1%})")
        success = False

    # 5. Results documented and reproducible
    print(f"✅ 5. Results documented in {RESULTS_FILE}")

    print()

    if success:
        print("🎉 ALL SUCCESS CRITERIA MET!")
    else:
        print("⚠️  Some success criteria not met - see details above")

    print()
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()

#!/usr/bin/bash
# Performance Baseline Testing - DÍA 11
# NEXUS VSCode - FASE 4 Post-Cutover Validation

API_URL="http://localhost:8003"
RESULTS_FILE="/tmp/performance_baseline_dia11.txt"

echo "=== PERFORMANCE BASELINE TEST - DÍA 11 ===" > $RESULTS_FILE
echo "Timestamp: $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> $RESULTS_FILE
echo "" >> $RESULTS_FILE

# TEST 1: Health Check Latency
echo "TEST 1: Health Check Latency (10 requests)" >> $RESULTS_FILE
for i in {1..10}; do
  time_ms=$(curl -s -w "%{time_total}\n" -o /dev/null $API_URL/health)
  echo "  Request $i: ${time_ms}s" >> $RESULTS_FILE
done
echo "" >> $RESULTS_FILE

# TEST 2: Stats Endpoint Latency
echo "TEST 2: Stats Endpoint Latency (10 requests)" >> $RESULTS_FILE
for i in {1..10}; do
  time_ms=$(curl -s -w "%{time_total}\n" -o /dev/null $API_URL/stats)
  echo "  Request $i: ${time_ms}s" >> $RESULTS_FILE
done
echo "" >> $RESULTS_FILE

# TEST 3: Recent Episodes Retrieval
echo "TEST 3: Recent Episodes Retrieval (limit=10, 5 requests)" >> $RESULTS_FILE
for i in {1..5}; do
  time_ms=$(curl -s -w "%{time_total}\n" -o /dev/null "$API_URL/memory/episodic/recent?limit=10")
  echo "  Request $i: ${time_ms}s" >> $RESULTS_FILE
done
echo "" >> $RESULTS_FILE

# TEST 4: Semantic Search Latency
echo "TEST 4: Semantic Search Latency (5 searches)" >> $RESULTS_FILE
queries=("fase 4 construccion" "migracion datos" "neural mesh" "embeddings automaticos" "postgresql arquitectura")
for i in {0..4}; do
  time_ms=$(curl -s -w "%{time_total}\n" -o /dev/null -X POST $API_URL/memory/search \
    -H "Content-Type: application/json" \
    -d "{\"query\": \"${queries[$i]}\", \"limit\": 5, \"min_similarity\": 0.3}")
  echo "  Search '$queries[$i]': ${time_ms}s" >> $RESULTS_FILE
done
echo "" >> $RESULTS_FILE

# TEST 5: Episode Creation Throughput (10 episodes)
echo "TEST 5: Episode Creation Throughput (10 episodes)" >> $RESULTS_FILE
start_time=$(date +%s.%N)
for i in {1..10}; do
  curl -s -X POST $API_URL/memory/action \
    -H "Content-Type: application/json" \
    -d "{
      \"action_type\": \"performance_test_episode\",
      \"action_details\": {\"test_number\": $i, \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"},
      \"context_state\": {\"test\": \"performance_baseline\"},
      \"tags\": [\"performance_test\", \"dia11\", \"baseline\"]
    }" > /dev/null
done
end_time=$(date +%s.%N)
duration=$(echo "$end_time - $start_time" | bc)
throughput=$(echo "scale=2; 10 / $duration" | bc)
echo "  Total time: ${duration}s" >> $RESULTS_FILE
echo "  Throughput: ${throughput} eps/sec" >> $RESULTS_FILE
echo "" >> $RESULTS_FILE

# TEST 6: Current System Stats
echo "TEST 6: System Stats Snapshot" >> $RESULTS_FILE
curl -s $API_URL/stats | python -m json.tool >> $RESULTS_FILE
echo "" >> $RESULTS_FILE

echo "=== BASELINE TEST COMPLETED ===" >> $RESULTS_FILE
echo "Results saved to: $RESULTS_FILE"

# Display results
cat $RESULTS_FILE

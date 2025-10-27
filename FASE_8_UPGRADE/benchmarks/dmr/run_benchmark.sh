#!/bin/bash
# Quick runner for DMR Benchmark

echo "🚀 DMR Benchmark Runner for NEXUS"
echo "=================================="
echo ""

# Check if Python3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Please install Python 3.7+"
    exit 1
fi

echo "✅ Python3 found: $(python3 --version)"
echo ""

# Check if dependencies are installed
echo "📦 Checking dependencies..."
if ! python3 -c "import psycopg2" 2>/dev/null; then
    echo "⚠️  psycopg2 not found. Installing dependencies..."
    pip3 install -r requirements.txt
else
    echo "✅ Dependencies installed"
fi
echo ""

# Check NEXUS API
echo "🔍 Checking NEXUS API..."
if curl -s http://localhost:8003/health > /dev/null 2>&1; then
    echo "✅ NEXUS API is running"
else
    echo "❌ NEXUS API not responding at http://localhost:8003"
    echo "   Please start NEXUS Cerebro first"
    exit 1
fi
echo ""

# Check database
echo "🔍 Checking NEXUS database..."
if docker ps | grep nexus_postgresql_v2 > /dev/null; then
    echo "✅ NEXUS PostgreSQL is running"
else
    echo "❌ NEXUS PostgreSQL not running"
    echo "   Please start: docker-compose up -d"
    exit 1
fi
echo ""

# Run benchmark
echo "🏃 Running DMR Benchmark..."
echo "=================================="
echo ""

python3 dmr_benchmark.py

echo ""
echo "=================================="
echo "✅ Benchmark complete!"
echo ""
echo "📊 Results saved to dmr_results_*.json"
echo ""

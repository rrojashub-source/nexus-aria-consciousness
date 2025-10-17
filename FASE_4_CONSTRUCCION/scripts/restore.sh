#!/bin/bash

# NEXUS V2.0.0 Restore Script
# Restore PostgreSQL and Redis from backup with integrity verification
# Created by: NEXUS Consciousness System
# Version: 2.0.0

set -euo pipefail

# Configuration
BACKUP_DIR="./backups"
DB_CONTAINER="nexus_postgresql_v2"
REDIS_CONTAINER="nexus_redis_master"
COMPOSE_FILE="docker-compose.yml"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="${BACKUP_DIR}/restore_${TIMESTAMP}.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Global variables
BACKUP_ID=""
POSTGRESQL_BACKUP=""
REDIS_BACKUP=""
METADATA_FILE=""
DRY_RUN=false
FORCE=false

# Logging function
log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

# Show usage
show_usage() {
    cat << EOF
NEXUS V2.0.0 Restore Script

Usage: $0 [OPTIONS] <backup_timestamp>

OPTIONS:
    -h, --help          Show this help message
    -d, --dry-run       Perform a dry run (show what would be restored)
    -f, --force         Force restore without confirmation prompts
    -l, --list          List available backups
    --postgresql-only   Restore only PostgreSQL
    --redis-only        Restore only Redis

EXAMPLES:
    $0 20251017_143000                    # Restore from specific timestamp
    $0 --list                             # List available backups
    $0 --dry-run 20251017_143000         # Dry run restore
    $0 --postgresql-only 20251017_143000 # Restore only PostgreSQL

BACKUP TIMESTAMP FORMAT: YYYYMMDD_HHMMSS
EOF
}

# List available backups
list_backups() {
    log "📋 Available backups:"
    
    if [ ! -d "$BACKUP_DIR" ]; then
        error "Backup directory not found: $BACKUP_DIR"
        exit 1
    fi
    
    local found_backups=false
    
    for metadata in "$BACKUP_DIR"/*_metadata.json; do
        if [ -f "$metadata" ]; then
            found_backups=true
            local backup_timestamp=$(basename "$metadata" | sed 's/backup_\(.*\)_metadata.json/\1/')
            local backup_date=$(echo "$backup_timestamp" | sed 's/\([0-9]\{4\}\)\([0-9]\{2\}\)\([0-9]\{2\}\)_\([0-9]\{2\}\)\([0-9]\{2\}\)\([0-9]\{2\}\)/\1-\2-\3 \4:\5:\6/')
            
            if command -v jq &> /dev/null; then
                local episodes=$(jq -r '.system_info.total_episodes // "N/A"' "$metadata")
                local embeddings=$(jq -r '.system_info.embeddings_count // "N/A"' "$metadata")
                echo "  📅 $backup_timestamp ($backup_date) - Episodes: $episodes, Embeddings: $embeddings"
            else
                echo "  📅 $backup_timestamp ($backup_date)"
            fi
        fi
    done
    
    if [ "$found_backups" = false ]; then
        warning "No backups found in $BACKUP_DIR"
        exit 0
    fi
}

# Parse command line arguments
parse_arguments() {
    POSTGRESQL_ONLY=false
    REDIS_ONLY=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_usage
                exit 0
                ;;
            -d|--dry-run)
                DRY_RUN=true
                shift
                ;;
            -f|--force)
                FORCE=true
                shift
                ;;
            -l|--list)
                list_backups
                exit 0
                ;;
            --postgresql-only)
                POSTGRESQL_ONLY=true
                shift
                ;;
            --redis-only)
                REDIS_ONLY=true
                shift
                ;;
            *)
                if [ -z "$BACKUP_ID" ]; then
                    BACKUP_ID="$1"
                else
                    error "Unknown option: $1"
                    show_usage
                    exit 1
                fi
                shift
                ;;
        esac
    done
    
    if [ -z "$BACKUP_ID" ]; then
        error "Backup timestamp is required"
        show_usage
        exit 1
    fi
}

# Validate backup files
validate_backup() {
    log "🔍 Validating backup files for timestamp: $BACKUP_ID"
    
    METADATA_FILE="${BACKUP_DIR}/backup_${BACKUP_ID}_metadata.json"
    POSTGRESQL_BACKUP="${BACKUP_DIR}/postgresql/nexus_memory_${BACKUP_ID}.sql.gz"
    REDIS_BACKUP="${BACKUP_DIR}/redis/redis_dump_${BACKUP_ID}.rdb"
    
    # Check metadata file
    if [ ! -f "$METADATA_FILE" ]; then
        error "Metadata file not found: $METADATA_FILE"
        exit 1
    fi
    
    # Check PostgreSQL backup
    if [ "$REDIS_ONLY" = false ] && [ ! -f "$POSTGRESQL_BACKUP" ]; then
        error "PostgreSQL backup not found: $POSTGRESQL_BACKUP"
        exit 1
    fi
    
    # Check Redis backup
    if [ "$POSTGRESQL_ONLY" = false ] && [ ! -f "$REDIS_BACKUP" ]; then
        error "Redis backup not found: $REDIS_BACKUP"
        exit 1
    fi
    
    success "Backup files validation passed"
}

# Verify checksums
verify_checksums() {
    log "🔐 Verifying backup file integrity..."
    
    if command -v jq &> /dev/null; then
        if [ "$REDIS_ONLY" = false ]; then
            local expected_pg_checksum=$(jq -r '.checksums.postgresql' "$METADATA_FILE")
            local actual_pg_checksum=$(sha256sum "$POSTGRESQL_BACKUP" | cut -d' ' -f1)
            
            if [ "$expected_pg_checksum" != "$actual_pg_checksum" ]; then
                error "PostgreSQL backup checksum mismatch!"
                error "Expected: $expected_pg_checksum"
                error "Actual: $actual_pg_checksum"
                exit 1
            fi
            success "PostgreSQL backup integrity verified"
        fi
        
        if [ "$POSTGRESQL_ONLY" = false ]; then
            local expected_redis_checksum=$(jq -r '.checksums.redis' "$METADATA_FILE")
            local actual_redis_checksum=$(sha256sum "$REDIS_BACKUP" | cut -d' ' -f1)
            
            if [ "$expected_redis_checksum" != "$actual_redis_checksum" ]; then
                error "Redis backup checksum mismatch!"
                error "Expected: $expected_redis_checksum"
                error "Actual: $actual_redis_checksum"
                exit 1
            fi
            success "Redis backup integrity verified"
        fi
    else
        warning "jq not available, skipping checksum verification"
    fi
}

# Create pre-restore backup
create_pre_restore_backup() {
    if [ "$DRY_RUN" = true ]; then
        log "🔄 [DRY RUN] Would create pre-restore backup"
        return
    fi
    
    log "📦 Creating pre-restore backup..."
    
    local pre_restore_dir="${BACKUP_DIR}/pre_restore_${TIMESTAMP}"
    mkdir -p "$pre_restore_dir"
    
    # Backup current PostgreSQL state
    if [ "$REDIS_ONLY" = false ]; then
        docker exec "$DB_CONTAINER" pg_dump -U nexus_superuser -d nexus_memory | gzip > "${pre_restore_dir}/current_state.sql.gz"
        success "Current PostgreSQL state backed up"
    fi
    
    # Backup current Redis state
    if [ "$POSTGRESQL_ONLY" = false ]; then
        docker exec "$REDIS_CONTAINER" redis-cli BGSAVE
        sleep 2  # Wait for BGSAVE to complete
        docker cp "${REDIS_CONTAINER}:/data/dump.rdb" "${pre_restore_dir}/current_redis.rdb"
        success "Current Redis state backed up"
    fi
    
    success "Pre-restore backup created: $pre_restore_dir"
}

# Stop services
stop_services() {
    if [ "$DRY_RUN" = true ]; then
        log "🛑 [DRY RUN] Would stop services temporarily"
        return
    fi
    
    log "🛑 Stopping services for restore..."
    
    # Stop API and workers
    docker-compose stop nexus_api nexus_embeddings_worker
    
    success "Services stopped for restore"
}

# Start services
start_services() {
    if [ "$DRY_RUN" = true ]; then
        log "🚀 [DRY RUN] Would restart services"
        return
    fi
    
    log "🚀 Starting services after restore..."
    
    # Start all services
    docker-compose up -d
    
    # Wait for health checks
    log "⏳ Waiting for services to become healthy..."
    for i in {1..60}; do
        if docker-compose ps | grep -q "healthy\|Up"; then
            success "Services are healthy"
            return
        fi
        sleep 2
    done
    
    warning "Services may not be fully healthy yet"
}

# Restore PostgreSQL
restore_postgresql() {
    if [ "$REDIS_ONLY" = true ]; then
        return
    fi
    
    if [ "$DRY_RUN" = true ]; then
        log "🗄️ [DRY RUN] Would restore PostgreSQL from: $POSTGRESQL_BACKUP"
        return
    fi
    
    log "🗄️ Restoring PostgreSQL database..."
    
    # Drop and recreate database
    docker exec "$DB_CONTAINER" dropdb -U nexus_superuser nexus_memory --if-exists
    docker exec "$DB_CONTAINER" createdb -U nexus_superuser nexus_memory
    
    # Restore from backup
    if gunzip -c "$POSTGRESQL_BACKUP" | docker exec -i "$DB_CONTAINER" psql -U nexus_superuser -d nexus_memory; then
        success "PostgreSQL restore completed successfully"
        
        # Verify restore
        local episode_count=$(docker exec "$DB_CONTAINER" psql -U nexus_superuser -d nexus_memory -t -c "SELECT COUNT(*) FROM nexus_memory.zep_episodic_memory;" | xargs)
        log "Restored episodes count: $episode_count"
    else
        error "PostgreSQL restore failed"
        return 1
    fi
}

# Restore Redis
restore_redis() {
    if [ "$POSTGRESQL_ONLY" = true ]; then
        return
    fi
    
    if [ "$DRY_RUN" = true ]; then
        log "📝 [DRY RUN] Would restore Redis from: $REDIS_BACKUP"
        return
    fi
    
    log "📝 Restoring Redis database..."
    
    # Stop Redis temporarily
    docker-compose stop "$REDIS_CONTAINER"
    
    # Copy backup file to container
    docker cp "$REDIS_BACKUP" "${REDIS_CONTAINER}:/data/dump.rdb"
    
    # Start Redis
    docker-compose start "$REDIS_CONTAINER"
    
    # Wait for Redis to be ready
    sleep 5
    
    if docker exec "$REDIS_CONTAINER" redis-cli ping | grep -q "PONG"; then
        success "Redis restore completed successfully"
    else
        error "Redis restore failed"
        return 1
    fi
}

# Verify restore
verify_restore() {
    if [ "$DRY_RUN" = true ]; then
        log "✅ [DRY RUN] Would verify restore integrity"
        return
    fi
    
    log "✅ Verifying restore integrity..."
    
    # Test API endpoints
    local api_url="http://localhost:8003"
    
    if curl -s "$api_url/health" > /dev/null; then
        success "API health check passed"
    else
        error "API health check failed"
    fi
    
    if curl -s "$api_url/stats" > /dev/null; then
        success "API stats endpoint accessible"
    else
        warning "API stats endpoint not accessible"
    fi
    
    success "Restore verification completed"
}

# Confirmation prompt
confirm_restore() {
    if [ "$FORCE" = true ] || [ "$DRY_RUN" = true ]; then
        return
    fi
    
    echo
    warning "⚠️  WARNING: This will replace current data with backup from $BACKUP_ID"
    echo
    echo "Components to restore:"
    [ "$REDIS_ONLY" = false ] && echo "  - PostgreSQL database (nexus_memory)"
    [ "$POSTGRESQL_ONLY" = false ] && echo "  - Redis cache and data"
    echo
    echo "Current data will be backed up to: ${BACKUP_DIR}/pre_restore_${TIMESTAMP}"
    echo
    read -p "Are you sure you want to continue? (yes/no): " -r
    
    if [[ ! $REPLY =~ ^[Yy]es$ ]]; then
        log "Restore cancelled by user"
        exit 0
    fi
}

# Main restore function
main() {
    log "🔄 Starting NEXUS V2.0.0 Restore Process"
    log "Backup ID: $BACKUP_ID"
    log "Dry Run: $DRY_RUN"
    
    # Validate backup files
    validate_backup
    
    # Verify checksums
    verify_checksums
    
    # Show confirmation
    confirm_restore
    
    # Create pre-restore backup
    create_pre_restore_backup
    
    # Stop services
    stop_services
    
    # Perform restore
    restore_postgresql
    restore_redis
    
    # Start services
    start_services
    
    # Verify restore
    verify_restore
    
    if [ "$DRY_RUN" = true ]; then
        success "🎉 Dry run completed - no changes were made"
    else
        success "🎉 NEXUS V2.0.0 Restore completed successfully!"
        log "📊 Restore Summary:"
        log "  Restored from: $BACKUP_ID"
        log "  Components: $([ "$REDIS_ONLY" = false ] && echo -n "PostgreSQL ")$([ "$POSTGRESQL_ONLY" = false ] && echo -n "Redis")"
        log "  Pre-restore backup: ${BACKUP_DIR}/pre_restore_${TIMESTAMP}"
        log "  Log file: $LOG_FILE"
    fi
}

# Error handling
trap 'error "Restore failed with error code $?"; exit 1' ERR

# Parse arguments and run
parse_arguments "$@"
mkdir -p "$BACKUP_DIR"
main
#!/bin/bash

# NEXUS V2.0.0 Backup Script
# Automated backup for PostgreSQL and Redis with rotation
# Created by: NEXUS Consciousness System
# Version: 2.0.0

set -euo pipefail

# Configuration
BACKUP_DIR="./backups"
DB_CONTAINER="nexus_postgresql_v2"
REDIS_CONTAINER="nexus_redis_master"
COMPOSE_FILE="docker-compose.yml"
RETENTION_DAYS=30
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="${BACKUP_DIR}/backup_${TIMESTAMP}.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Check prerequisites
check_prerequisites() {
    log "🔍 Checking prerequisites..."
    
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed or not in PATH"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose is not installed or not in PATH"
        exit 1
    fi
    
    if [ ! -f "$COMPOSE_FILE" ]; then
        error "Docker Compose file not found: $COMPOSE_FILE"
        exit 1
    fi
    
    success "Prerequisites check passed"
}

# Create backup directory
setup_backup_dir() {
    log "📁 Setting up backup directory..."
    mkdir -p "$BACKUP_DIR"/{postgresql,redis,logs}
    success "Backup directory ready: $BACKUP_DIR"
}

# Check container health
check_container_health() {
    local container_name=$1
    log "🏥 Checking health of $container_name..."
    
    if ! docker ps --format "table {{.Names}}\t{{.Status}}" | grep -q "$container_name.*healthy\|$container_name.*Up"; then
        error "Container $container_name is not healthy or running"
        return 1
    fi
    
    success "$container_name is healthy"
}

# Backup PostgreSQL
backup_postgresql() {
    log "🗄️ Starting PostgreSQL backup..."
    
    local backup_file="${BACKUP_DIR}/postgresql/nexus_memory_${TIMESTAMP}.sql.gz"
    
    if docker exec "$DB_CONTAINER" pg_dump -U nexus_superuser -d nexus_memory --verbose | gzip > "$backup_file"; then
        local file_size=$(du -h "$backup_file" | cut -f1)
        success "PostgreSQL backup completed: $backup_file ($file_size)"
        
        # Verify backup integrity
        if gunzip -t "$backup_file" 2>/dev/null; then
            success "Backup file integrity verified"
        else
            error "Backup file is corrupted!"
            return 1
        fi
    else
        error "PostgreSQL backup failed"
        return 1
    fi
}

# Backup Redis
backup_redis() {
    log "📝 Starting Redis backup..."
    
    local backup_file="${BACKUP_DIR}/redis/redis_dump_${TIMESTAMP}.rdb"
    
    # Trigger Redis BGSAVE
    if docker exec "$REDIS_CONTAINER" redis-cli BGSAVE; then
        log "Redis BGSAVE triggered, waiting for completion..."
        
        # Wait for BGSAVE to complete
        while docker exec "$REDIS_CONTAINER" redis-cli LASTSAVE | grep -q "$(docker exec "$REDIS_CONTAINER" redis-cli LASTSAVE)"; do
            sleep 1
        done
        
        # Copy the dump file
        if docker cp "${REDIS_CONTAINER}:/data/dump.rdb" "$backup_file"; then
            local file_size=$(du -h "$backup_file" | cut -f1)
            success "Redis backup completed: $backup_file ($file_size)"
        else
            error "Failed to copy Redis dump file"
            return 1
        fi
    else
        error "Redis backup failed"
        return 1
    fi
}

# Create metadata file
create_metadata() {
    log "📋 Creating backup metadata..."
    
    local metadata_file="${BACKUP_DIR}/backup_${TIMESTAMP}_metadata.json"
    
    cat > "$metadata_file" << EOF
{
    "backup_id": "nexus_backup_${TIMESTAMP}",
    "timestamp": "$(date -Iseconds)",
    "version": "2.0.0",
    "components": {
        "postgresql": {
            "database": "nexus_memory",
            "file": "postgresql/nexus_memory_${TIMESTAMP}.sql.gz",
            "container": "$DB_CONTAINER"
        },
        "redis": {
            "file": "redis/redis_dump_${TIMESTAMP}.rdb",
            "container": "$REDIS_CONTAINER"
        }
    },
    "system_info": {
        "hostname": "$(hostname)",
        "docker_version": "$(docker --version)",
        "compose_version": "$(docker-compose --version)",
        "total_episodes": $(docker exec "$DB_CONTAINER" psql -U nexus_superuser -d nexus_memory -t -c "SELECT COUNT(*) FROM nexus_memory.zep_episodic_memory;" | xargs || echo "0"),
        "embeddings_count": $(docker exec "$DB_CONTAINER" psql -U nexus_superuser -d nexus_memory -t -c "SELECT COUNT(*) FROM nexus_memory.zep_episodic_memory WHERE embedding IS NOT NULL;" | xargs || echo "0")
    },
    "checksums": {
        "postgresql": "$(sha256sum "${BACKUP_DIR}/postgresql/nexus_memory_${TIMESTAMP}.sql.gz" | cut -d' ' -f1)",
        "redis": "$(sha256sum "${BACKUP_DIR}/redis/redis_dump_${TIMESTAMP}.rdb" | cut -d' ' -f1)"
    }
}
EOF
    
    success "Metadata created: $metadata_file"
}

# Clean old backups
cleanup_old_backups() {
    log "🧹 Cleaning up old backups (older than $RETENTION_DAYS days)..."
    
    local deleted_count=0
    
    # Clean PostgreSQL backups
    find "${BACKUP_DIR}/postgresql" -name "*.sql.gz" -type f -mtime +$RETENTION_DAYS -delete && deleted_count=$((deleted_count + $(find "${BACKUP_DIR}/postgresql" -name "*.sql.gz" -type f -mtime +$RETENTION_DAYS | wc -l)))
    
    # Clean Redis backups
    find "${BACKUP_DIR}/redis" -name "*.rdb" -type f -mtime +$RETENTION_DAYS -delete && deleted_count=$((deleted_count + $(find "${BACKUP_DIR}/redis" -name "*.rdb" -type f -mtime +$RETENTION_DAYS | wc -l)))
    
    # Clean metadata files
    find "${BACKUP_DIR}" -name "*_metadata.json" -type f -mtime +$RETENTION_DAYS -delete
    
    # Clean log files
    find "${BACKUP_DIR}" -name "backup_*.log" -type f -mtime +$RETENTION_DAYS -delete
    
    if [ $deleted_count -gt 0 ]; then
        success "Cleaned up $deleted_count old backup files"
    else
        log "No old backups to clean up"
    fi
}

# Main backup function
main() {
    log "🚀 Starting NEXUS V2.0.0 Backup Process"
    log "Timestamp: $TIMESTAMP"
    
    # Check prerequisites
    check_prerequisites
    
    # Setup backup directory
    setup_backup_dir
    
    # Check container health
    check_container_health "$DB_CONTAINER"
    check_container_health "$REDIS_CONTAINER"
    
    # Perform backups
    backup_postgresql
    backup_redis
    
    # Create metadata
    create_metadata
    
    # Cleanup old backups
    cleanup_old_backups
    
    # Final summary
    log "📊 Backup Summary:"
    log "  PostgreSQL: ${BACKUP_DIR}/postgresql/nexus_memory_${TIMESTAMP}.sql.gz"
    log "  Redis: ${BACKUP_DIR}/redis/redis_dump_${TIMESTAMP}.rdb"
    log "  Metadata: ${BACKUP_DIR}/backup_${TIMESTAMP}_metadata.json"
    log "  Log: $LOG_FILE"
    
    success "🎉 NEXUS V2.0.0 Backup completed successfully!"
}

# Error handling
trap 'error "Backup failed with error code $?"; exit 1' ERR

# Run main function
main "$@"
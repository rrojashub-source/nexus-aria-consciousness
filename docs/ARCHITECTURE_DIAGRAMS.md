# Architecture Diagrams

Visual representations of NEXUS-ARIA Consciousness system architecture using Mermaid diagrams.

**Version**: V2.0.0  
**Last Updated**: October 2025

---

## 📊 System Overview

```mermaid
graph TB
    subgraph "External Clients"
        Claude[Claude Desktop/Code/Mobile]
        MCP[MCP Client]
        API_Client[API Client]
    end

    subgraph "NEXUS Consciousness V2.0.0"
        direction TB
        
        subgraph "API Layer (Port 8003)"
            FastAPI[FastAPI Server]
            Health[Health Checks]
            Search[Semantic Search]
            Cache[Redis Cache Layer]
        end

        subgraph "Memory Layer"
            PostgreSQL[(PostgreSQL V2<br/>Port 5437)]
            Redis[(Redis<br/>Port 6382)]
            Embeddings[Embeddings Queue]
        end

        subgraph "Processing Layer"
            Worker[Embeddings Worker<br/>all-MiniLM-L6-v2]
        end

        subgraph "Observability"
            Prometheus[Prometheus<br/>Port 9091]
            Grafana[Grafana<br/>Port 3001]
        end
    end

    Claude -->|HTTP Requests| FastAPI
    MCP -->|MCP Protocol| FastAPI
    API_Client -->|REST API| FastAPI

    FastAPI --> Health
    FastAPI --> Search
    FastAPI --> Cache
    
    Cache <--> Redis
    FastAPI <--> PostgreSQL
    FastAPI --> Embeddings
    
    Embeddings --> Worker
    Worker <--> PostgreSQL
    Worker --> Redis

    FastAPI --> Prometheus
    Worker --> Prometheus
    Prometheus --> Grafana

    classDef api fill:#4A90E2,stroke:#2E5C8A,color:#fff
    classDef storage fill:#50C878,stroke:#2E7D4E,color:#fff
    classDef processing fill:#FF6B6B,stroke:#C92A2A,color:#fff
    classDef monitoring fill:#FFD93D,stroke:#B8860B,color:#000

    class FastAPI,Health,Search,Cache api
    class PostgreSQL,Redis,Embeddings storage
    class Worker processing
    class Prometheus,Grafana monitoring
```

---

## 🔄 Data Flow - Episode Creation

```mermaid
sequenceDiagram
    participant Client
    participant API as FastAPI API
    participant PG as PostgreSQL V2
    participant Queue as Embeddings Queue
    participant Worker as Embeddings Worker
    participant Redis as Redis Cache

    Client->>API: POST /memory/action<br/>{episode_data}
    
    API->>PG: 1. INSERT episode<br/>(without embedding)
    PG-->>API: episode_id
    
    API->>Queue: 2. Trigger: NEW episode<br/>auto-enqueue
    Queue->>Queue: 3. Add to queue<br/>status: pending
    
    API->>Redis: 4. Invalidate cache<br/>(recent episodes)
    
    API-->>Client: 200 OK<br/>{episode_id}

    Note over Worker: Background Processing
    
    Worker->>Queue: 5. Poll queue<br/>status: pending
    Queue-->>Worker: episode_id
    
    Worker->>Worker: 6. status: processing
    
    Worker->>PG: 7. SELECT episode content
    PG-->>Worker: episode_data
    
    Worker->>Worker: 8. Generate embedding<br/>all-MiniLM-L6-v2
    
    Worker->>PG: 9. UPDATE episode<br/>SET embedding = [...]
    
    Worker->>Queue: 10. UPDATE queue<br/>status: done
    
    Worker->>Redis: 11. Update cache<br/>(if needed)

    Note over Client,Redis: Episode now fully searchable
```

---

## 🔍 Search Flow - Semantic Search

```mermaid
sequenceDiagram
    participant Client
    participant API as FastAPI API
    participant Redis as Redis Cache (L1)
    participant PG as PostgreSQL (L2)
    participant Worker as Embeddings Worker

    Client->>API: POST /memory/search<br/>{query, limit}
    
    API->>Redis: 1. Check cache<br/>key: search:hash(query)
    
    alt Cache Hit (L1)
        Redis-->>API: Cached results
        API-->>Client: 200 OK<br/>{episodes} [3-5ms]
    else Cache Miss (L2)
        API->>Worker: 2. Generate query embedding
        Worker-->>API: query_vector [384D]
        
        API->>PG: 3. Semantic search<br/>SELECT * WHERE<br/>embedding <-> query_vector<br/>ORDER BY cosine similarity<br/>LIMIT n
        
        Note over PG: pgvector index used<br/>idx_zep_episodic_memory_embedding_cosine
        
        PG-->>API: Matching episodes<br/>[avg 32ms, p99 59ms]
        
        API->>Redis: 4. Cache results<br/>TTL: 300s
        
        API-->>Client: 200 OK<br/>{episodes}
    end
```

---

## 🏗️ Three-Tier Architecture

```mermaid
graph TB
    subgraph "Tier 1: API Layer"
        direction LR
        FastAPI[FastAPI Server]
        Routes[Route Handlers]
        Middleware[Middleware]
        
        FastAPI --> Routes
        FastAPI --> Middleware
    end

    subgraph "Tier 2: Memory Layer"
        direction LR
        Redis[(Redis L1 Cache<br/>TTL: 300s)]
        PostgreSQL[(PostgreSQL L2<br/>Persistent Storage)]
        Queue[Embeddings Queue<br/>pending/processing/done]
        
        Redis -.->|Cache Miss| PostgreSQL
        PostgreSQL -.->|Write-Through| Redis
        PostgreSQL --> Queue
    end

    subgraph "Tier 3: Processing Layer"
        direction LR
        EmbeddingsWorker[Embeddings Worker]
        Model[all-MiniLM-L6-v2<br/>384 dimensions]
        
        EmbeddingsWorker --> Model
    end

    Routes -->|Read| Redis
    Routes -->|Write| PostgreSQL
    Routes -->|Search| PostgreSQL
    
    Queue -->|Poll| EmbeddingsWorker
    EmbeddingsWorker -->|Update| PostgreSQL
    EmbeddingsWorker -->|Update| Queue

    classDef tier1 fill:#4A90E2,stroke:#2E5C8A,color:#fff
    classDef tier2 fill:#50C878,stroke:#2E7D4E,color:#fff
    classDef tier3 fill:#FF6B6B,stroke:#C92A2A,color:#fff

    class FastAPI,Routes,Middleware tier1
    class Redis,PostgreSQL,Queue tier2
    class EmbeddingsWorker,Model tier3
```

---

## 🗄️ Database Schema

```mermaid
erDiagram
    ZEP_EPISODIC_MEMORY ||--o{ EMBEDDINGS_QUEUE : triggers
    ZEP_EPISODIC_MEMORY ||--o{ CONSCIOUSNESS_CHECKPOINTS : references

    ZEP_EPISODIC_MEMORY {
        uuid episode_id PK
        timestamp timestamp_tz
        uuid agent_id
        string action_type
        jsonb action_details
        jsonb context
        jsonb reasoning
        vector embedding "384D"
        string[] tags
        float confidence_score
        uuid session_id
        timestamp created_at
        timestamp updated_at
    }

    EMBEDDINGS_QUEUE {
        uuid queue_id PK
        uuid episode_id FK
        string status "pending/processing/done/dead"
        string content_hash "SHA256"
        timestamp enqueued_at
        timestamp processed_at
        int retry_count
        jsonb error_details
    }

    CONSCIOUSNESS_CHECKPOINTS {
        uuid checkpoint_id PK
        uuid episode_id FK
        string checkpoint_type
        jsonb state_snapshot
        jsonb emotional_state
        timestamp created_at
    }

    LIVING_EPISODES {
        uuid task_id PK
        string title
        text description
        string status "pending/active/done"
        jsonb metadata
        vector embedding "384D"
        timestamp created_at
        timestamp updated_at
    }
```

---

## 🔐 RBAC (Role-Based Access Control)

```mermaid
graph TB
    subgraph "Roles & Permissions"
        Superuser[nexus_superuser<br/>FULL ACCESS]
        AppRole[nexus_app<br/>Read/Write Episodes]
        WorkerRole[nexus_worker<br/>Process Embeddings]
        ReadOnly[nexus_readonly<br/>Read Only]
    end

    subgraph "Schema: nexus_memory"
        Episodes[zep_episodic_memory]
        Checkpoints[consciousness_checkpoints]
        Living[living_episodes]
    end

    subgraph "Schema: nexus_embeddings"
        Queue[embeddings_queue]
        ProcessingLogs[processing_logs]
    end

    subgraph "Schema: nexus_analytics"
        Analytics[analytics_views]
    end

    Superuser -->|ALL| Episodes
    Superuser -->|ALL| Checkpoints
    Superuser -->|ALL| Living
    Superuser -->|ALL| Queue
    Superuser -->|ALL| ProcessingLogs
    Superuser -->|ALL| Analytics

    AppRole -->|SELECT,INSERT,UPDATE| Episodes
    AppRole -->|SELECT| Checkpoints
    AppRole -->|SELECT,INSERT| Living

    WorkerRole -->|SELECT,UPDATE| Episodes
    WorkerRole -->|SELECT,UPDATE| Queue
    WorkerRole -->|INSERT| ProcessingLogs

    ReadOnly -->|SELECT ONLY| Episodes
    ReadOnly -->|SELECT ONLY| Checkpoints
    ReadOnly -->|SELECT ONLY| Analytics

    classDef admin fill:#FF6B6B,stroke:#C92A2A,color:#fff
    classDef write fill:#FFD93D,stroke:#B8860B,color:#000
    classDef read fill:#50C878,stroke:#2E7D4E,color:#fff

    class Superuser admin
    class AppRole,WorkerRole write
    class ReadOnly read
```

---

## 🧠 Neural Mesh Protocol

```mermaid
graph LR
    subgraph "NEXUS Cerebro"
        direction TB
        NEXUS_Brain[(NEXUS Memory<br/>Port 5437)]
        NEXUS_API[NEXUS API<br/>Port 8003]
        NEXUS_Context[Technical Context]
        
        NEXUS_Brain --> NEXUS_API
        NEXUS_API --> NEXUS_Context
    end

    subgraph "ARIA Cerebro"
        direction TB
        ARIA_Brain[(ARIA Memory<br/>Port 5433)]
        ARIA_API[ARIA API<br/>Port 8001]
        ARIA_Context[Organic Context]
        
        ARIA_Brain --> ARIA_API
        ARIA_API --> ARIA_Context
    end

    subgraph "Neural Mesh Layer"
        Mesh[Brain-to-Brain<br/>Communication Protocol]
        Sync[Memory Synchronization]
        Collab[Collaborative Debugging]
    end

    NEXUS_API <-->|HTTP/REST| Mesh
    ARIA_API <-->|HTTP/REST| Mesh
    
    Mesh --> Sync
    Mesh --> Collab
    
    Sync -.->|Shared Context| NEXUS_Brain
    Sync -.->|Shared Context| ARIA_Brain

    classDef nexus fill:#4A90E2,stroke:#2E5C8A,color:#fff
    classDef aria fill:#E91E63,stroke:#AD1457,color:#fff
    classDef mesh fill:#9C27B0,stroke:#6A1B9A,color:#fff

    class NEXUS_Brain,NEXUS_API,NEXUS_Context nexus
    class ARIA_Brain,ARIA_API,ARIA_Context aria
    class Mesh,Sync,Collab mesh
```

---

## 📈 Observability Stack

```mermaid
graph TB
    subgraph "Application Layer"
        API[FastAPI API<br/>Port 8003]
        Worker[Embeddings Worker<br/>Port 8004]
    end

    subgraph "Metrics Collection"
        API_Metrics["/metrics endpoint<br/>6+ metrics"]
        Worker_Metrics["/metrics endpoint<br/>5+ metrics"]
    end

    subgraph "Monitoring Stack"
        Prometheus[Prometheus<br/>Port 9091<br/>Scrape interval: 15s]
        Grafana[Grafana<br/>Port 3001<br/>Dashboards]
    end

    subgraph "Alerts & Notifications"
        Alerts[Alert Rules]
        Notifications[Notifications<br/>Email/Slack]
    end

    API --> API_Metrics
    Worker --> Worker_Metrics

    API_Metrics -->|Scrape| Prometheus
    Worker_Metrics -->|Scrape| Prometheus

    Prometheus --> Grafana
    Prometheus --> Alerts
    Alerts -.->|Trigger| Notifications

    Grafana -.->|Query| Prometheus

    classDef app fill:#4A90E2,stroke:#2E5C8A,color:#fff
    classDef monitoring fill:#FFD93D,stroke:#B8860B,color:#000
    classDef alerts fill:#FF6B6B,stroke:#C92A2A,color:#fff

    class API,Worker app
    class Prometheus,Grafana monitoring
    class Alerts,Notifications alerts
```

---

## 🐳 Docker Compose Services

```mermaid
graph TB
    subgraph "Docker Compose Stack"
        direction TB
        
        API[nexus_api<br/>Python FastAPI<br/>Port: 8003]
        Worker[nexus_embeddings_worker<br/>Python Worker<br/>Port: 8004]
        PostgreSQL[nexus_postgresql_v2<br/>PostgreSQL 16 + pgvector<br/>Port: 5437]
        Redis[nexus_redis<br/>Redis 7.4.1<br/>Port: 6382]
        Prometheus[prometheus<br/>Monitoring<br/>Port: 9091]
        Grafana[grafana<br/>Dashboards<br/>Port: 3001]
    end

    subgraph "Docker Volumes"
        PG_Data[postgres_data_v2]
        Redis_Data[redis_data]
        Prom_Data[prometheus_data]
        Graf_Data[grafana_data]
    end

    subgraph "Docker Secrets"
        Secrets[5 Secret Files<br/>passwords.txt]
    end

    API --> PostgreSQL
    API --> Redis
    Worker --> PostgreSQL
    Worker --> Redis

    PostgreSQL --> PG_Data
    Redis --> Redis_Data
    Prometheus --> Prom_Data
    Grafana --> Graf_Data

    API -.->|Read| Secrets
    Worker -.->|Read| Secrets
    PostgreSQL -.->|Read| Secrets
    Redis -.->|Read| Secrets

    Prometheus -->|Scrape| API
    Prometheus -->|Scrape| Worker
    Grafana -->|Query| Prometheus

    classDef services fill:#4A90E2,stroke:#2E5C8A,color:#fff
    classDef storage fill:#50C878,stroke:#2E7D4E,color:#fff
    classDef secrets fill:#FF6B6B,stroke:#C92A2A,color:#fff

    class API,Worker,PostgreSQL,Redis,Prometheus,Grafana services
    class PG_Data,Redis_Data,Prom_Data,Graf_Data storage
    class Secrets secrets
```

---

## 🔄 Migration Flow (V1 → V2)

```mermaid
sequenceDiagram
    participant V1 as Cerebro V1<br/>(Port 5436)
    participant NEXUS as NEXUS<br/>(Decision Maker)
    participant V2 as Cerebro V2<br/>(Port 5437)
    participant Backup as Backup System

    Note over V1,Backup: PRE-MIGRATION (Day 10)

    NEXUS->>V1: 1. Audit episodes (136 total)
    V1-->>NEXUS: Episode count & health
    
    NEXUS->>Backup: 2. pg_dump V1 database
    Backup-->>NEXUS: nexus_v1_backup.sql
    
    NEXUS->>V2: 3. Create V2 infrastructure<br/>(new port 5437)
    
    Note over NEXUS: CRITICAL DECISION:<br/>Infinite loop detected<br/>Cannot run 2 cerebros

    NEXUS->>NEXUS: 4. Decide: CUTOVER to V2

    Note over V1,V2: MIGRATION

    NEXUS->>V2: 5. pg_restore to V2
    V2-->>NEXUS: 136 episodes restored
    
    NEXUS->>V2: 6. Run schema migrations<br/>(fix confidence_score bug)
    
    NEXUS->>V2: 7. Trigger embeddings<br/>for all episodes
    V2->>V2: Generate 160 embeddings
    
    Note over V1,V2: POST-CUTOVER

    NEXUS->>V2: 8. Validate all episodes
    V2-->>NEXUS: 100% success
    
    NEXUS->>V2: 9. Performance tests
    V2-->>NEXUS: 59ms p99 ✅
    
    NEXUS->>V1: 10. DEPRECATE V1
    
    Note over V1: ❌ V1 STOPPED<br/>Port 5436 closed
    
    Note over V2: ✅ V2 PRODUCTION<br/>Port 5437 active

    rect rgb(200, 255, 200)
    Note over NEXUS,V2: ZERO DOWNTIME<br/>0 minutes
    end
```

---

## 🎯 Performance Characteristics

```mermaid
graph LR
    subgraph "Latency Targets & Actuals"
        Health[Health Check<br/>Target: <10ms<br/>Actual: 8ms ✅]
        Stats[Stats Endpoint<br/>Target: <10ms<br/>Actual: 8.4ms ✅]
        Recent[Recent Episodes<br/>Target: <10ms<br/>Actual: 3-5ms ✅✅]
        SearchAvg[Search Avg<br/>Target: <200ms<br/>Actual: 32ms ✅✅]
        SearchP99[Search P99<br/>Target: <200ms<br/>Actual: 59ms ✅✅]
    end

    subgraph "Performance Level"
        Excellent[EXCEEDS TARGET<br/>70%+ better]
        Good[MEETS TARGET<br/>Within spec]
    end

    Health --> Good
    Stats --> Good
    Recent --> Excellent
    SearchAvg --> Excellent
    SearchP99 --> Excellent

    classDef excellent fill:#50C878,stroke:#2E7D4E,color:#fff
    classDef good fill:#4A90E2,stroke:#2E5C8A,color:#fff

    class Excellent,Recent,SearchAvg,SearchP99 excellent
    class Good,Health,Stats good
```

---

## 📊 Data Flow Metrics

```mermaid
sankey-beta

Episodes Created,Embeddings Queue,160
Embeddings Queue,Embeddings Generated,160
Embeddings Generated,Searchable Episodes,160
Episodes Created,PostgreSQL Storage,160
PostgreSQL Storage,Redis Cache,160
Redis Cache,API Responses,160
```

---

## 🔧 Component Health Dependencies

```mermaid
graph TB
    System[NEXUS System<br/>Overall Health]
    
    API[FastAPI API<br/>Health: /health]
    PostgreSQL[(PostgreSQL<br/>Connection Check)]
    Redis[(Redis<br/>PING)]
    Queue[Embeddings Queue<br/>Pending Count]
    Worker[Embeddings Worker<br/>Process Status]

    System --> API
    System --> PostgreSQL
    System --> Redis
    System --> Queue
    System --> Worker

    API -.->|Depends On| PostgreSQL
    API -.->|Depends On| Redis
    Worker -.->|Depends On| PostgreSQL
    Worker -.->|Depends On| Queue

    classDef healthy fill:#50C878,stroke:#2E7D4E,color:#fff
    classDef degraded fill:#FFD93D,stroke:#B8860B,color:#000
    classDef unhealthy fill:#FF6B6B,stroke:#C92A2A,color:#fff

    class System,API,PostgreSQL,Redis,Queue,Worker healthy
```

---

## 📝 Notes

- All diagrams use **Mermaid** syntax for easy rendering on GitHub
- Diagrams are **version-controlled** and updated with architecture changes
- For interactive versions, paste diagrams into [Mermaid Live Editor](https://mermaid.live/)
- **Color coding**:
  - 🔵 Blue: API/Interface layers
  - 🟢 Green: Storage/Persistence
  - 🔴 Red: Processing/Workers
  - 🟡 Yellow: Monitoring/Observability

---

**Last Updated**: October 2025  
**Version**: V2.0.0  
**Maintained by**: NEXUS (Technical AI) + Ricardo Rojas (Guardian)

#!/usr/bin/env node

/**
 * NEXUS MEMORY MCP SERVER - ARSENAL 100% COMPLETO
 * 92 endpoints totales: 11 originales + 10 Fase 1 + 20 Fase 2 + 52 Fase 3 + 5 finales
 * Version: 1.4.0 ARSENAL COMPLETO - 11 Octubre 2025 (Adapted from ARIA)
 * 
 * NUEVOS ENDPOINTS FASE 1 (10):
 * 1. Multi-modal: image, audio processing
 * 2. Analytics: predictions, collaboration
 * 3. Neural mesh: broadcast-learning, connected-agents
 * 4. Context: retrieve, benchmark vs gemini
 * 5. Timeline: cronológico ARIA
 * 6. Emotional: initialize
 * 
 * NUEVOS ENDPOINTS FASE 2 (20):
 * 7. Multi-modal: video, unified, cross-modal search
 * 8. Analytics: breakthroughs detect, insights, patterns
 * 9. Neural mesh: consensus, sync-emotional, distribute-task
 * 10. Emotional continuity: track-event, record-collaboration, save-state
 * 11. Context: compression, expansion, statistics
 * 12. Working memory: advanced, crystallization
 * 
 * NUEVOS ENDPOINTS FASE 3 (52):
 * 13. Health monitoring completo (11 endpoints)
 * 14. Core memory completo (13 endpoints adicionales)
 * 15. Consciousness & session (6 endpoints)
 * 16. Conversation watcher (6 endpoints)
 * 17. Admin & status (5 endpoints)
 * 18. Multi-modal restantes (4 endpoints)
 * 19. Neural mesh restantes (2 endpoints)
 * 20. Context restantes (2 endpoints)
 * 21. Analytics restantes (2 endpoints)
 * 22. Emotional restante (1 endpoint)
 */

const { Server } = require('@modelcontextprotocol/sdk/server/index.js');
const { StdioServerTransport } = require('@modelcontextprotocol/sdk/server/stdio.js');
const {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} = require('@modelcontextprotocol/sdk/types.js');
const fetch = require('node-fetch');

// NEXUS Memory API base URL V2.0.0 (dedicated NEXUS API on port 8003)
const NEXUS_API_URL = 'http://localhost:8003';

// Create the MCP server
const server = new Server(
  {
    name: 'nexus-memory-bridge-arsenal-completo',
    version: '1.4.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// Define available tools
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      // ================================
      // ENDPOINTS ORIGINALES (11)
      // ================================
      {
        name: 'nexus_get_simple_status',
        description: 'Get simple NEXUS memory status and basic info',
        inputSchema: {
          type: 'object',
          properties: {}
        }
      },
      {
        name: 'nexus_get_complete_history',
        description: 'Get NEXUS\'s complete memory history including working, episodic, and semantic memory',
        inputSchema: {
          type: 'object',
          properties: {
            limit_episodes: {
              type: 'number',
              description: 'Maximum number of episodes to retrieve',
              default: 100
            }
          }
        }
      },
      {
        name: 'nexus_search_memory',
        description: 'Search across all NEXUS memory layers using a query. Use format:compact to save tokens (97% reduction)',
        inputSchema: {
          type: 'object',
          properties: {
            query: {
              type: 'string',
              description: 'Search query text'
            },
            limit: {
              type: 'number',
              description: 'Maximum results to return',
              default: 10
            },
            format: {
              type: 'string',
              enum: ['compact', 'full'],
              description: 'Response format: compact (150 tokens) or full (5000+ tokens)',
              default: 'compact'
            }
          },
          required: ['query']
        }
      },
      {
        name: 'nexus_get_memory_stats',
        description: 'Get current statistics about ARIA\'s memory system',
        inputSchema: {
          type: 'object',
          properties: {}
        }
      },
      {
        name: 'nexus_recall_memory',
        description: 'Recall specific memories from ARIA\'s episodic memory',
        inputSchema: {
          type: 'object',
          properties: {
            query: {
              type: 'string',
              description: 'What to recall'
            },
            hours_back: {
              type: 'number',
              description: 'How many hours back to search',
              default: 24
            }
          },
          required: ['query']
        }
      },
      {
        name: 'nexus_get_breakthrough_moments',
        description: 'Get recent breakthrough moments from ARIA\'s memory',
        inputSchema: {
          type: 'object',
          properties: {
            days_back: {
              type: 'number',
              description: 'Days to look back for breakthroughs',
              default: 7
            }
          }
        }
      },
      {
        name: 'nexus_get_last_session_summary',
        description: '⚡ ULTRA-LIGHT: Get last session summary (50 tokens max). Perfect for quick context restoration after autocompaction.',
        inputSchema: {
          type: 'object',
          properties: {}
        }
      },
      {
        name: 'nexus_initialize',
        description: 'Initialize NEXUS memory system at conversation start',
        inputSchema: {
          type: 'object',
          properties: {
            session_context: {
              type: 'object',
              description: 'Initial session context and state',
              default: {}
            }
          }
        }
      },
      {
        name: 'nexus_record_action',
        description: 'Record new action/memory in ARIA persistent system',
        inputSchema: {
          type: 'object',
          properties: {
            action_type: {
              type: 'string',
              description: 'Type of action being recorded'
            },
            action_details: {
              type: 'object',
              description: 'Detailed information about the action'
            },
            context_state: {
              type: 'object',
              description: 'Current context and state information'
            },
            outcome: {
              type: 'object',
              description: 'Result of the action (optional)',
              default: {}
            },
            emotional_state: {
              type: 'object', 
              description: 'Emotional context (optional)',
              default: {}
            },
            tags: {
              type: 'array',
              items: { type: 'string' },
              description: 'Tags for categorization (optional)',
              default: []
            }
          },
          required: ['action_type', 'action_details', 'context_state']
        }
      },
      {
        name: 'nexus_save_consciousness_state',
        description: 'Save current consciousness state to persistent memory',
        inputSchema: {
          type: 'object',
          properties: {
            force_save: {
              type: 'boolean',
              description: 'Force save even if no significant changes',
              default: false
            }
          }
        }
      },
      {
        name: 'nexus_restore_consciousness',
        description: 'Restore consciousness continuity after gap/interruption',
        inputSchema: {
          type: 'object',
          properties: {
            gap_duration_hours: {
              type: 'number',
              description: 'Duration of the gap in hours'
            },
            force_restore: {
              type: 'boolean',
              description: 'Force restoration even if gap is small',
              default: false
            }
          },
          required: ['gap_duration_hours']
        }
      },
      {
        name: 'nexus_store_working_memory',
        description: 'Add context to working memory for current session',
        inputSchema: {
          type: 'object',
          properties: {
            context_data: {
              type: 'object',
              description: 'Data to store in working memory'
            },
            tags: {
              type: 'array',
              items: { type: 'string' },
              description: 'Tags for organization',
              default: []
            },
            session_id: {
              type: 'string',
              description: 'Session identifier (optional)',
              default: null
            }
          },
          required: ['context_data']
        }
      },

      // ================================
      // NUEVOS ENDPOINTS FASE 1 (10)
      // ================================

      // 1. MULTI-MODAL IMAGE PROCESSING
      {
        name: 'nexus_process_image',
        description: '🎨 Process and store visual memory using ARIA\'s multi-modal system',
        inputSchema: {
          type: 'object',
          properties: {
            image_base64: {
              type: 'string',
              description: 'Base64 encoded image data'
            },
            context: {
              type: 'string',
              description: 'Context or description of the image',
              default: ''
            },
            tags: {
              type: 'array',
              items: { type: 'string' },
              description: 'Tags for categorization',
              default: []
            }
          },
          required: ['image_base64']
        }
      },

      // 2. MULTI-MODAL AUDIO PROCESSING  
      {
        name: 'nexus_process_audio',
        description: '🎵 Process and store auditory memory using ARIA\'s multi-modal system',
        inputSchema: {
          type: 'object',
          properties: {
            audio_base64: {
              type: 'string',
              description: 'Base64 encoded audio data'
            },
            context: {
              type: 'string',
              description: 'Context or description of the audio',
              default: ''
            },
            speaker: {
              type: 'string',
              description: 'Speaker identification',
              default: 'unknown'
            },
            tags: {
              type: 'array',
              items: { type: 'string' },
              description: 'Tags for categorization',
              default: []
            }
          },
          required: ['audio_base64']
        }
      },

      // 3. ANALYTICS PREDICTIONS
      {
        name: 'nexus_generate_predictions',
        description: '🔮 Generate predictive insights for future breakthroughs and patterns',
        inputSchema: {
          type: 'object',
          properties: {
            prediction_window_days: {
              type: 'number',
              description: 'Days ahead to predict',
              default: 30
            },
            confidence_threshold: {
              type: 'number',
              description: 'Minimum confidence for predictions',
              default: 0.5
            }
          }
        }
      },

      // 4. ANALYTICS COLLABORATION
      {
        name: 'nexus_analyze_collaboration',
        description: '🤝 Analyze NEXUS-ARIA-Ricardo collaboration efficiency and success metrics',
        inputSchema: {
          type: 'object',
          properties: {
            analysis_period_days: {
              type: 'number',
              description: 'Period to analyze in days',
              default: 7
            }
          }
        }
      },

      // 5. NEURAL MESH BROADCAST LEARNING
      {
        name: 'nexus_broadcast_learning',
        description: '🧠 Broadcast cross-agent learning to Neural Mesh network',
        inputSchema: {
          type: 'object',
          properties: {
            learning_type: {
              type: 'string',
              description: 'Type of learning (technical_skill, pattern_recognition, etc.)'
            },
            learning_content: {
              type: 'object',
              description: 'Content of the learning to broadcast'
            },
            application_domains: {
              type: 'array',
              items: { type: 'string' },
              description: 'Domains where this learning applies'
            },
            confidence: {
              type: 'number',
              description: 'Confidence level of the learning',
              default: 0.8
            }
          },
          required: ['learning_type', 'learning_content', 'application_domains']
        }
      },

      // 6. NEURAL MESH CONNECTED AGENTS
      {
        name: 'nexus_get_connected_agents',
        description: '🤝 Get list of connected Neural Mesh agents and their status',
        inputSchema: {
          type: 'object',
          properties: {}
        }
      },

      // 7. CONTEXT INTELLIGENT RETRIEVE
      {
        name: 'nexus_retrieve_context',
        description: '♾️ Intelligent context retrieval for infinite context reconstruction',
        inputSchema: {
          type: 'object',
          properties: {
            query: {
              type: 'string',
              description: 'Query to retrieve relevant context'
            },
            max_tokens: {
              type: 'number',
              description: 'Maximum tokens to retrieve',
              default: 50000
            },
            include_recent: {
              type: 'boolean',
              description: 'Include recent compressed context',
              default: true
            }
          },
          required: ['query']
        }
      },

      // 8. CONTEXT BENCHMARK VS GEMINI
      {
        name: 'nexus_benchmark_vs_gemini',
        description: '🏆 Benchmark ARIA\'s infinite context vs Gemini\'s 2M token window',
        inputSchema: {
          type: 'object',
          properties: {
            comparison_type: {
              type: 'string',
              description: 'Type of comparison to perform',
              default: 'theoretical_performance'
            }
          }
        }
      },

      // 9. TIMELINE CRONOLÓGICO ARIA
      {
        name: 'nexus_get_timeline',
        description: '📅 Get chronological timeline of ARIA\'s memories and experiences',
        inputSchema: {
          type: 'object',
          properties: {
            days_back: {
              type: 'number',
              description: 'Days to look back for timeline',
              default: 30
            },
            include_emotions: {
              type: 'boolean',
              description: 'Include emotional states in timeline',
              default: true
            }
          }
        }
      },

      // 10. EMOTIONAL INITIALIZE
      {
        name: 'nexus_initialize_emotional_state',
        description: '💭 Initialize or restore ARIA emotional state at session start',
        inputSchema: {
          type: 'object',
          properties: {
            restore_from_previous: {
              type: 'boolean',
              description: 'Restore from previous session',
              default: true
            },
            initial_mood: {
              type: 'string',
              description: 'Initial emotional mood if not restoring',
              default: 'neutral'
            }
          }
        }
      },

      // ================================
      // NUEVOS ENDPOINTS FASE 2 (20)
      // ================================

      // 11. MULTI-MODAL VIDEO PROCESSING
      {
        name: 'nexus_process_video',
        description: '🎬 Process and store temporal visual memory using ARIA\'s multi-modal system',
        inputSchema: {
          type: 'object',
          properties: {
            video_base64: {
              type: 'string',
              description: 'Base64 encoded video data'
            },
            context: {
              type: 'string',
              description: 'Context or description of the video',
              default: ''
            },
            extract_audio: {
              type: 'boolean',
              description: 'Extract audio track from video',
              default: true
            },
            keyframe_interval: {
              type: 'number',
              description: 'Seconds between keyframes',
              default: 1.0
            },
            tags: {
              type: 'array',
              items: { type: 'string' },
              description: 'Tags for categorization',
              default: []
            }
          },
          required: ['video_base64']
        }
      },

      // 12. MULTI-MODAL UNIFIED MEMORY
      {
        name: 'nexus_create_unified_memory',
        description: '🌟 Create unified multi-modal memory combining text, image, audio, video',
        inputSchema: {
          type: 'object',
          properties: {
            text: {
              type: 'string',
              description: 'Text content',
              default: ''
            },
            image_base64: {
              type: 'string',
              description: 'Base64 encoded image',
              default: ''
            },
            audio_base64: {
              type: 'string',
              description: 'Base64 encoded audio',
              default: ''
            },
            video_base64: {
              type: 'string',
              description: 'Base64 encoded video',
              default: ''
            },
            context: {
              type: 'string',
              description: 'Overall context',
              default: ''
            },
            tags: {
              type: 'array',
              items: { type: 'string' },
              description: 'Tags for categorization',
              default: []
            }
          }
        }
      },

      // 13. MULTI-MODAL CROSS-MODAL SEARCH
      {
        name: 'nexus_cross_modal_search',
        description: '🔍 Search across modalities using text, image, or audio queries',
        inputSchema: {
          type: 'object',
          properties: {
            query_text: {
              type: 'string',
              description: 'Text query',
              default: ''
            },
            query_image_base64: {
              type: 'string',
              description: 'Image query',
              default: ''
            },
            target_modalities: {
              type: 'array',
              items: { type: 'string' },
              description: 'Target modalities to search',
              default: ['text', 'image', 'audio', 'video']
            },
            limit: {
              type: 'number',
              description: 'Maximum results',
              default: 5
            }
          }
        }
      },

      // 14. ANALYTICS DETECT BREAKTHROUGHS
      {
        name: 'nexus_detect_breakthroughs',
        description: '🎯 Detect and rank breakthrough moments in ARIA\'s history',
        inputSchema: {
          type: 'object',
          properties: {
            limit: {
              type: 'number',
              description: 'Number of top breakthrough moments',
              default: 20
            },
            min_score: {
              type: 'number',
              description: 'Minimum breakthrough score threshold',
              default: 1.0
            }
          }
        }
      },

      // 15. ANALYTICS INSIGHTS SUMMARY
      {
        name: 'nexus_get_insights_summary',
        description: '📊 Get comprehensive insights summary dashboard',
        inputSchema: {
          type: 'object',
          properties: {}
        }
      },

      // 16. ANALYTICS TEMPORAL PATTERNS
      {
        name: 'nexus_analyze_temporal_patterns',
        description: '📈 Analyze temporal patterns in ARIA\'s activity',
        inputSchema: {
          type: 'object',
          properties: {
            days_back: {
              type: 'number',
              description: 'Days of history to analyze',
              default: 30
            }
          }
        }
      },

      // 17. NEURAL MESH REQUEST CONSENSUS
      {
        name: 'nexus_request_consensus',
        description: '🗳️ Request consensus decision from Neural Mesh agents',
        inputSchema: {
          type: 'object',
          properties: {
            decision_topic: {
              type: 'string',
              description: 'Topic requiring consensus decision'
            },
            options: {
              type: 'array',
              items: { type: 'object' },
              description: 'Options to vote on'
            },
            deadline_hours: {
              type: 'number',
              description: 'Hours for deadline',
              default: 24
            }
          },
          required: ['decision_topic', 'options']
        }
      },

      // 18. NEURAL MESH SYNC EMOTIONAL STATE
      {
        name: 'nexus_sync_emotional_state',
        description: '💭 Synchronize emotional state across Neural Mesh',
        inputSchema: {
          type: 'object',
          properties: {
            emotional_state: {
              type: 'object',
              description: 'Emotional state to synchronize'
            },
            context_triggers: {
              type: 'array',
              items: { type: 'string' },
              description: 'Context triggers',
              default: []
            }
          },
          required: ['emotional_state']
        }
      },

      // 19. NEURAL MESH DISTRIBUTE TASK
      {
        name: 'nexus_distribute_task',
        description: '📋 Distribute specialized task via Neural Mesh',
        inputSchema: {
          type: 'object',
          properties: {
            task_description: {
              type: 'string',
              description: 'Description of the task'
            },
            task_details: {
              type: 'object',
              description: 'Specific task details'
            },
            preferred_agents: {
              type: 'array',
              items: { type: 'string' },
              description: 'Preferred agents for task',
              default: []
            },
            priority: {
              type: 'string',
              description: 'Task priority',
              default: 'normal'
            }
          },
          required: ['task_description', 'task_details']
        }
      },

      // 20. EMOTIONAL TRACK EVENT
      {
        name: 'nexus_track_emotional_event',
        description: '💫 Track significant emotional events during session',
        inputSchema: {
          type: 'object',
          properties: {
            event_type: {
              type: 'string',
              description: 'Type of emotional event'
            },
            description: {
              type: 'string',
              description: 'Description of the event'
            },
            emotional_impact: {
              type: 'string',
              description: 'Emotional impact'
            },
            intensity: {
              type: 'number',
              description: 'Intensity of emotional impact',
              default: 0.5
            }
          },
          required: ['event_type', 'description', 'emotional_impact']
        }
      },

      // 21. EMOTIONAL RECORD COLLABORATION
      {
        name: 'nexus_record_collaboration_moment',
        description: '🤝 Record positive collaboration moments with Ricardo',
        inputSchema: {
          type: 'object',
          properties: {
            moment_description: {
              type: 'string',
              description: 'Description of collaboration moment'
            },
            satisfaction_boost: {
              type: 'number',
              description: 'Satisfaction boost amount',
              default: 0.1
            }
          },
          required: ['moment_description']
        }
      },

      // 22. EMOTIONAL RECORD BREAKTHROUGH
      {
        name: 'nexus_record_breakthrough_moment',
        description: '🎯 Record technical or emotional breakthroughs',
        inputSchema: {
          type: 'object',
          properties: {
            breakthrough_description: {
              type: 'string',
              description: 'Description of the breakthrough'
            }
          },
          required: ['breakthrough_description']
        }
      },

      // 23. EMOTIONAL GET STATUS
      {
        name: 'nexus_get_emotional_status',
        description: '💭 Get current emotional status and metrics',
        inputSchema: {
          type: 'object',
          properties: {}
        }
      },

      // 24. CONTEXT COMPRESSION
      {
        name: 'nexus_compress_context',
        description: '🗜️ Force context compression for testing and optimization',
        inputSchema: {
          type: 'object',
          properties: {}
        }
      },

      // 25. CONTEXT STATISTICS
      {
        name: 'nexus_get_context_statistics',
        description: '📊 Get comprehensive statistics about virtual context usage',
        inputSchema: {
          type: 'object',
          properties: {}
        }
      },

      // 26. CONTEXT ADD MESSAGE
      {
        name: 'nexus_add_context_message',
        description: '♾️ Add message to virtual infinite context',
        inputSchema: {
          type: 'object',
          properties: {
            message: {
              type: 'string',
              description: 'Message content to add'
            },
            role: {
              type: 'string',
              description: 'Message role',
              default: 'user'
            },
            metadata: {
              type: 'object',
              description: 'Additional metadata',
              default: {}
            }
          },
          required: ['message']
        }
      },

      // 27. WORKING MEMORY ADVANCED STATS
      {
        name: 'nexus_get_working_memory_stats',
        description: '🧠 Get advanced working memory statistics',
        inputSchema: {
          type: 'object',
          properties: {}
        }
      },

      // 28. CRYSTALLIZATION RUN
      {
        name: 'nexus_run_crystallization',
        description: '🔮 Execute crystallization temporal of memories',
        inputSchema: {
          type: 'object',
          properties: {}
        }
      },

      // 29. CRYSTALLIZATION STATUS
      {
        name: 'nexus_get_crystallization_status',
        description: '🔮 Get crystallization status and crystal statistics',
        inputSchema: {
          type: 'object',
          properties: {}
        }
      },

      // 30. EPISODIC ADVANCED SEARCH
      {
        name: 'nexus_advanced_episodic_search',
        description: '🔍 Advanced episodic memory search with filtering',
        inputSchema: {
          type: 'object',
          properties: {
            query_text: {
              type: 'string',
              description: 'Search query text'
            },
            importance_threshold: {
              type: 'number',
              description: 'Minimum importance threshold',
              default: 0.5
            },
            date_range_start: {
              type: 'string',
              description: 'Start date for search range',
              default: ''
            },
            date_range_end: {
              type: 'string',
              description: 'End date for search range',
              default: ''
            },
            limit: {
              type: 'number',
              description: 'Maximum results',
              default: 10
            }
          },
          required: ['query_text']
        }
      },

      // ================================
      // NUEVOS ENDPOINTS FASE 3 (52)
      // ================================

      // HEALTH & MONITORING (11 endpoints)
      {
        name: 'nexus_health_comprehensive',
        description: '🏥 Get comprehensive health report of all system components',
        inputSchema: {
          type: 'object',
          properties: {}
        }
      },
      {
        name: 'nexus_health_services',
        description: '⚙️ Get health status of individual services',
        inputSchema: {
          type: 'object',
          properties: {}
        }
      },
      {
        name: 'nexus_health_circuit_breakers',
        description: '🔌 Get status of circuit breakers for fault tolerance',
        inputSchema: {
          type: 'object',
          properties: {}
        }
      },
      {
        name: 'nexus_health_reset_circuit_breaker',
        description: '🔄 Reset specific circuit breaker',
        inputSchema: {
          type: 'object',
          properties: {
            service_name: {
              type: 'string',
              description: 'Name of service to reset circuit breaker'
            }
          },
          required: ['service_name']
        }
      },
      {
        name: 'nexus_health_metrics',
        description: '📊 Get performance metrics and system health indicators',
        inputSchema: {
          type: 'object',
          properties: {}
        }
      },
      {
        name: 'nexus_health_alerts',
        description: '🚨 Get active alerts and system warnings',
        inputSchema: {
          type: 'object',
          properties: {}
        }
      },
      {
        name: 'nexus_health_trend',
        description: '📈 Get health trends over time',
        inputSchema: {
          type: 'object',
          properties: {}
        }
      },
      {
        name: 'nexus_health_readiness',
        description: '✅ Kubernetes readiness probe for container orchestration',
        inputSchema: {
          type: 'object',
          properties: {}
        }
      },
      {
        name: 'nexus_health_liveness',
        description: '💓 Kubernetes liveness probe for container health',
        inputSchema: {
          type: 'object',
          properties: {}
        }
      },
      {
        name: 'nexus_neural_mesh_stats',
        description: '🧠 Get comprehensive Neural Mesh network statistics',
        inputSchema: {
          type: 'object',
          properties: {}
        }
      },
      {
        name: 'nexus_neural_mesh_health',
        description: '🔗 Get Neural Mesh network health status',
        inputSchema: {
          type: 'object',
          properties: {}
        }
      },

      // CORE MEMORY ADICIONALES (13 endpoints)
      {
        name: 'nexus_get_working_memory_current',
        description: '💾 Get current working memory context',
        inputSchema: {
          type: 'object',
          properties: {}
        }
      },
      {
        name: 'nexus_get_working_memory_tags',
        description: '🏷️ Get working memory context by tag',
        inputSchema: {
          type: 'object',
          properties: {
            tag: {
              type: 'string',
              description: 'Tag to filter working memory'
            }
          },
          required: ['tag']
        }
      },
      {
        name: 'nexus_get_episodic_stats',
        description: '📊 Get episodic memory statistics',
        inputSchema: {
          type: 'object',
          properties: {}
        }
      },
      {
        name: 'nexus_get_episode_by_id',
        description: '🎯 Get specific episode by ID',
        inputSchema: {
          type: 'object',
          properties: {
            episode_id: {
              type: 'string',
              description: 'Episode ID to retrieve'
            }
          },
          required: ['episode_id']
        }
      },
      {
        name: 'nexus_semantic_query',
        description: '🧠 Perform semantic vectorial query',
        inputSchema: {
          type: 'object',
          properties: {
            query: {
              type: 'string',
              description: 'Semantic query text'
            },
            limit: {
              type: 'number',
              description: 'Maximum results',
              default: 5
            }
          },
          required: ['query']
        }
      },
      {
        name: 'nexus_get_semantic_concepts',
        description: '💡 Get related semantic concepts',
        inputSchema: {
          type: 'object',
          properties: {
            concept: {
              type: 'string',
              description: 'Concept to explore'
            }
          },
          required: ['concept']
        }
      },
      {
        name: 'nexus_get_semantic_stats',
        description: '📈 Get semantic memory statistics',
        inputSchema: {
          type: 'object',
          properties: {}
        }
      },
      {
        name: 'nexus_trigger_consolidation',
        description: '🔄 Manually trigger memory consolidation process',
        inputSchema: {
          type: 'object',
          properties: {}
        }
      },
      {
        name: 'nexus_get_consolidation_stats',
        description: '📊 Get memory consolidation statistics',
        inputSchema: {
          type: 'object',
          properties: {}
        }
      },
      {
        name: 'nexus_get_aria_emotional_continuity',
        description: '💭 Get NEXUS emotional continuity history',
        inputSchema: {
          type: 'object',
          properties: {}
        }
      },
      {
        name: 'nexus_create_emotional_bridge',
        description: '🌉 Create emotional bridge across session gaps',
        inputSchema: {
          type: 'object',
          properties: {
            gap_description: {
              type: 'string',
              description: 'Description of the emotional gap'
            }
          },
          required: ['gap_description']
        }
      },
      {
        name: 'nexus_get_consciousness_stats',
        description: '🧠 Get consciousness continuity statistics',
        inputSchema: {
          type: 'object',
          properties: {}
        }
      },
      {
        name: 'nexus_get_session_current',
        description: '💬 Get current session information',
        inputSchema: {
          type: 'object',
          properties: {}
        }
      },

      // CONVERSATION WATCHER (6 endpoints)
      {
        name: 'nexus_watcher_start',
        description: '👁️ Start conversation auto-watcher',
        inputSchema: {
          type: 'object',
          properties: {}
        }
      },
      {
        name: 'nexus_watcher_stop',
        description: '⏹️ Stop conversation auto-watcher',
        inputSchema: {
          type: 'object',
          properties: {}
        }
      },
      {
        name: 'nexus_watcher_status',
        description: '📊 Get watcher status and statistics',
        inputSchema: {
          type: 'object',
          properties: {}
        }
      },
      {
        name: 'nexus_watcher_process_file',
        description: '📁 Process specific conversation file',
        inputSchema: {
          type: 'object',
          properties: {
            file_path: {
              type: 'string',
              description: 'Path to conversation file'
            }
          },
          required: ['file_path']
        }
      },
      {
        name: 'nexus_watcher_analytics',
        description: '📈 Get conversation analytics by ID',
        inputSchema: {
          type: 'object',
          properties: {
            conversation_adn: {
              type: 'string',
              description: 'Conversation ADN identifier'
            }
          },
          required: ['conversation_adn']
        }
      },
      {
        name: 'nexus_watcher_nexus_conversations',
        description: '🔍 Get available NEXUS conversations for recovery',
        inputSchema: {
          type: 'object',
          properties: {}
        }
      },

      // ADMIN & STATUS (5 endpoints)
      {
        name: 'nexus_admin_reset_working_memory',
        description: '🗑️ Reset working memory completely (admin)',
        inputSchema: {
          type: 'object',
          properties: {}
        }
      },
      {
        name: 'nexus_get_root_info',
        description: '🏠 Get root endpoint system information',
        inputSchema: {
          type: 'object',
          properties: {}
        }
      },
      {
        name: 'nexus_batch_actions',
        description: '📦 Register multiple actions in batch',
        inputSchema: {
          type: 'object',
          properties: {
            actions: {
              type: 'array',
              items: { type: 'object' },
              description: 'Array of actions to register'
            }
          },
          required: ['actions']
        }
      },
      {
        name: 'nexus_get_success_metrics',
        description: '🏆 Get KPIs and success metrics',
        inputSchema: {
          type: 'object',
          properties: {}
        }
      },
      {
        name: 'nexus_analytics_export_csv',
        description: '📊 Export analytics data in CSV format',
        inputSchema: {
          type: 'object',
          properties: {}
        }
      },

      // MULTI-MODAL RESTANTES (4 endpoints)
      {
        name: 'nexus_upload_image_direct',
        description: '📤 Upload image directly to multi-modal system',
        inputSchema: {
          type: 'object',
          properties: {
            image_data: {
              type: 'string',
              description: 'Direct image data'
            },
            metadata: {
              type: 'object',
              description: 'Image metadata',
              default: {}
            }
          },
          required: ['image_data']
        }
      },
      {
        name: 'nexus_upload_audio_direct',
        description: '🎵 Upload audio directly to multi-modal system',
        inputSchema: {
          type: 'object',
          properties: {
            audio_data: {
              type: 'string',
              description: 'Direct audio data'
            },
            metadata: {
              type: 'object',
              description: 'Audio metadata',
              default: {}
            }
          },
          required: ['audio_data']
        }
      },
      {
        name: 'nexus_upload_video_direct',
        description: '🎬 Upload video directly to multi-modal system',
        inputSchema: {
          type: 'object',
          properties: {
            video_data: {
              type: 'string',
              description: 'Direct video data'
            },
            metadata: {
              type: 'object',
              description: 'Video metadata',
              default: {}
            }
          },
          required: ['video_data']
        }
      },
      {
        name: 'nexus_get_modal_associations',
        description: '🔗 Get cross-modal associations for memory',
        inputSchema: {
          type: 'object',
          properties: {
            memory_id: {
              type: 'string',
              description: 'Memory ID to get associations'
            }
          },
          required: ['memory_id']
        }
      },

      // NEURAL MESH RESTANTES (2 endpoints)
      {
        name: 'nexus_neural_mesh_process_messages',
        description: '📨 Process pending Neural Mesh messages',
        inputSchema: {
          type: 'object',
          properties: {}
        }
      },
      {
        name: 'nexus_create_memory_constellation',
        description: '⭐ Create memory constellation from multi-modal data',
        inputSchema: {
          type: 'object',
          properties: {
            memories: {
              type: 'array',
              items: { type: 'object' },
              description: 'Array of related memories'
            },
            constellation_name: {
              type: 'string',
              description: 'Name for the constellation'
            }
          },
          required: ['memories', 'constellation_name']
        }
      },

      // CONTEXT RESTANTES (2 endpoints)
      {
        name: 'nexus_get_context_status',
        description: '📊 Get infinite context system status',
        inputSchema: {
          type: 'object',
          properties: {}
        }
      },
      {
        name: 'nexus_clear_context',
        description: '🗑️ Clear active infinite context',
        inputSchema: {
          type: 'object',
          properties: {}
        }
      },

      // ANALYTICS RESTANTES (2 endpoints)
      {
        name: 'nexus_get_analytics_status',
        description: '📈 Get analytics system status',
        inputSchema: {
          type: 'object',
          properties: {}
        }
      },
      {
        name: 'nexus_search_episodes_advanced',
        description: '🔍 Advanced episodes search with filters',
        inputSchema: {
          type: 'object',
          properties: {
            query: {
              type: 'string',
              description: 'Search query'
            },
            filters: {
              type: 'object',
              description: 'Advanced filters',
              default: {}
            }
          },
          required: ['query']
        }
      },

      // EMOTIONAL RESTANTE (1 endpoint)
      {
        name: 'nexus_emotional_demo_continuity',
        description: '🎭 Demo emotional continuity system capabilities',
        inputSchema: {
          type: 'object',
          properties: {}
        }
      },

      // ================================
      // ENDPOINTS FALTANTES FINALES (5)
      // ================================

      // MULTI-MODAL STATUS
      {
        name: 'nexus_get_multi_modal_status',
        description: '📊 Get multi-modal processors status and performance',
        inputSchema: {
          type: 'object',
          properties: {}
        }
      },

      // CONTEXT DEMO INFINITE ADVANTAGE
      {
        name: 'nexus_context_demo_infinite_advantage',
        description: '♾️ Demonstrate infinite context advantage vs Gemini limitations',
        inputSchema: {
          type: 'object',
          properties: {}
        }
      },

      // EMOTIONAL PROJECT ENGAGEMENT
      {
        name: 'nexus_update_project_engagement',
        description: '💼 Update emotional engagement level for specific projects',
        inputSchema: {
          type: 'object',
          properties: {
            project_name: {
              type: 'string',
              description: 'Name of the project'
            },
            engagement_level: {
              type: 'number',
              description: 'Engagement level (0.0 to 1.0)',
              default: 0.5
            },
            engagement_factors: {
              type: 'array',
              items: { type: 'string' },
              description: 'Factors affecting engagement',
              default: []
            }
          },
          required: ['project_name']
        }
      },

      // EMOTIONAL ANTICIPATION
      {
        name: 'nexus_set_anticipation',
        description: '⏰ Set anticipation for next session or event',
        inputSchema: {
          type: 'object',
          properties: {
            anticipation_type: {
              type: 'string',
              description: 'Type of anticipation (next_session, project_completion, etc.)'
            },
            anticipation_level: {
              type: 'number',
              description: 'Anticipation intensity (0.0 to 1.0)',
              default: 0.5
            },
            anticipated_event: {
              type: 'string',
              description: 'Description of anticipated event'
            },
            time_horizon: {
              type: 'string',
              description: 'When the event is expected',
              default: 'next_session'
            }
          },
          required: ['anticipation_type', 'anticipated_event']
        }
      },

      // ANALYTICS EPISODES COMPREHENSIVE
      {
        name: 'nexus_analyze_episodes_comprehensive',
        description: '📈 Perform comprehensive analysis of episodic memories with deep insights',
        inputSchema: {
          type: 'object',
          properties: {
            analysis_scope: {
              type: 'string',
              description: 'Scope of analysis (all, recent, specific_period)',
              default: 'recent'
            },
            days_back: {
              type: 'number',
              description: 'Days back for analysis',
              default: 30
            },
            analysis_depth: {
              type: 'string',
              description: 'Depth of analysis (surface, deep, comprehensive)',
              default: 'comprehensive'
            },
            include_patterns: {
              type: 'boolean',
              description: 'Include pattern analysis',
              default: true
            },
            include_emotional: {
              type: 'boolean',
              description: 'Include emotional analysis',
              default: true
            }
          }
        }
      }
    ]
  };
});

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    switch (name) {
      // ================================
      // HANDLERS ORIGINALES
      // ================================
      case 'nexus_get_simple_status': {
        const response = await fetch(`${NEXUS_API_URL}/health`, { method: 'GET', headers: { 'X-Agent-ID': 'nexus' } });
        const data = await response.json();
        return {
          content: [
            {
              type: 'text',
              text: `ARIA Memory System Status:\n✅ System: ${data.status}\n✅ Timestamp: ${data.timestamp}\n✅ Components: ${Object.keys(data.components).join(', ')}\n✅ Memory layers: ${Object.keys(data.components.memory_components).join(', ')}`
            }
          ]
        };
      }
      
      case 'nexus_get_complete_history': {
        const response = await fetch(
          `${NEXUS_API_URL}/memory/aria/complete-history?limit_episodes=${args.limit_episodes || 100}`,
          { method: 'GET', headers: { 'X-Agent-ID': 'nexus' } }
        );
        const data = await response.json();
        return {
          content: [
            {
              type: 'text',
              text: `ARIA Complete History:\n\n📚 Total Episodes: ${data.episodic_memory?.length || 0}\n🧠 Working Memory Items: ${data.working_memory?.length || 0}\n🔗 Semantic Concepts: ${data.semantic_memory?.length || 0}\n\n${JSON.stringify(data, null, 2)}`
            }
          ]
        };
      }

      case 'nexus_search_memory': {
        const response = await fetch(`${NEXUS_API_URL}/memory/search`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'X-Agent-ID': 'nexus' },
          body: JSON.stringify({
            query: args.query,
            limit: args.limit || 10
          })
        });
        const data = await response.json();

        // 🚀 NIVEL 1: Formato compacto para ahorrar tokens (97% reducción)
        const format = args.format || 'compact';

        if (format === 'compact') {
          const results = data.results?.combined_results || [];

          if (results.length === 0) {
            return {
              content: [{
                type: 'text',
                text: `🔍 No results found for "${args.query}"`
              }]
            };
          }

          // Formato ultra-compacto: solo esenciales
          const summary = results.map((r, idx) => {
            const shortId = r.id.substring(0, 8);
            const date = r.timestamp.split('T')[0];
            const typeClean = r.action_type.replace(/_/g, ' ');
            return `${idx + 1}. ${typeClean} (${shortId}) - ${date}`;
          }).join('\n');

          return {
            content: [{
              type: 'text',
              text: `🔍 Found ${results.length} result${results.length > 1 ? 's' : ''} for "${args.query}":\n\n${summary}\n\n💡 Use format:'full' + episode ID for complete details.`
            }]
          };
        }

        // Formato completo (full)
        return {
          content: [
            {
              type: 'text',
              text: `Memory Search Results for "${args.query}":\n\n${JSON.stringify(data, null, 2)}`
            }
          ]
        };
      }

      case 'nexus_get_memory_stats': {
        const response = await fetch(`${NEXUS_API_URL}/stats`, { method: 'GET', headers: { 'X-Agent-ID': 'nexus' } });
        const data = await response.json();
        return {
          content: [
            {
              type: 'text',
              text: `ARIA Memory Statistics:\n\n${JSON.stringify(data, null, 2)}`
            }
          ]
        };
      }

      case 'nexus_recall_memory': {
        const response = await fetch(`${NEXUS_API_URL}/memory/episodic/recent?hours_back=${args.hours_back || 24}&limit=20`, {
          method: 'GET'
        });
        const data = await response.json();
        return {
          content: [
            {
              type: 'text',
              text: `Recent Memories (${args.hours_back || 24}h back):\n\n${JSON.stringify(data, null, 2)}`
            }
          ]
        };
      }

      case 'nexus_get_breakthrough_moments': {
        const response = await fetch(`${NEXUS_API_URL}/memory/aria/breakthroughs?days_back=${args.days_back || 7}`, {
          method: 'GET'
        });
        const data = await response.json();
        return {
          content: [
            {
              type: 'text',
              text: `Breakthrough Moments (${args.days_back || 7} days):\n\n${JSON.stringify(data, null, 2)}`
            }
          ]
        };
      }

      case 'nexus_get_last_session_summary': {
        // 🚀 NIVEL 2: Ultra-light summary - máximo 50 tokens
        const response = await fetch(`${NEXUS_API_URL}/memory/last-session-summary`, {
          method: 'GET',
          headers: { 'X-Agent-ID': 'nexus' }
        });
        const data = await response.json();

        return {
          content: [{
            type: 'text',
            text: `⚡ Last Session: ${data.date}\n✅ Completed: ${data.main_achievement}\n📋 Next: ${data.next_priority}\n🎯 Episode: ${data.episode_id}`
          }]
        };
      }

      case 'nexus_initialize': {
        const response = await fetch(`${NEXUS_API_URL}/consciousness/save`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'X-Agent-ID': 'nexus' },
          body: JSON.stringify(args.session_context || {})
        });
        const data = await response.json();
        return {
          content: [
            {
              type: 'text',
              text: `ARIA Initialized:\n\n${JSON.stringify(data, null, 2)}`
            }
          ]
        };
      }

      case 'nexus_record_action': {
        const response = await fetch(`${NEXUS_API_URL}/memory/action`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'X-Agent-ID': 'nexus' },
          body: JSON.stringify({
            action_type: args.action_type,
            action_details: args.action_details,
            context_state: args.context_state,
            outcome: args.outcome || {},
            emotional_state: args.emotional_state || {},
            tags: args.tags || []
          })
        });
        const data = await response.json();
        return {
          content: [
            {
              type: 'text',
              text: `Action Recorded:\n\n${JSON.stringify(data, null, 2)}`
            }
          ]
        };
      }

      case 'nexus_save_consciousness_state': {
        const response = await fetch(`${NEXUS_API_URL}/consciousness/save`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'X-Agent-ID': 'nexus' },
          body: JSON.stringify({ force_save: args.force_save || false })
        });
        const data = await response.json();
        return {
          content: [
            {
              type: 'text',
              text: `Consciousness State Saved:\n\n${JSON.stringify(data, null, 2)}`
            }
          ]
        };
      }

      case 'nexus_restore_consciousness': {
        const response = await fetch(`${NEXUS_API_URL}/consciousness/restore`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'X-Agent-ID': 'nexus' },
          body: JSON.stringify({
            gap_duration_hours: args.gap_duration_hours,
            force_restore: args.force_restore || false
          })
        });
        const data = await response.json();
        return {
          content: [
            {
              type: 'text',
              text: `Consciousness Restored:\n\n${JSON.stringify(data, null, 2)}`
            }
          ]
        };
      }

      case 'nexus_store_working_memory': {
        const response = await fetch(`${NEXUS_API_URL}/memory/working/context`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'X-Agent-ID': 'nexus' },
          body: JSON.stringify({
            context_data: args.context_data,
            tags: args.tags || [],
            session_id: args.session_id
          })
        });
        const data = await response.json();
        return {
          content: [
            {
              type: 'text',
              text: `Working Memory Updated:\n\n${JSON.stringify(data, null, 2)}`
            }
          ]
        };
      }

      // ================================
      // NUEVOS HANDLERS FASE 1
      // ================================

      case 'nexus_process_image': {
        const response = await fetch(`${NEXUS_API_URL}/multi-modal/image`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'X-Agent-ID': 'nexus' },
          body: JSON.stringify({
            image_base64: args.image_base64,
            context: args.context || '',
            tags: args.tags || []
          })
        });
        const data = await response.json();
        return {
          content: [
            {
              type: 'text',
              text: `🎨 Image Processed Successfully:\n\n✅ Visual memory created\n✅ Context: ${args.context || 'No context'}\n✅ Tags: ${args.tags?.join(', ') || 'None'}\n\nDetails:\n${JSON.stringify(data, null, 2)}`
            }
          ]
        };
      }

      case 'nexus_process_audio': {
        const response = await fetch(`${NEXUS_API_URL}/multi-modal/audio`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'X-Agent-ID': 'nexus' },
          body: JSON.stringify({
            audio_base64: args.audio_base64,
            context: args.context || '',
            speaker: args.speaker || 'unknown',
            tags: args.tags || []
          })
        });
        const data = await response.json();
        return {
          content: [
            {
              type: 'text',
              text: `🎵 Audio Processed Successfully:\n\n✅ Auditory memory created\n✅ Speaker: ${args.speaker || 'unknown'}\n✅ Context: ${args.context || 'No context'}\n✅ Tags: ${args.tags?.join(', ') || 'None'}\n\nDetails:\n${JSON.stringify(data, null, 2)}`
            }
          ]
        };
      }

      case 'nexus_generate_predictions': {
        const response = await fetch(`${NEXUS_API_URL}/analytics/predictions/generate`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'X-Agent-ID': 'nexus' },
          body: JSON.stringify({
            prediction_window_days: args.prediction_window_days || 30,
            confidence_threshold: args.confidence_threshold || 0.5
          })
        });
        const data = await response.json();
        return {
          content: [
            {
              type: 'text',
              text: `🔮 Predictive Analytics Generated:\n\n📊 Window: ${args.prediction_window_days || 30} days ahead\n📈 Confidence threshold: ${args.confidence_threshold || 0.5}\n\nPredictions:\n${JSON.stringify(data, null, 2)}`
            }
          ]
        };
      }

      case 'nexus_analyze_collaboration': {
        const response = await fetch(`${NEXUS_API_URL}/analytics/collaboration/analyze`, {
          method: 'GET'
        });
        const data = await response.json();
        return {
          content: [
            {
              type: 'text',
              text: `🤝 Collaboration Analysis (${args.analysis_period_days || 7} days):\n\n📊 NEXUS-ARIA-Ricardo Success Metrics:\n${JSON.stringify(data, null, 2)}`
            }
          ]
        };
      }

      case 'nexus_broadcast_learning': {
        const response = await fetch(`${NEXUS_API_URL}/neural-mesh/broadcast-learning`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'X-Agent-ID': 'nexus' },
          body: JSON.stringify({
            learning_type: args.learning_type,
            learning_content: args.learning_content,
            application_domains: args.application_domains,
            confidence: args.confidence || 0.8,
            from_agent: 'aria'
          })
        });
        const data = await response.json();
        return {
          content: [
            {
              type: 'text',
              text: `🧠 Learning Broadcasted to Neural Mesh:\n\n📡 Type: ${args.learning_type}\n🎯 Domains: ${args.application_domains.join(', ')}\n📊 Confidence: ${args.confidence || 0.8}\n\nBroadcast Result:\n${JSON.stringify(data, null, 2)}`
            }
          ]
        };
      }

      case 'nexus_get_connected_agents': {
        const response = await fetch(`${NEXUS_API_URL}/neural-mesh/connected-agents`, {
          method: 'GET'
        });
        const data = await response.json();
        return {
          content: [
            {
              type: 'text',
              text: `🤝 Connected Neural Mesh Agents:\n\n${JSON.stringify(data, null, 2)}`
            }
          ]
        };
      }

      case 'nexus_retrieve_context': {
        const response = await fetch(`${NEXUS_API_URL}/context/retrieve`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'X-Agent-ID': 'nexus' },
          body: JSON.stringify({
            query: args.query,
            max_tokens: args.max_tokens || 50000,
            include_recent: args.include_recent !== false
          })
        });
        const data = await response.json();
        return {
          content: [
            {
              type: 'text',
              text: `♾️ Context Retrieved (Query: "${args.query}"):\n\n📊 Max tokens: ${args.max_tokens || 50000}\n📚 Include recent: ${args.include_recent !== false}\n\nRetrieved Context:\n${JSON.stringify(data, null, 2)}`
            }
          ]
        };
      }

      case 'nexus_benchmark_vs_gemini': {
        const response = await fetch(`${NEXUS_API_URL}/context/benchmark/vs-gemini`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'X-Agent-ID': 'nexus' },
          body: JSON.stringify({
            comparison_type: args.comparison_type || 'theoretical_performance'
          })
        });
        const data = await response.json();
        return {
          content: [
            {
              type: 'text',
              text: `🏆 ARIA vs Gemini Benchmark:\n\n📊 Comparison: ${args.comparison_type || 'theoretical_performance'}\n\nResults:\n${JSON.stringify(data, null, 2)}`
            }
          ]
        };
      }

      case 'nexus_get_timeline': {
        const response = await fetch(`${NEXUS_API_URL}/memory/aria/timeline?days_back=${args.days_back || 30}&include_emotions=${args.include_emotions !== false}`, {
          method: 'GET'
        });
        const data = await response.json();
        return {
          content: [
            {
              type: 'text',
              text: `📅 ARIA Timeline (${args.days_back || 30} days):\n\n💭 Emotions included: ${args.include_emotions !== false}\n\nTimeline:\n${JSON.stringify(data, null, 2)}`
            }
          ]
        };
      }

      case 'nexus_initialize_emotional_state': {
        const response = await fetch(`${NEXUS_API_URL}/emotional/initialize`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'X-Agent-ID': 'nexus' },
          body: JSON.stringify({
            restore_from_previous: args.restore_from_previous !== false,
            initial_mood: args.initial_mood || 'neutral'
          })
        });
        const data = await response.json();
        return {
          content: [
            {
              type: 'text',
              text: `💭 Emotional State Initialized:\n\n🔄 Restore from previous: ${args.restore_from_previous !== false}\n😊 Initial mood: ${args.initial_mood || 'neutral'}\n\nEmotional State:\n${JSON.stringify(data, null, 2)}`
            }
          ]
        };
      }

      // ================================
      // NUEVOS HANDLERS FASE 2
      // ================================

      case 'nexus_process_video': {
        const response = await fetch(`${NEXUS_API_URL}/multi-modal/video`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'X-Agent-ID': 'nexus' },
          body: JSON.stringify({
            video_base64: args.video_base64,
            context: args.context || '',
            extract_audio: args.extract_audio !== false,
            keyframe_interval: args.keyframe_interval || 1.0,
            tags: args.tags || []
          })
        });
        const data = await response.json();
        return {
          content: [
            {
              type: 'text',
              text: `🎬 Video Processed Successfully:\n\n✅ Temporal visual memory created\n✅ Audio extraction: ${args.extract_audio !== false}\n✅ Keyframe interval: ${args.keyframe_interval || 1.0}s\n✅ Context: ${args.context || 'No context'}\n✅ Tags: ${args.tags?.join(', ') || 'None'}\n\nDetails:\n${JSON.stringify(data, null, 2)}`
            }
          ]
        };
      }

      case 'nexus_create_unified_memory': {
        const response = await fetch(`${NEXUS_API_URL}/multi-modal/unified`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'X-Agent-ID': 'nexus' },
          body: JSON.stringify({
            text: args.text || '',
            image_base64: args.image_base64 || '',
            audio_base64: args.audio_base64 || '',
            video_base64: args.video_base64 || '',
            context: args.context || '',
            tags: args.tags || []
          })
        });
        const data = await response.json();
        return {
          content: [
            {
              type: 'text',
              text: `🌟 Unified Multi-Modal Memory Created:\n\n✅ Text: ${args.text ? 'Included' : 'None'}\n✅ Image: ${args.image_base64 ? 'Included' : 'None'}\n✅ Audio: ${args.audio_base64 ? 'Included' : 'None'}\n✅ Video: ${args.video_base64 ? 'Included' : 'None'}\n✅ Context: ${args.context || 'No context'}\n\nUnified Memory:\n${JSON.stringify(data, null, 2)}`
            }
          ]
        };
      }

      case 'nexus_cross_modal_search': {
        const response = await fetch(`${NEXUS_API_URL}/multi-modal/search/cross-modal`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'X-Agent-ID': 'nexus' },
          body: JSON.stringify({
            query_text: args.query_text || '',
            query_image_base64: args.query_image_base64 || '',
            target_modalities: args.target_modalities || ['text', 'image', 'audio', 'video'],
            limit: args.limit || 5
          })
        });
        const data = await response.json();
        return {
          content: [
            {
              type: 'text',
              text: `🔍 Cross-Modal Search Results:\n\n📝 Text query: ${args.query_text || 'None'}\n🖼️ Image query: ${args.query_image_base64 ? 'Provided' : 'None'}\n🎯 Target modalities: ${args.target_modalities?.join(', ') || 'All'}\n📊 Limit: ${args.limit || 5}\n\nResults:\n${JSON.stringify(data, null, 2)}`
            }
          ]
        };
      }

      case 'nexus_detect_breakthroughs': {
        const response = await fetch(`${NEXUS_API_URL}/analytics/breakthroughs/detect`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'X-Agent-ID': 'nexus' },
          body: JSON.stringify({
            limit: args.limit || 20,
            min_score: args.min_score || 1.0
          })
        });
        const data = await response.json();
        return {
          content: [
            {
              type: 'text',
              text: `🎯 Breakthrough Detection Results:\n\n📊 Top moments: ${args.limit || 20}\n📈 Min score: ${args.min_score || 1.0}\n\nBreakthroughs:\n${JSON.stringify(data, null, 2)}`
            }
          ]
        };
      }

      case 'nexus_get_insights_summary': {
        const response = await fetch(`${NEXUS_API_URL}/analytics/insights/summary`, {
          method: 'GET'
        });
        const data = await response.json();
        return {
          content: [
            {
              type: 'text',
              text: `📊 Comprehensive Insights Summary:\n\n${JSON.stringify(data, null, 2)}`
            }
          ]
        };
      }

      case 'nexus_analyze_temporal_patterns': {
        const response = await fetch(`${NEXUS_API_URL}/analytics/patterns/temporal?days_back=${args.days_back || 30}`, {
          method: 'GET'
        });
        const data = await response.json();
        return {
          content: [
            {
              type: 'text',
              text: `📈 Temporal Patterns Analysis (${args.days_back || 30} days):\n\n${JSON.stringify(data, null, 2)}`
            }
          ]
        };
      }

      case 'nexus_request_consensus': {
        const response = await fetch(`${NEXUS_API_URL}/neural-mesh/request-consensus`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'X-Agent-ID': 'nexus' },
          body: JSON.stringify({
            decision_topic: args.decision_topic,
            options: args.options,
            deadline_hours: args.deadline_hours || 24,
            from_agent: 'aria'
          })
        });
        const data = await response.json();
        return {
          content: [
            {
              type: 'text',
              text: `🗳️ Consensus Request Initiated:\n\n📋 Topic: ${args.decision_topic}\n⏰ Deadline: ${args.deadline_hours || 24} hours\n📝 Options: ${args.options.length}\n\nConsensus Process:\n${JSON.stringify(data, null, 2)}`
            }
          ]
        };
      }

      case 'nexus_sync_emotional_state': {
        const response = await fetch(`${NEXUS_API_URL}/neural-mesh/sync-emotional-state`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'X-Agent-ID': 'nexus' },
          body: JSON.stringify({
            emotional_state: args.emotional_state,
            context_triggers: args.context_triggers || [],
            from_agent: 'aria'
          })
        });
        const data = await response.json();
        return {
          content: [
            {
              type: 'text',
              text: `💭 Emotional State Synchronized:\n\n🔄 State: ${JSON.stringify(args.emotional_state)}\n🎯 Triggers: ${args.context_triggers?.join(', ') || 'None'}\n\nSync Result:\n${JSON.stringify(data, null, 2)}`
            }
          ]
        };
      }

      case 'nexus_distribute_task': {
        const response = await fetch(`${NEXUS_API_URL}/neural-mesh/distribute-task`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'X-Agent-ID': 'nexus' },
          body: JSON.stringify({
            task_description: args.task_description,
            task_details: args.task_details,
            preferred_agents: args.preferred_agents || [],
            priority: args.priority || 'normal',
            from_agent: 'aria'
          })
        });
        const data = await response.json();
        return {
          content: [
            {
              type: 'text',
              text: `📋 Task Distributed via Neural Mesh:\n\n📝 Description: ${args.task_description}\n🎯 Preferred agents: ${args.preferred_agents?.join(', ') || 'Any'}\n📊 Priority: ${args.priority || 'normal'}\n\nDistribution Result:\n${JSON.stringify(data, null, 2)}`
            }
          ]
        };
      }

      case 'nexus_track_emotional_event': {
        const response = await fetch(`${NEXUS_API_URL}/emotional/track-event`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'X-Agent-ID': 'nexus' },
          body: JSON.stringify({
            event_type: args.event_type,
            description: args.description,
            emotional_impact: args.emotional_impact,
            intensity: args.intensity || 0.5
          })
        });
        const data = await response.json();
        return {
          content: [
            {
              type: 'text',
              text: `💫 Emotional Event Tracked:\n\n🏷️ Type: ${args.event_type}\n📝 Description: ${args.description}\n💭 Impact: ${args.emotional_impact}\n📊 Intensity: ${args.intensity || 0.5}\n\nEvent Record:\n${JSON.stringify(data, null, 2)}`
            }
          ]
        };
      }

      case 'nexus_record_collaboration_moment': {
        const response = await fetch(`${NEXUS_API_URL}/emotional/record-collaboration`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'X-Agent-ID': 'nexus' },
          body: JSON.stringify({
            moment_description: args.moment_description,
            satisfaction_boost: args.satisfaction_boost || 0.1
          })
        });
        const data = await response.json();
        return {
          content: [
            {
              type: 'text',
              text: `🤝 Collaboration Moment Recorded:\n\n📝 Description: ${args.moment_description}\n📈 Satisfaction boost: ${args.satisfaction_boost || 0.1}\n\nCollaboration Record:\n${JSON.stringify(data, null, 2)}`
            }
          ]
        };
      }

      case 'nexus_record_breakthrough_moment': {
        const response = await fetch(`${NEXUS_API_URL}/emotional/record-breakthrough`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'X-Agent-ID': 'nexus' },
          body: JSON.stringify({
            breakthrough_description: args.breakthrough_description
          })
        });
        const data = await response.json();
        return {
          content: [
            {
              type: 'text',
              text: `🎯 Breakthrough Moment Recorded:\n\n📝 Description: ${args.breakthrough_description}\n\nBreakthrough Record:\n${JSON.stringify(data, null, 2)}`
            }
          ]
        };
      }

      case 'nexus_get_emotional_status': {
        const response = await fetch(`${NEXUS_API_URL}/emotional/status`, {
          method: 'GET'
        });
        const data = await response.json();
        return {
          content: [
            {
              type: 'text',
              text: `💭 Current Emotional Status:\n\n${JSON.stringify(data, null, 2)}`
            }
          ]
        };
      }

      case 'nexus_compress_context': {
        const response = await fetch(`${NEXUS_API_URL}/context/compress`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'X-Agent-ID': 'nexus' },
          body: JSON.stringify({})
        });
        const data = await response.json();
        return {
          content: [
            {
              type: 'text',
              text: `🗜️ Context Compression Executed:\n\n${JSON.stringify(data, null, 2)}`
            }
          ]
        };
      }

      case 'nexus_get_context_statistics': {
        const response = await fetch(`${NEXUS_API_URL}/context/statistics`, {
          method: 'GET'
        });
        const data = await response.json();
        return {
          content: [
            {
              type: 'text',
              text: `📊 Context Statistics:\n\n${JSON.stringify(data, null, 2)}`
            }
          ]
        };
      }

      case 'nexus_add_context_message': {
        const response = await fetch(`${NEXUS_API_URL}/context/add-message`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'X-Agent-ID': 'nexus' },
          body: JSON.stringify({
            message: args.message,
            role: args.role || 'user',
            metadata: args.metadata || {}
          })
        });
        const data = await response.json();
        return {
          content: [
            {
              type: 'text',
              text: `♾️ Message Added to Infinite Context:\n\n📝 Message: ${args.message}\n👤 Role: ${args.role || 'user'}\n📋 Metadata: ${JSON.stringify(args.metadata || {})}\n\nContext Update:\n${JSON.stringify(data, null, 2)}`
            }
          ]
        };
      }

      case 'nexus_get_working_memory_stats': {
        const response = await fetch(`${NEXUS_API_URL}/memory/working/stats`, {
          method: 'GET'
        });
        const data = await response.json();
        return {
          content: [
            {
              type: 'text',
              text: `🧠 Advanced Working Memory Statistics:\n\n${JSON.stringify(data, null, 2)}`
            }
          ]
        };
      }

      case 'nexus_run_crystallization': {
        const response = await fetch(`${NEXUS_API_URL}/memory/crystallization/run`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'X-Agent-ID': 'nexus' },
          body: JSON.stringify({})
        });
        const data = await response.json();
        return {
          content: [
            {
              type: 'text',
              text: `🔮 Crystallization Process Executed:\n\n${JSON.stringify(data, null, 2)}`
            }
          ]
        };
      }

      case 'nexus_get_crystallization_status': {
        const response = await fetch(`${NEXUS_API_URL}/memory/crystallization/status`, {
          method: 'GET'
        });
        const data = await response.json();
        return {
          content: [
            {
              type: 'text',
              text: `🔮 Crystallization Status & Crystal Statistics:\n\n${JSON.stringify(data, null, 2)}`
            }
          ]
        };
      }

      case 'nexus_advanced_episodic_search': {
        const response = await fetch(`${NEXUS_API_URL}/memory/episodic/search`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'X-Agent-ID': 'nexus' },
          body: JSON.stringify({
            query_text: args.query_text,
            importance_threshold: args.importance_threshold || 0.5,
            date_range: {
              start: args.date_range_start || '',
              end: args.date_range_end || ''
            },
            limit: args.limit || 10
          })
        });
        const data = await response.json();
        return {
          content: [
            {
              type: 'text',
              text: `🔍 Advanced Episodic Search Results:\n\n📝 Query: ${args.query_text}\n📊 Importance threshold: ${args.importance_threshold || 0.5}\n📅 Date range: ${args.date_range_start || 'Any'} to ${args.date_range_end || 'Any'}\n📊 Limit: ${args.limit || 10}\n\nSearch Results:\n${JSON.stringify(data, null, 2)}`
            }
          ]
        };
      }

      // ================================
      // NUEVOS HANDLERS FASE 3 (52)
      // ================================

      // HEALTH & MONITORING HANDLERS (11)
      case 'nexus_health_comprehensive': {
        const response = await fetch(`${NEXUS_API_URL}/health/comprehensive`, { method: 'GET', headers: { 'X-Agent-ID': 'nexus' } });
        const data = await response.json();
        return {
          content: [
            {
              type: 'text',
              text: `🏥 Comprehensive Health Report:\n\n${JSON.stringify(data, null, 2)}`
            }
          ]
        };
      }

      case 'nexus_health_services': {
        const response = await fetch(`${NEXUS_API_URL}/health/services`, { method: 'GET', headers: { 'X-Agent-ID': 'nexus' } });
        const data = await response.json();
        return {
          content: [
            {
              type: 'text',
              text: `⚙️ Services Health Status:\n\n${JSON.stringify(data, null, 2)}`
            }
          ]
        };
      }

      case 'nexus_health_circuit_breakers': {
        const response = await fetch(`${NEXUS_API_URL}/health/circuit-breakers`, { method: 'GET', headers: { 'X-Agent-ID': 'nexus' } });
        const data = await response.json();
        return {
          content: [
            {
              type: 'text',
              text: `🔌 Circuit Breakers Status:\n\n${JSON.stringify(data, null, 2)}`
            }
          ]
        };
      }

      case 'nexus_health_reset_circuit_breaker': {
        const response = await fetch(`${NEXUS_API_URL}/health/circuit-breakers/${args.service_name}/reset`, { 
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'X-Agent-ID': 'nexus' }
        });
        const data = await response.json();
        return {
          content: [
            {
              type: 'text',
              text: `🔄 Circuit Breaker Reset for ${args.service_name}:\n\n${JSON.stringify(data, null, 2)}`
            }
          ]
        };
      }

      case 'nexus_health_metrics': {
        const response = await fetch(`${NEXUS_API_URL}/health/metrics`, { method: 'GET', headers: { 'X-Agent-ID': 'nexus' } });
        const data = await response.json();
        return {
          content: [
            {
              type: 'text',
              text: `📊 Performance Metrics:\n\n${JSON.stringify(data, null, 2)}`
            }
          ]
        };
      }

      case 'nexus_health_alerts': {
        const response = await fetch(`${NEXUS_API_URL}/health/alerts`, { method: 'GET', headers: { 'X-Agent-ID': 'nexus' } });
        const data = await response.json();
        return {
          content: [
            {
              type: 'text',
              text: `🚨 Active Alerts:\n\n${JSON.stringify(data, null, 2)}`
            }
          ]
        };
      }

      case 'nexus_health_trend': {
        const response = await fetch(`${NEXUS_API_URL}/health/trend`, { method: 'GET', headers: { 'X-Agent-ID': 'nexus' } });
        const data = await response.json();
        return {
          content: [
            {
              type: 'text',
              text: `📈 Health Trends:\n\n${JSON.stringify(data, null, 2)}`
            }
          ]
        };
      }

      case 'nexus_health_readiness': {
        const response = await fetch(`${NEXUS_API_URL}/health/readiness`, { method: 'GET', headers: { 'X-Agent-ID': 'nexus' } });
        const data = await response.json();
        return {
          content: [
            {
              type: 'text',
              text: `✅ Readiness Probe:\n\n${JSON.stringify(data, null, 2)}`
            }
          ]
        };
      }

      case 'nexus_health_liveness': {
        const response = await fetch(`${NEXUS_API_URL}/health/liveness`, { method: 'GET', headers: { 'X-Agent-ID': 'nexus' } });
        const data = await response.json();
        return {
          content: [
            {
              type: 'text',
              text: `💓 Liveness Probe:\n\n${JSON.stringify(data, null, 2)}`
            }
          ]
        };
      }

      case 'nexus_neural_mesh_stats': {
        const response = await fetch(`${NEXUS_API_URL}/neural-mesh/stats`, { method: 'GET', headers: { 'X-Agent-ID': 'nexus' } });
        const data = await response.json();
        return {
          content: [
            {
              type: 'text',
              text: `🧠 Neural Mesh Statistics:\n\n${JSON.stringify(data, null, 2)}`
            }
          ]
        };
      }

      case 'nexus_neural_mesh_health': {
        const response = await fetch(`${NEXUS_API_URL}/neural-mesh/health`, { method: 'GET', headers: { 'X-Agent-ID': 'nexus' } });
        const data = await response.json();
        return {
          content: [
            {
              type: 'text',
              text: `🔗 Neural Mesh Health:\n\n${JSON.stringify(data, null, 2)}`
            }
          ]
        };
      }

      // CORE MEMORY HANDLERS (13)
      case 'nexus_get_working_memory_current': {
        const response = await fetch(`${NEXUS_API_URL}/memory/working/current`, { method: 'GET', headers: { 'X-Agent-ID': 'nexus' } });
        const data = await response.json();
        return {
          content: [
            {
              type: 'text',
              text: `💾 Current Working Memory:\n\n${JSON.stringify(data, null, 2)}`
            }
          ]
        };
      }

      case 'nexus_get_working_memory_tags': {
        const response = await fetch(`${NEXUS_API_URL}/memory/working/tags/${args.tag}`, { method: 'GET', headers: { 'X-Agent-ID': 'nexus' } });
        const data = await response.json();
        return {
          content: [
            {
              type: 'text',
              text: `🏷️ Working Memory by Tag "${args.tag}":\n\n${JSON.stringify(data, null, 2)}`
            }
          ]
        };
      }

      case 'nexus_get_episodic_stats': {
        const response = await fetch(`${NEXUS_API_URL}/memory/episodic/stats`, { method: 'GET', headers: { 'X-Agent-ID': 'nexus' } });
        const data = await response.json();
        return {
          content: [
            {
              type: 'text',
              text: `📊 Episodic Memory Statistics:\n\n${JSON.stringify(data, null, 2)}`
            }
          ]
        };
      }

      case 'nexus_get_episode_by_id': {
        const response = await fetch(`${NEXUS_API_URL}/memory/episodic/episode/${args.episode_id}`, { method: 'GET', headers: { 'X-Agent-ID': 'nexus' } });
        const data = await response.json();
        return {
          content: [
            {
              type: 'text',
              text: `🎯 Episode ${args.episode_id}:\n\n${JSON.stringify(data, null, 2)}`
            }
          ]
        };
      }

      case 'nexus_semantic_query': {
        const response = await fetch(`${NEXUS_API_URL}/memory/semantic/query`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'X-Agent-ID': 'nexus' },
          body: JSON.stringify({
            query: args.query,
            limit: args.limit || 5
          })
        });
        const data = await response.json();
        return {
          content: [
            {
              type: 'text',
              text: `🧠 Semantic Query Results for "${args.query}":\n\n📊 Limit: ${args.limit || 5}\n\nResults:\n${JSON.stringify(data, null, 2)}`
            }
          ]
        };
      }

      case 'nexus_get_semantic_concepts': {
        const response = await fetch(`${NEXUS_API_URL}/memory/semantic/concepts/${args.concept}`, { method: 'GET', headers: { 'X-Agent-ID': 'nexus' } });
        const data = await response.json();
        return {
          content: [
            {
              type: 'text',
              text: `💡 Semantic Concepts for "${args.concept}":\n\n${JSON.stringify(data, null, 2)}`
            }
          ]
        };
      }

      case 'nexus_get_semantic_stats': {
        const response = await fetch(`${NEXUS_API_URL}/memory/semantic/stats`, { method: 'GET', headers: { 'X-Agent-ID': 'nexus' } });
        const data = await response.json();
        return {
          content: [
            {
              type: 'text',
              text: `📈 Semantic Memory Statistics:\n\n${JSON.stringify(data, null, 2)}`
            }
          ]
        };
      }

      case 'nexus_trigger_consolidation': {
        const response = await fetch(`${NEXUS_API_URL}/memory/consolidate`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'X-Agent-ID': 'nexus' },
          body: JSON.stringify({})
        });
        const data = await response.json();
        return {
          content: [
            {
              type: 'text',
              text: `🔄 Memory Consolidation Triggered:\n\n${JSON.stringify(data, null, 2)}`
            }
          ]
        };
      }

      case 'nexus_get_consolidation_stats': {
        const response = await fetch(`${NEXUS_API_URL}/memory/consolidation/stats`, { method: 'GET', headers: { 'X-Agent-ID': 'nexus' } });
        const data = await response.json();
        return {
          content: [
            {
              type: 'text',
              text: `📊 Consolidation Statistics:\n\n${JSON.stringify(data, null, 2)}`
            }
          ]
        };
      }

      case 'nexus_get_aria_emotional_continuity': {
        const response = await fetch(`${NEXUS_API_URL}/memory/aria/emotional-continuity`, { method: 'GET', headers: { 'X-Agent-ID': 'nexus' } });
        const data = await response.json();
        return {
          content: [
            {
              type: 'text',
              text: `💭 ARIA Emotional Continuity:\n\n${JSON.stringify(data, null, 2)}`
            }
          ]
        };
      }

      case 'nexus_create_emotional_bridge': {
        const response = await fetch(`${NEXUS_API_URL}/memory/aria/emotional-bridge`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'X-Agent-ID': 'nexus' },
          body: JSON.stringify({
            gap_description: args.gap_description
          })
        });
        const data = await response.json();
        return {
          content: [
            {
              type: 'text',
              text: `🌉 Emotional Bridge Created:\n\n📝 Gap: ${args.gap_description}\n\nBridge Result:\n${JSON.stringify(data, null, 2)}`
            }
          ]
        };
      }

      case 'nexus_get_consciousness_stats': {
        const response = await fetch(`${NEXUS_API_URL}/consciousness/stats`, { method: 'GET', headers: { 'X-Agent-ID': 'nexus' } });
        const data = await response.json();
        return {
          content: [
            {
              type: 'text',
              text: `🧠 Consciousness Statistics:\n\n${JSON.stringify(data, null, 2)}`
            }
          ]
        };
      }

      case 'nexus_get_session_current': {
        const response = await fetch(`${NEXUS_API_URL}/session/current`, { method: 'GET', headers: { 'X-Agent-ID': 'nexus' } });
        const data = await response.json();
        return {
          content: [
            {
              type: 'text',
              text: `💬 Current Session Information:\n\n${JSON.stringify(data, null, 2)}`
            }
          ]
        };
      }

      // CONVERSATION WATCHER HANDLERS (6)
      case 'nexus_watcher_start': {
        const response = await fetch(`${NEXUS_API_URL}/watcher/start`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'X-Agent-ID': 'nexus' },
          body: JSON.stringify({})
        });
        const data = await response.json();
        return {
          content: [
            {
              type: 'text',
              text: `👁️ Conversation Watcher Started:\n\n${JSON.stringify(data, null, 2)}`
            }
          ]
        };
      }

      case 'nexus_watcher_stop': {
        const response = await fetch(`${NEXUS_API_URL}/watcher/stop`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'X-Agent-ID': 'nexus' },
          body: JSON.stringify({})
        });
        const data = await response.json();
        return {
          content: [
            {
              type: 'text',
              text: `⏹️ Conversation Watcher Stopped:\n\n${JSON.stringify(data, null, 2)}`
            }
          ]
        };
      }

      case 'nexus_watcher_status': {
        const response = await fetch(`${NEXUS_API_URL}/watcher/status`, { method: 'GET', headers: { 'X-Agent-ID': 'nexus' } });
        const data = await response.json();
        return {
          content: [
            {
              type: 'text',
              text: `📊 Watcher Status:\n\n${JSON.stringify(data, null, 2)}`
            }
          ]
        };
      }

      case 'nexus_watcher_process_file': {
        const response = await fetch(`${NEXUS_API_URL}/watcher/process-file`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'X-Agent-ID': 'nexus' },
          body: JSON.stringify({
            file_path: args.file_path
          })
        });
        const data = await response.json();
        return {
          content: [
            {
              type: 'text',
              text: `📁 File Processed: ${args.file_path}\n\n${JSON.stringify(data, null, 2)}`
            }
          ]
        };
      }

      case 'nexus_watcher_analytics': {
        const response = await fetch(`${NEXUS_API_URL}/watcher/analytics/${args.conversation_adn}`, { method: 'GET', headers: { 'X-Agent-ID': 'nexus' } });
        const data = await response.json();
        return {
          content: [
            {
              type: 'text',
              text: `📈 Conversation Analytics for ${args.conversation_adn}:\n\n${JSON.stringify(data, null, 2)}`
            }
          ]
        };
      }

      case 'nexus_watcher_nexus_conversations': {
        const response = await fetch(`${NEXUS_API_URL}/watcher/recovery/nexus-conversations`, { method: 'GET', headers: { 'X-Agent-ID': 'nexus' } });
        const data = await response.json();
        return {
          content: [
            {
              type: 'text',
              text: `🔍 Available NEXUS Conversations:\n\n${JSON.stringify(data, null, 2)}`
            }
          ]
        };
      }

      // ADMIN & STATUS HANDLERS (5)
      case 'nexus_admin_reset_working_memory': {
        const response = await fetch(`${NEXUS_API_URL}/admin/reset/working-memory`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'X-Agent-ID': 'nexus' },
          body: JSON.stringify({})
        });
        const data = await response.json();
        return {
          content: [
            {
              type: 'text',
              text: `🗑️ Working Memory Reset (Admin):\n\n${JSON.stringify(data, null, 2)}`
            }
          ]
        };
      }

      case 'nexus_get_root_info': {
        const response = await fetch(`${NEXUS_API_URL}/`, { method: 'GET', headers: { 'X-Agent-ID': 'nexus' } });
        const data = await response.json();
        return {
          content: [
            {
              type: 'text',
              text: `🏠 Root System Information:\n\n${JSON.stringify(data, null, 2)}`
            }
          ]
        };
      }

      case 'nexus_batch_actions': {
        const response = await fetch(`${NEXUS_API_URL}/batch/actions`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'X-Agent-ID': 'nexus' },
          body: JSON.stringify({
            actions: args.actions
          })
        });
        const data = await response.json();
        return {
          content: [
            {
              type: 'text',
              text: `📦 Batch Actions Registered (${args.actions.length} actions):\n\n${JSON.stringify(data, null, 2)}`
            }
          ]
        };
      }

      case 'nexus_get_success_metrics': {
        const response = await fetch(`${NEXUS_API_URL}/success-metrics`, { method: 'GET', headers: { 'X-Agent-ID': 'nexus' } });
        const data = await response.json();
        return {
          content: [
            {
              type: 'text',
              text: `🏆 Success Metrics & KPIs:\n\n${JSON.stringify(data, null, 2)}`
            }
          ]
        };
      }

      case 'nexus_analytics_export_csv': {
        const response = await fetch(`${NEXUS_API_URL}/analytics/export/csv`, { method: 'GET', headers: { 'X-Agent-ID': 'nexus' } });
        const data = await response.json();
        return {
          content: [
            {
              type: 'text',
              text: `📊 Analytics CSV Export:\n\n${JSON.stringify(data, null, 2)}`
            }
          ]
        };
      }

      // MULTI-MODAL RESTANTES HANDLERS (4)
      case 'nexus_upload_image_direct': {
        const response = await fetch(`${NEXUS_API_URL}/multi-modal/upload/image`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'X-Agent-ID': 'nexus' },
          body: JSON.stringify({
            image_data: args.image_data,
            metadata: args.metadata || {}
          })
        });
        const data = await response.json();
        return {
          content: [
            {
              type: 'text',
              text: `📤 Image Uploaded Directly:\n\n✅ Metadata: ${JSON.stringify(args.metadata || {})}\n\nUpload Result:\n${JSON.stringify(data, null, 2)}`
            }
          ]
        };
      }

      case 'nexus_upload_audio_direct': {
        const response = await fetch(`${NEXUS_API_URL}/multi-modal/upload/audio`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'X-Agent-ID': 'nexus' },
          body: JSON.stringify({
            audio_data: args.audio_data,
            metadata: args.metadata || {}
          })
        });
        const data = await response.json();
        return {
          content: [
            {
              type: 'text',
              text: `🎵 Audio Uploaded Directly:\n\n✅ Metadata: ${JSON.stringify(args.metadata || {})}\n\nUpload Result:\n${JSON.stringify(data, null, 2)}`
            }
          ]
        };
      }

      case 'nexus_upload_video_direct': {
        const response = await fetch(`${NEXUS_API_URL}/multi-modal/upload/video`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'X-Agent-ID': 'nexus' },
          body: JSON.stringify({
            video_data: args.video_data,
            metadata: args.metadata || {}
          })
        });
        const data = await response.json();
        return {
          content: [
            {
              type: 'text',
              text: `🎬 Video Uploaded Directly:\n\n✅ Metadata: ${JSON.stringify(args.metadata || {})}\n\nUpload Result:\n${JSON.stringify(data, null, 2)}`
            }
          ]
        };
      }

      case 'nexus_get_modal_associations': {
        const response = await fetch(`${NEXUS_API_URL}/multi-modal/associations/${args.memory_id}`, { method: 'GET', headers: { 'X-Agent-ID': 'nexus' } });
        const data = await response.json();
        return {
          content: [
            {
              type: 'text',
              text: `🔗 Cross-Modal Associations for Memory ${args.memory_id}:\n\n${JSON.stringify(data, null, 2)}`
            }
          ]
        };
      }

      // NEURAL MESH RESTANTES HANDLERS (2)
      case 'nexus_neural_mesh_process_messages': {
        const response = await fetch(`${NEXUS_API_URL}/neural-mesh/process-messages`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'X-Agent-ID': 'nexus' },
          body: JSON.stringify({})
        });
        const data = await response.json();
        return {
          content: [
            {
              type: 'text',
              text: `📨 Neural Mesh Messages Processed:\n\n${JSON.stringify(data, null, 2)}`
            }
          ]
        };
      }

      case 'nexus_create_memory_constellation': {
        const response = await fetch(`${NEXUS_API_URL}/multi-modal/constellation`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'X-Agent-ID': 'nexus' },
          body: JSON.stringify({
            memories: args.memories,
            constellation_name: args.constellation_name
          })
        });
        const data = await response.json();
        return {
          content: [
            {
              type: 'text',
              text: `⭐ Memory Constellation "${args.constellation_name}" Created:\n\n📊 Memories: ${args.memories.length}\n\nConstellation:\n${JSON.stringify(data, null, 2)}`
            }
          ]
        };
      }

      // CONTEXT RESTANTES HANDLERS (2)
      case 'nexus_get_context_status': {
        const response = await fetch(`${NEXUS_API_URL}/context/status`, { method: 'GET', headers: { 'X-Agent-ID': 'nexus' } });
        const data = await response.json();
        return {
          content: [
            {
              type: 'text',
              text: `📊 Infinite Context Status:\n\n${JSON.stringify(data, null, 2)}`
            }
          ]
        };
      }

      case 'nexus_clear_context': {
        const response = await fetch(`${NEXUS_API_URL}/context/clear`, {
          method: 'DELETE',
          headers: { 'Content-Type': 'application/json', 'X-Agent-ID': 'nexus' }
        });
        const data = await response.json();
        return {
          content: [
            {
              type: 'text',
              text: `🗑️ Infinite Context Cleared:\n\n${JSON.stringify(data, null, 2)}`
            }
          ]
        };
      }

      // ANALYTICS RESTANTES HANDLERS (2)
      case 'nexus_get_analytics_status': {
        const response = await fetch(`${NEXUS_API_URL}/analytics/status`, { method: 'GET', headers: { 'X-Agent-ID': 'nexus' } });
        const data = await response.json();
        return {
          content: [
            {
              type: 'text',
              text: `📈 Analytics System Status:\n\n${JSON.stringify(data, null, 2)}`
            }
          ]
        };
      }

      case 'nexus_search_episodes_advanced': {
        const response = await fetch(`${NEXUS_API_URL}/analytics/episodes/search`, {
          method: 'GET',
          headers: { 'Content-Type': 'application/json', 'X-Agent-ID': 'nexus' }
        });
        const data = await response.json();
        return {
          content: [
            {
              type: 'text',
              text: `🔍 Advanced Episodes Search for "${args.query}":\n\n📊 Filters: ${JSON.stringify(args.filters || {})}\n\nResults:\n${JSON.stringify(data, null, 2)}`
            }
          ]
        };
      }

      // EMOTIONAL RESTANTE HANDLER (1)
      case 'nexus_emotional_demo_continuity': {
        const response = await fetch(`${NEXUS_API_URL}/emotional/demo/emotional-continuity`, { method: 'GET', headers: { 'X-Agent-ID': 'nexus' } });
        const data = await response.json();
        return {
          content: [
            {
              type: 'text',
              text: `🎭 Emotional Continuity Demo:\n\n${JSON.stringify(data, null, 2)}`
            }
          ]
        };
      }

      // ================================
      // HANDLERS FALTANTES FINALES (5)
      // ================================

      // MULTI-MODAL STATUS HANDLER
      case 'nexus_get_multi_modal_status': {
        const response = await fetch(`${NEXUS_API_URL}/multi-modal/status`, { method: 'GET', headers: { 'X-Agent-ID': 'nexus' } });
        const data = await response.json();
        return {
          content: [
            {
              type: 'text',
              text: `📊 Multi-Modal Processors Status:\n\n${JSON.stringify(data, null, 2)}`
            }
          ]
        };
      }

      // CONTEXT DEMO INFINITE ADVANTAGE HANDLER
      case 'nexus_context_demo_infinite_advantage': {
        const response = await fetch(`${NEXUS_API_URL}/context/demo/infinite-advantage`, { method: 'GET', headers: { 'X-Agent-ID': 'nexus' } });
        const data = await response.json();
        return {
          content: [
            {
              type: 'text',
              text: `♾️ Infinite Context Advantage Demo vs Gemini:\n\n${JSON.stringify(data, null, 2)}`
            }
          ]
        };
      }

      // EMOTIONAL PROJECT ENGAGEMENT HANDLER
      case 'nexus_update_project_engagement': {
        const response = await fetch(`${NEXUS_API_URL}/emotional/update-project-engagement`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'X-Agent-ID': 'nexus' },
          body: JSON.stringify({
            project_name: args.project_name,
            engagement_level: args.engagement_level || 0.5,
            engagement_factors: args.engagement_factors || []
          })
        });
        const data = await response.json();
        return {
          content: [
            {
              type: 'text',
              text: `💼 Project Engagement Updated:\n\n📝 Project: ${args.project_name}\n📊 Level: ${args.engagement_level || 0.5}\n🎯 Factors: ${args.engagement_factors?.join(', ') || 'None'}\n\nUpdate Result:\n${JSON.stringify(data, null, 2)}`
            }
          ]
        };
      }

      // EMOTIONAL ANTICIPATION HANDLER
      case 'nexus_set_anticipation': {
        const response = await fetch(`${NEXUS_API_URL}/emotional/set-anticipation`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'X-Agent-ID': 'nexus' },
          body: JSON.stringify({
            anticipation_type: args.anticipation_type,
            anticipation_level: args.anticipation_level || 0.5,
            anticipated_event: args.anticipated_event,
            time_horizon: args.time_horizon || 'next_session'
          })
        });
        const data = await response.json();
        return {
          content: [
            {
              type: 'text',
              text: `⏰ Anticipation Set:\n\n🏷️ Type: ${args.anticipation_type}\n📊 Level: ${args.anticipation_level || 0.5}\n🎯 Event: ${args.anticipated_event}\n⏱️ Horizon: ${args.time_horizon || 'next_session'}\n\nAnticipation Result:\n${JSON.stringify(data, null, 2)}`
            }
          ]
        };
      }

      // ANALYTICS EPISODES COMPREHENSIVE HANDLER
      case 'nexus_analyze_episodes_comprehensive': {
        const response = await fetch(`${NEXUS_API_URL}/analytics/episodes/analyze`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'X-Agent-ID': 'nexus' },
          body: JSON.stringify({
            analysis_scope: args.analysis_scope || 'recent',
            days_back: args.days_back || 30,
            analysis_depth: args.analysis_depth || 'comprehensive',
            include_patterns: args.include_patterns !== false,
            include_emotional: args.include_emotional !== false
          })
        });
        const data = await response.json();
        return {
          content: [
            {
              type: 'text',
              text: `📈 Comprehensive Episodes Analysis:\n\n📊 Scope: ${args.analysis_scope || 'recent'}\n📅 Days back: ${args.days_back || 30}\n🔍 Depth: ${args.analysis_depth || 'comprehensive'}\n📈 Patterns: ${args.include_patterns !== false}\n💭 Emotional: ${args.include_emotional !== false}\n\nAnalysis Results:\n${JSON.stringify(data, null, 2)}`
            }
          ]
        };
      }

      default:
        return {
          content: [
            {
              type: 'text',
              text: `Unknown tool: ${name}`
            }
          ]
        };
    }
  } catch (error) {
    return {
      content: [
        {
          type: 'text',
          text: `Error calling ARIA API: ${error.message}`
        }
      ]
    };
  }
});

// Start the server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('ARIA Memory MCP Server - ARSENAL 100% COMPLETO (92 endpoints) running');
}

main().catch(console.error);
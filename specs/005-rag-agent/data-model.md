# Data Model: RAG Agent using OpenAI Agents SDK with Gemini model

## Overview
Data model for the Retrieval-Augmented Generation (RAG) Agent that uses OpenAI Agents SDK with a Gemini model and FastAPI integration.

## AgentRequest Entity

### Attributes
- `request_id`: UUID (Primary Key)
  - Unique identifier for each agent request
  - Generated automatically upon creation
- `query_text`: Text
  - The user's main question or query
  - Required
- `selected_text`: Text
  - Optional selected text for focused queries
  - Optional
- `context`: Text
  - Additional context provided with the query
  - Optional
- `user_id`: String
  - Identifier for the user making the request
  - Optional (for tracking purposes)
- `session_id`: String
  - Identifier for the conversation session
  - Optional
- `created_at`: DateTime (UTC)
  - Timestamp when the request was created
  - Required
- `request_metadata`: JSON
  - Additional metadata about the request
  - Optional (e.g., client info, source)

### Relationships
- One-to-One: AgentRequest to AgentResponse
- One-to-Many: AgentRequest to RetrievedContext

## AgentResponse Entity

### Attributes
- `response_id`: UUID (Primary Key)
  - Unique identifier for each agent response
  - Generated automatically upon creation
- `request_id`: UUID (Foreign Key)
  - Reference to the original request
  - Required, indexed, unique
- `answer_text`: Text
  - The agent's generated response
  - Required
- `source_chunks`: Array<String>
  - List of chunk IDs used to generate the answer
  - Required (can be empty if no sources)
- `confidence_score`: Float
  - Confidence score of the response (0.0 to 1.0)
  - Required, default: 0.5
- `response_time_ms`: Integer
  - Time taken to generate the response in milliseconds
  - Required
- `grounding_validated`: Boolean
  - Whether the response was validated against sources
  - Required, default: false
- `citations`: Array<JSON>
  - Citations to source documents
  - Optional (e.g., [{"url": "...", "title": "...", "position": ...}])
- `generated_at`: DateTime (UTC)
  - Timestamp when the response was generated
  - Required
- `response_metadata`: JSON
  - Additional metadata about the response
  - Optional (e.g., model info, tokens used)

### Relationships
- Many-to-One: AgentResponse to AgentRequest
- One-to-Many: AgentResponse to ResponseQualityMetrics

## RetrievedContext Entity

### Attributes
- `context_id`: UUID (Primary Key)
  - Unique identifier for each retrieved context
  - Generated automatically upon creation
- `request_id`: UUID (Foreign Key)
  - Reference to the original request
  - Required, indexed
- `query_text`: Text
  - Original query that triggered the retrieval
  - Required
- `retrieved_chunks`: Array<JSON>
  - List of retrieved chunk objects with metadata
  - Required (e.g., [{"chunk_id": "...", "text": "...", "similarity": ..., "metadata": ...}])
- `retrieval_time_ms`: Integer
  - Time taken for retrieval in milliseconds
  - Required
- `retrieval_params`: JSON
  - Parameters used for the retrieval operation
  - Optional (e.g., {"top_k": 5, "threshold": 0.7})
- `retrieved_at`: DateTime (UTC)
  - Timestamp when context was retrieved
  - Required

### Relationships
- Many-to-One: RetrievedContext to AgentRequest
- One-to-Many: RetrievedContext to RetrievalMetrics

## AgentSession Entity

### Attributes
- `session_id`: UUID (Primary Key)
  - Unique identifier for each agent session
  - Generated automatically upon creation
- `user_id`: String
  - Identifier for the user associated with the session
  - Optional
- `session_start`: DateTime (UTC)
  - When the session started
  - Required
- `session_end`: DateTime (UTC)
  - When the session ended (null if active)
  - Optional
- `query_count`: Integer
  - Number of queries made in this session
  - Required, default: 0
- `is_active`: Boolean
  - Whether the session is currently active
  - Required, default: true
- `session_metadata`: JSON
  - Additional metadata about the session
  - Optional (e.g., device info, session type)

### Relationships
- One-to-Many: AgentSession to AgentRequests
- One-to-Many: AgentSession to SessionMetrics

## ResponseQualityMetrics Entity

### Attributes
- `metric_id`: UUID (Primary Key)
  - Unique identifier for each quality metric record
  - Generated automatically upon creation
- `response_id`: UUID (Foreign Key)
  - Reference to the response being evaluated
  - Required, indexed
- `content_grounding_score`: Float
  - Score measuring how well response is grounded in sources (0.0 to 1.0)
  - Required
- `hallucination_detected`: Boolean
  - Whether hallucinations were detected in the response
  - Required, default: false
- `factual_accuracy_score`: Float
  - Score measuring factual accuracy against sources (0.0 to 1.0)
  - Required
- `relevance_score`: Float
  - Score measuring relevance to the original query (0.0 to 1.0)
  - Required
- `quality_check_timestamp`: DateTime (UTC)
  - When the quality metrics were calculated
  - Required
- `quality_checker`: String
  - Identifier for the quality checking mechanism used
  - Required (e.g., "automated", "manual")

### Relationships
- Many-to-One: ResponseQualityMetrics to AgentResponse

## RetrievalMetrics Entity

### Attributes
- `metric_id`: UUID (Primary Key)
  - Unique identifier for each retrieval metric record
  - Generated automatically upon creation
- `context_id`: UUID (Foreign Key)
  - Reference to the retrieved context
  - Required, indexed
- `retrieval_precision`: Float
  - Precision of the retrieval operation (0.0 to 1.0)
  - Required
- `retrieval_recall`: Float
  - Recall of the retrieval operation (0.0 to 1.0)
  - Required
- `average_similarity`: Float
  - Average similarity score of retrieved chunks
  - Required
- `query_expansion_used`: Boolean
  - Whether query expansion was used during retrieval
  - Required, default: false
- `filtering_applied`: Boolean
  - Whether additional filtering was applied
  - Required, default: false
- `metrics_calculated_at`: DateTime (UTC)
  - When the retrieval metrics were calculated
  - Required

### Relationships
- Many-to-One: RetrievalMetrics to RetrievedContext

## SessionMetrics Entity

### Attributes
- `metric_id`: UUID (Primary Key)
  - Unique identifier for each session metric record
  - Generated automatically upon creation
- `session_id`: UUID (Foreign Key)
  - Reference to the session being measured
  - Required, indexed
- `average_response_time`: Float
  - Average response time for queries in this session
  - Required
- `average_confidence`: Float
  - Average confidence score of responses in this session
  - Required
- `successful_queries`: Integer
  - Number of successful queries in this session
  - Required, default: 0
- `failed_queries`: Integer
  - Number of failed queries in this session
  - Required, default: 0
- `total_tokens_used`: Integer
  - Total tokens used by the LLM in this session
  - Optional
- `metrics_calculated_at`: DateTime (UTC)
  - When the session metrics were calculated
  - Required

### Relationships
- Many-to-One: SessionMetrics to AgentSession

## ConversationTurn Entity

### Attributes
- `turn_id`: UUID (Primary Key)
  - Unique identifier for each conversation turn
  - Generated automatically upon creation
- `session_id`: UUID (Foreign Key)
  - Reference to the session containing this turn
  - Required, indexed
- `turn_number`: Integer
  - Sequential number of this turn in the conversation
  - Required, positive
- `user_query`: Text
  - The user's query in this turn
  - Required
- `agent_response`: Text
  - The agent's response in this turn
  - Required
- `timestamp`: DateTime (UTC)
  - When this turn occurred
  - Required
- `turn_metadata`: JSON
  - Additional metadata for this turn
  - Optional (e.g., sentiment, intent)

### Relationships
- Many-to-One: ConversationTurn to AgentSession

## Constraints and Validation

### AgentRequest Constraints
- `query_text` length must be between 1 and 10000 characters
- `selected_text` length must be between 1 and 5000 characters if provided
- `created_at` must be current or past timestamp
- `session_id` should be valid UUID format if provided

### AgentResponse Constraints
- `confidence_score` must be between 0.0 and 1.0
- `response_time_ms` must be non-negative
- `request_id` must reference an existing AgentRequest
- `response_time_ms` should be reasonable (less than 60000ms)

### RetrievedContext Constraints
- `retrieval_time_ms` must be non-negative
- `retrieved_chunks` array should not exceed 100 elements
- `request_id` must reference an existing AgentRequest

### Quality Metrics Constraints
- All score fields (0.0 to 1.0) must be within range
- `response_id` and `context_id` must reference existing records

## Indexing Strategy

### Primary Indexes
- `request_id` in AgentRequest table
- `response_id` in AgentResponse table
- `context_id` in RetrievedContext table
- `session_id` in AgentSession table

### Secondary Indexes
- `request_id` in AgentResponse (foreign key)
- `request_id` in RetrievedContext (foreign key)
- `session_id` in AgentRequest (for session queries)
- `created_at` in AgentRequest (for time-based queries)
- `session_id` in ConversationTurn (for session queries)

## Performance Considerations

### Partitioning Strategy
- Consider partitioning AgentRequest/Response by date for large datasets
- May partition by session_id for better session-based queries

### Query Optimization
- Index foreign key relationships for join operations
- Consider materialized views for common aggregate queries
- Optimize for time-range queries on requests/responses

## Data Integrity

### Referential Integrity
- Foreign key constraints ensure valid relationships
- Prevent orphaned records
- Cascade operations where appropriate

### Audit Trail
- Created/updated timestamps on all entities
- Track request-response lifecycle
- Maintain conversation history for context
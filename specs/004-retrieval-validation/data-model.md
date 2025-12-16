# Data Model: Retrieval Validation Module

## Overview
Data model for the retrieval validation module that validates semantic search results from Qdrant vector database.

## Query Entity

### Attributes
- `query_id`: UUID (Primary Key)
  - Unique identifier for each validation query
  - Generated automatically upon creation
- `query_text`: Text
  - The original query text used for validation
  - Required
- `query_type`: Enum
  - Type of query: ['factual', 'conceptual', 'procedural', 'comparative', 'hybrid']
  - Required, default: 'factual'
- `expected_topics`: Array<String>
  - List of topics expected in relevant results
  - Optional
- `created_at`: DateTime (UTC)
  - Timestamp when query was created
  - Required
- `embedding_vector`: Array<Float>
  - The embedding vector for the query text
  - Optional (may be computed on demand)
- `query_metadata`: JSON
  - Additional metadata about the query
  - Optional

### Relationships
- One-to-Many: Query to ValidationResults

## ValidationResults Entity

### Attributes
- `result_id`: UUID (Primary Key)
  - Unique identifier for each validation result set
  - Generated automatically upon creation
- `query_id`: UUID (Foreign Key)
  - Reference to the original query
  - Required, indexed
- `retrieved_count`: Integer
  - Number of chunks retrieved in the search
  - Required, positive
- `relevance_score`: Float
  - Overall relevance score (0.0 to 1.0)
  - Required
- `metadata_accuracy`: Float
  - Accuracy of metadata mapping (0.0 to 1.0)
  - Required
- `precision_at_k`: JSON
  - Precision scores at different K values
  - Optional (e.g., {"p@1": 0.8, "p@3": 0.7, "p@5": 0.6})
- `mrr_score`: Float
  - Mean Reciprocal Rank score
  - Optional
- `ndcg_score`: Float
  - Normalized Discounted Cumulative Gain score
  - Optional
- `execution_time_ms`: Integer
  - Time taken to execute the query in milliseconds
  - Required
- `created_at`: DateTime (UTC)
  - Timestamp when validation was executed
  - Required

### Relationships
- Many-to-One: ValidationResults to Query
- One-to-Many: ValidationResults to RetrievedChunks

## RetrievedChunk Entity

### Attributes
- `retrieved_chunk_id`: UUID (Primary Key)
  - Unique identifier for each retrieved chunk in a result set
  - Generated automatically upon creation
- `result_id`: UUID (Foreign Key)
  - Reference to the validation result set
  - Required, indexed
- `chunk_id`: String
  - ID of the chunk as stored in Qdrant
  - Required
- `similarity_score`: Float
  - Similarity score between query and this chunk (0.0 to 1.0)
  - Required
- `rank_position`: Integer
  - Position of this chunk in the ranked results (1-indexed)
  - Required, positive
- `content_preview`: Text
  - First 200 characters of the retrieved chunk
  - Optional
- `source_url`: String (URL)
  - URL of the original document
  - Required
- `document_title`: String
  - Title of the source document
  - Optional
- `position_in_document`: Integer
  - Position of this chunk in the original document
  - Optional
- `metadata_valid`: Boolean
  - Whether metadata mapping is correct
  - Required, default: false
- `content_relevant`: Boolean
  - Whether content is relevant to the query
  - Required, default: false

### Relationships
- Many-to-One: RetrievedChunk to ValidationResults

## ValidationRun Entity

### Attributes
- `run_id`: UUID (Primary Key)
  - Unique identifier for each validation run
  - Generated automatically upon creation
- `run_name`: String
  - Name/description of the validation run
  - Optional
- `total_queries`: Integer
  - Total number of queries in this run
  - Required, positive
- `queries_executed`: Integer
  - Number of queries that were successfully executed
  - Required, non-negative
- `queries_failed`: Integer
  - Number of queries that failed during execution
  - Required, non-negative
- `average_relevance`: Float
  - Average relevance score across all queries
  - Optional
- `average_metadata_accuracy`: Float
  - Average metadata accuracy across all queries
  - Optional
- `start_time`: DateTime (UTC)
  - When the validation run started
  - Required
- `end_time`: DateTime (UTC)
  - When the validation run ended
  - Optional
- `status`: Enum
  - Current status: ['running', 'completed', 'failed', 'cancelled']
  - Required, default: 'running'

### Relationships
- One-to-Many: ValidationRun to QueryExecutions

## QueryExecution Entity

### Attributes
- `execution_id`: UUID (Primary Key)
  - Unique identifier for each query execution
  - Generated automatically upon creation
- `run_id`: UUID (Foreign Key)
  - Reference to the validation run
  - Required, indexed
- `query_id`: UUID (Foreign Key)
  - Reference to the query being executed
  - Required, indexed
- `result_id`: UUID (Foreign Key)
  - Reference to the validation results
  - Optional (null if execution failed)
- `status`: Enum
  - Execution status: ['pending', 'executing', 'success', 'failed']
  - Required, default: 'pending'
- `error_message`: Text
  - Error message if execution failed
  - Optional
- `execution_time_ms`: Integer
  - Time taken for this specific execution
  - Optional
- `created_at`: DateTime (UTC)
  - When execution was initiated
  - Required

### Relationships
- Many-to-One: QueryExecution to ValidationRun
- Many-to-One: QueryExecution to Query
- Many-to-One: QueryExecution to ValidationResults (optional)

## TestDataset Entity

### Attributes
- `dataset_id`: UUID (Primary Key)
  - Unique identifier for each test dataset
  - Generated automatically upon creation
- `name`: String
  - Name of the test dataset
  - Required
- `description`: Text
  - Description of the dataset purpose
  - Optional
- `query_count`: Integer
  - Number of queries in this dataset
  - Required, positive
- `domain`: String
  - Domain or topic area of the dataset
  - Optional
- `created_at`: DateTime (UTC)
  - When the dataset was created
  - Required
- `is_golden`: Boolean
  - Whether this is a golden dataset with known answers
  - Required, default: false
- `dataset_metadata`: JSON
  - Additional metadata about the dataset
  - Optional

### Relationships
- One-to-Many: TestDataset to DatasetQueries

## DatasetQuery Entity

### Attributes
- `dataset_query_id`: UUID (Primary Key)
  - Unique identifier for each query in a dataset
  - Generated automatically upon creation
- `dataset_id`: UUID (Foreign Key)
  - Reference to the test dataset
  - Required, indexed
- `query_id`: UUID (Foreign Key)
  - Reference to the query entity
  - Required, unique per dataset
- `expected_relevant_chunks`: Array<String>
  - List of expected relevant chunk IDs
  - Optional
- `relevance_threshold`: Float
  - Threshold for considering a result relevant (0.0 to 1.0)
  - Optional, default: 0.7

### Relationships
- Many-to-One: DatasetQuery to TestDataset
- Many-to-One: DatasetQuery to Query

## Constraints and Validation

### Query Constraints
- `query_text` length must be between 5 and 1000 characters
- `query_type` must be one of the defined enum values
- `relevance_score` and `metadata_accuracy` must be between 0.0 and 1.0

### ValidationResults Constraints
- `retrieved_count` must be non-negative
- `execution_time_ms` must be non-negative
- `query_id` must reference an existing Query

### RetrievedChunk Constraints
- `similarity_score` must be between 0.0 and 1.0
- `rank_position` must be positive
- `result_id` must reference an existing ValidationResults
- `rank_position` must be unique within a ValidationResults set

### ValidationRun Constraints
- `total_queries` >= `queries_executed` + `queries_failed`
- `start_time` <= `end_time` (if end_time is set)

## Indexing Strategy

### Primary Indexes
- `query_id` in Query table
- `result_id` in ValidationResults table
- `retrieved_chunk_id` in RetrievedChunk table
- `run_id` in ValidationRun table

### Secondary Indexes
- `query_id` in ValidationResults (foreign key)
- `result_id` in RetrievedChunk (foreign key)
- `run_id` in QueryExecution (foreign key)
- `created_at` in Query (for time-based queries)
- `created_at` in ValidationResults (for time-based queries)

## Performance Considerations

### Partitioning Strategy
- Consider partitioning ValidationResults by date for large datasets
- May partition by query type for analytical queries

### Query Optimization
- Index foreign key relationships for join operations
- Consider materialized views for common aggregate queries
- Optimize for time-range queries on validation runs

## Data Integrity

### Referential Integrity
- Foreign key constraints ensure valid relationships
- Cascade delete operations where appropriate
- Prevent orphaned records

### Audit Trail
- Created/updated timestamps on all entities
- Track execution details for debugging
- Maintain query history for analysis
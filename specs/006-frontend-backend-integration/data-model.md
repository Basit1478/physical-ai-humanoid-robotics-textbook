# Data Model: Docusaurus-Backend Integration

## Overview
Data model for the integration layer connecting Docusaurus frontend to FastAPI backend for chatbot functionality.

## FrontendRequest Entity

### Attributes
- `request_id`: String (Primary Key)
  - Unique identifier for each frontend request
  - Generated automatically upon request creation
- `query_text`: Text
  - The user's main question or query
  - Required
- `selected_text`: Text
  - Text selected by the user on the current page
  - Optional
- `current_page_url`: String (URL)
  - URL of the page where the query originated
  - Optional
- `current_page_title`: String
  - Title of the current page
  - Optional
- `user_context`: JSON
  - Additional context about the user's current state
  - Optional (e.g., scroll position, section)
- `timestamp`: DateTime (ISO string)
  - When the request was created
  - Required

### Relationships
- One-to-One: FrontendRequest to BackendResponse
- One-to-Many: FrontendRequest to ChatMessage (as user message)

## BackendResponse Entity

### Attributes
- `response_id`: String (Primary Key)
  - Unique identifier from the backend service
  - Provided by backend API
- `request_id`: String (Foreign Key)
  - Reference to the original frontend request
  - Required, indexed
- `answer_text`: Text
  - The AI-generated response text
  - Required
- `source_chunks`: Array<String>
  - List of source chunk IDs used to generate the response
  - Optional
- `confidence_score`: Float
  - Confidence level of the response (0.0 to 1.0)
  - Optional
- `citations`: Array<JSON>
  - Citations to source documents
  - Optional (e.g., [{"url": "...", "title": "...", "position": ...}])
- `response_metadata`: JSON
  - Additional metadata from the backend
  - Optional (e.g., tokens used, processing time)
- `received_at`: DateTime (ISO string)
  - When the response was received from backend
  - Required

### Relationships
- Many-to-One: BackendResponse to FrontendRequest
- One-to-Many: BackendResponse to ChatMessage (as agent response)

## ChatMessage Entity

### Attributes
- `message_id`: String (Primary Key)
  - Unique identifier for each chat message
  - Generated automatically upon creation
- `session_id`: String
  - Identifier for the chat session
  - Required, indexed
- `content`: Text
  - The message content
  - Required
- `sender`: Enum
  - Who sent the message: ['user', 'agent']
  - Required
- `request_id`: String (Foreign Key)
  - Reference to the frontend request (for user messages)
  - Optional, indexed
- `response_id`: String (Foreign Key)
  - Reference to the backend response (for agent messages)
  - Optional, indexed
- `timestamp`: DateTime (ISO string)
  - When the message was created/sent
  - Required
- `status`: Enum
  - Message status: ['pending', 'sent', 'received', 'error']
  - Required, default: 'sent'
- `error_message`: Text
  - Error details if status is 'error'
  - Optional

### Relationships
- Many-to-One: ChatMessage to ChatSession
- Many-to-One: ChatMessage to FrontendRequest (optional)
- Many-to-One: ChatMessage to BackendResponse (optional)

## ChatSession Entity

### Attributes
- `session_id`: String (Primary Key)
  - Unique identifier for each chat session
  - Generated automatically upon session creation
- `page_url`: String (URL)
  - URL of the page where the session started
  - Optional
- `page_title`: String
  - Title of the page where the session started
  - Optional
- `created_at`: DateTime (ISO string)
  - When the session was created
  - Required
- `last_activity`: DateTime (ISO string)
  - When the last message was sent/received
  - Required
- `message_count`: Integer
  - Number of messages in the session
  - Required, default: 0
- `is_active`: Boolean
  - Whether the session is currently active
  - Required, default: true
- `session_metadata`: JSON
  - Additional metadata about the session
  - Optional (e.g., user agent, device info)

### Relationships
- One-to-Many: ChatSession to ChatMessages
- One-to-Many: ChatSession to SessionEvents

## SessionEvent Entity

### Attributes
- `event_id`: String (Primary Key)
  - Unique identifier for each session event
  - Generated automatically upon event creation
- `session_id`: String (Foreign Key)
  - Reference to the chat session
  - Required, indexed
- `event_type`: Enum
  - Type of event: ['session_start', 'message_sent', 'message_received', 'session_end', 'error']
  - Required
- `event_data`: JSON
  - Additional data about the event
  - Optional (e.g., {'message_id': '...', 'error_type': '...'})
- `timestamp`: DateTime (ISO string)
  - When the event occurred
  - Required

### Relationships
- Many-to-One: SessionEvent to ChatSession

## TextSelection Entity

### Attributes
- `selection_id`: String (Primary Key)
  - Unique identifier for each text selection
  - Generated automatically upon selection
- `session_id`: String (Foreign Key)
  - Reference to the chat session
  - Optional, indexed
- `selected_text`: Text
  - The actual selected text
  - Required
- `page_url`: String (URL)
  - URL of the page where text was selected
  - Required
- `page_title`: String
  - Title of the page where text was selected
  - Required
- `selection_context`: JSON
  - Context around the selection
  - Optional (e.g., {'before': '...', 'after': '...', 'element': '...'})
- `dom_path`: String
  - DOM path to the selected element
  - Optional
- `created_at`: DateTime (ISO string)
  - When the selection was made
  - Required

### Relationships
- Many-to-One: TextSelection to ChatSession (optional)
- One-to-Many: TextSelection to SelectionUsage

## SelectionUsage Entity

### Attributes
- `usage_id`: String (Primary Key)
  - Unique identifier for each selection usage
  - Generated automatically upon usage
- `selection_id`: String (Foreign Key)
  - Reference to the text selection
  - Required, indexed
- `request_id`: String (Foreign Key)
  - Reference to the frontend request that used this selection
  - Required, indexed
- `usage_type`: Enum
  - How the selection was used: ['query_context', 'focused_query', 'reference']
  - Required
- `used_at`: DateTime (ISO string)
  - When the selection was used
  - Required

### Relationships
- Many-to-One: SelectionUsage to TextSelection
- Many-to-One: SelectionUsage to FrontendRequest

## IntegrationConfig Entity

### Attributes
- `config_id`: String (Primary Key)
  - Unique identifier for configuration
  - Usually 'default' for the main configuration
- `backend_url`: String (URL)
  - URL of the FastAPI backend
  - Required
- `api_timeout`: Integer
  - Timeout for API requests in milliseconds
  - Required, default: 15000
- `selected_text_enabled`: Boolean
  - Whether selected text feature is enabled
  - Required, default: true
- `chat_position`: Enum
  - Position of chat interface: ['bottom-right', 'sidebar', 'inline']
  - Required, default: 'bottom-right'
- `max_messages_stored`: Integer
  - Maximum number of messages to store locally
  - Required, default: 50
- `last_updated`: DateTime (ISO string)
  - When the configuration was last updated
  - Required

## UIState Entity

### Attributes
- `state_id`: String (Primary Key)
  - Unique identifier for UI state
  - Usually 'current' for current state
- `session_id`: String (Foreign Key)
  - Reference to the current chat session
  - Optional, indexed
- `is_chat_open`: Boolean
  - Whether the chat interface is currently open
  - Required, default: false
- `input_text`: Text
  - Current text in the chat input field
  - Optional
- `selected_text`: Text
  - Currently highlighted text in the UI
  - Optional
- `last_interaction`: DateTime (ISO string)
  - When the last UI interaction occurred
  - Required
- `ui_preferences`: JSON
  - User preferences for UI behavior
  - Optional (e.g., {'theme': 'dark', 'notifications': true})

### Relationships
- Many-to-One: UIState to ChatSession (optional)

## Constraints and Validation

### FrontendRequest Constraints
- `query_text` length must be between 1 and 10000 characters
- `selected_text` length must be between 1 and 5000 characters if provided
- `timestamp` must be a valid ISO date string

### BackendResponse Constraints
- `confidence_score` must be between 0.0 and 1.0 if provided
- `request_id` must reference an existing FrontendRequest
- `response_id` should match the ID from backend API

### ChatMessage Constraints
- `sender` must be either 'user' or 'agent'
- `status` must be one of the defined enum values
- Either `request_id` or `response_id` must be provided based on sender type

### TextSelection Constraints
- `selected_text` length must be between 1 and 5000 characters
- `page_url` must be a valid URL format

## Indexing Strategy

### Primary Indexes
- `request_id` in FrontendRequest table
- `response_id` in BackendResponse table
- `message_id` in ChatMessage table
- `session_id` in ChatSession table

### Secondary Indexes
- `session_id` in ChatMessage (for session queries)
- `request_id` in ChatMessage (for user messages)
- `response_id` in ChatMessage (for agent messages)
- `created_at` in ChatMessage (for chronological queries)
- `session_id` in SessionEvent (for event queries)

## Performance Considerations

### Data Storage Strategy
- Consider browser storage (localStorage/sessionStorage) for client-side state
- Implement pagination for large message histories
- Cache configuration values to avoid repeated lookups

### Query Optimization
- Index frequently queried fields
- Consider denormalization for frequently accessed data
- Optimize for the most common query patterns

## Data Integrity

### Referential Integrity
- Validate relationships between entities
- Handle session cleanup appropriately
- Maintain consistency between related records

### Lifecycle Management
- Implement session expiration for inactive sessions
- Clean up old messages based on retention policy
- Handle component unmounting and state cleanup
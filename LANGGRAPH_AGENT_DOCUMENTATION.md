# LangGraph Agent Documentation

## Overview

The LangGraph agent is the core AI component of the CRM HCP module. It manages HCP interactions through intelligent processing of natural language descriptions, automated form filling, validation, and correction capabilities.

## Agent Role

The LangGraph agent acts as an intelligent assistant that:

1. **Processes Natural Language**: Interprets unstructured descriptions of HCP interactions
2. **Extracts Structured Data**: Automatically extracts entities (names, dates, topics, sentiment) from text
3. **Automates Form Filling**: Populates form fields based on conversation context
4. **Validates Data**: Ensures completeness and accuracy of logged interactions
5. **Identifies Errors**: Detects mistakes or inconsistencies in form data
6. **Applies Corrections**: Modifies logged data based on user feedback
7. **Suggests Actions**: Generates intelligent follow-up recommendations
8. **Maintains Context**: Preserves conversation state for multi-turn interactions

## Agent Architecture

### State Management

The agent uses a typed state (`AgentState`) that tracks:

- **messages**: Conversation history between user and agent
- **current_form_data**: Current state of the interaction form
- **extracted_entities**: Entities extracted from natural language
- **interaction_id**: ID of the logged interaction
- **hcp_id**: ID of the HCP being interacted with
- **validation_errors**: List of validation errors if any
- **suggested_followups**: AI-generated follow-up suggestions
- **correction_result**: Result of correction operations

### Graph Structure

The agent follows a directed graph workflow:

```
extract_entities → fill_form → validate_form → suggest_followups → log_interaction → END
                      ↓
                 correct_form (if validation fails)
```

## Agent Tools

The agent uses 6 specialized tools for sales-related activities:

### 1. Log Interaction Tool

**Purpose**: Captures interaction data using LLM for summarization and entity extraction.

**Function**: `log_interaction(interaction_data: Dict[str, Any])`

**Parameters**:
- `interaction_data`: Dictionary containing:
  - `hcp_id`: ID of the healthcare professional
  - `interaction_type`: Type (Meeting, Call, Email, etc.)
  - `date`: Date of interaction
  - `time`: Time of interaction
  - `attendees`: Other participants
  - `topics_discussed`: Key discussion points
  - `sentiment`: HCP sentiment (Positive, Neutral, Negative)
  - `outcomes`: Key outcomes or agreements
  - `follow_up_actions`: Next steps
  - `materials_shared`: List of shared materials
  - `samples_distributed`: List of distributed samples

**Returns**: 
- `success`: Boolean indicating operation status
- `interaction_id`: ID of the logged interaction
- `message`: Status message
- `data`: The logged interaction data

**LLM Integration**: Uses LLM to:
- Summarize lengthy descriptions
- Extract key entities automatically
- Format data for database storage
- Generate interaction summaries

### 2. Edit Interaction Tool

**Purpose**: Allows modification of logged data with AI validation.

**Function**: `edit_interaction(interaction_id: int, updates: Dict[str, Any])`

**Parameters**:
- `interaction_id`: ID of the interaction to edit
- `updates`: Dictionary of fields to update with new values

**Returns**:
- `success`: Boolean indicating operation status
- `interaction_id`: ID of the updated interaction
- `message`: Status message
- `updated_fields`: List of fields that were modified

**AI Validation**: 
- Validates new data against business rules
- Checks for data consistency
- Maintains audit trail of changes

### 3. Search HCP Tool

**Purpose**: Searches and retrieves HCP information from the database.

**Function**: `search_hcp(query: str)`

**Parameters**:
- `query`: Search term (name, specialty, or organization)

**Returns**:
- `success`: Boolean indicating operation status
- `results`: List of matching HCPs with details
- `count`: Number of results found

**Usage Context**:
- Used when user mentions an HCP name in description
- Helps identify the correct HCP for logging
- Provides context for interaction logging

### 4. Extract Entities Tool

**Purpose**: Extracts key entities from natural language descriptions.

**Function**: `extract_entities(description: str)`

**Parameters**:
- `description`: Natural language description of the interaction

**Returns**:
- `success`: Boolean indicating operation status
- `entities`: Dictionary containing:
  - `hcp_name`: Name of the healthcare professional
  - `date`: Date of interaction
  - `time`: Time of interaction
  - `interaction_type`: Type of interaction
  - `topics_discussed`: Key topics
  - `sentiment`: Detected sentiment
  - `outcomes`: Key outcomes
  - `attendees`: Other participants
  - `materials`: List of materials mentioned
  - `samples`: List of samples mentioned

**Extraction Methods**:
- Pattern matching for structured data (names, dates)
- Keyword analysis for sentiment detection
- Contextual extraction for topics and outcomes
- Entity recognition for medical terms

### 5. Suggest Follow-ups Tool

**Purpose**: Generates AI-suggested follow-up actions based on interaction context.

**Function**: `suggest_followups(interaction_context: Dict[str, Any])`

**Parameters**:
- `interaction_context`: Dictionary with interaction details including:
  - `topics_discussed`: What was discussed
  - `sentiment`: HCP's sentiment
  - `outcomes`: What was achieved
  - `hcp_specialty`: HCP's medical specialty

**Returns**:
- `success`: Boolean indicating operation status
- `suggestions`: List of 3-5 relevant follow-up actions

**Suggestion Logic**:
- Topic-specific recommendations (e.g., clinical data for product discussions)
- Sentiment-based actions (e.g., MSL visit for negative sentiment)
- Outcome-driven suggestions (e.g., confirmation emails for agreements)
- Specialty-tailored recommendations

**Example Suggestions**:
- "Schedule follow-up meeting in 2 weeks"
- "Send clinical trial data PDF"
- "Add to advisory board invite list"
- "Request referral to colleague"
- "Schedule sample replenishment visit"

### 6. Validate Interaction Tool

**Purpose**: Validates interaction data for completeness and accuracy.

**Function**: `validate_interaction(interaction_data: Dict[str, Any])`

**Parameters**:
- `interaction_data`: Dictionary with interaction form data

**Returns**:
- `success`: Boolean indicating validation status
- `errors`: List of validation errors
- `warnings`: List of warnings (non-critical issues)
- `is_valid`: Boolean indicating if data is valid

**Validation Checks**:
- Required field presence (hcp_id, interaction_type, date)
- Data format validation (date format, time format)
- Value validation (sentiment must be Positive/Neutral/Negative)
- Logical consistency checks
- Completeness warnings

## Agent Nodes

### Extract Entities Node
- Processes user's natural language description
- Invokes `extract_entities` tool
- Stores extracted entities in state
- Provides feedback to user

### Fill Form Node
- Structures extracted entities into form data
- Applies default values for missing fields
- Updates state with current form data
- Notifies user of form completion

### Validate Form Node
- Invokes `validate_interaction` tool
- Checks for errors and warnings
- Routes to correction if errors exist
- Proceeds to suggestions if valid

### Suggest Follow-ups Node
- Invokes `suggest_followups` tool
- Generates relevant follow-up actions
- Updates form data with suggestions
- Enhances interaction value

### Log Interaction Node
- Invokes `log_interaction` tool
- Persists interaction to database
- Returns interaction ID
- Confirms successful logging

### Correct Form Node
- Processes user correction instructions
- Uses LLM to understand and apply corrections
- Updates form data accordingly
- Re-routes to validation

### Chat Node
- Handles general conversational interactions
- Maintains conversation context
- Provides helpful responses
- Guides users through the process

## LLM Integration

### Model Configuration
- **Primary Model**: llama-3.1-8b-instant (Groq)
- **Alternative Model**: llama-3.3-70b-versatile (for complex tasks)
- **Temperature**: 0.1 (for consistent, deterministic outputs)

### LLM Usage Patterns

1. **Entity Extraction**: Structured output parsing from natural language
2. **Form Filling**: JSON generation for form data
3. **Correction Application**: Understanding and applying user feedback
4. **Follow-up Generation**: Context-aware suggestion generation
5. **Conversational Response**: Natural language generation for chat

### Prompt Engineering

The agent uses carefully crafted system prompts to:
- Define the agent's role and capabilities
- Guide output format (JSON for structured data)
- Ensure consistency in responses
- Handle edge cases gracefully

## API Endpoints

### Agent-Specific Endpoints

- `POST /api/agent/fill-form` - AI fills form from description
- `POST /api/agent/correct` - AI corrects form errors
- `POST /api/agent/chat` - Chat with AI agent
- `POST /api/agent/suggest-followups` - Generate follow-up suggestions

### Request/Response Examples

#### Fill Form Request
```json
{
  "description": "Met Dr. Smith, discussed Product X efficacy, positive sentiment, shared brochure"
}
```

#### Fill Form Response
```json
{
  "success": true,
  "form_data": {
    "hcp_name": "Dr. Smith",
    "interaction_type": "Meeting",
    "sentiment": "Positive",
    "topics_discussed": "Product X efficacy",
    "materials": ["brochure"],
    "ai_suggested_followups": [
      "Schedule follow-up meeting in 2 weeks",
      "Send clinical trial data PDF"
    ]
  }
}
```

## Error Handling

The agent handles various error scenarios:

1. **LLM API Failures**: Graceful fallback to rule-based extraction
2. **Invalid Input**: Clear error messages with guidance
3. **Validation Failures**: Specific error details for correction
4. **Network Issues**: Retry logic with user notification

## Performance Considerations

- **Async Operations**: All LLM calls are asynchronous for responsiveness
- **Caching**: HCP search results cached for efficiency
- **Batch Processing**: Multiple entities extracted in single LLM call
- **State Management**: Minimal state to reduce memory footprint

## Security

- **API Key Management**: Environment variable configuration
- **Input Sanitization**: All user inputs validated
- **Output Filtering**: Sensitive data filtered from responses
- **Audit Logging**: All agent actions logged for compliance

## Future Enhancements

Potential improvements to the agent:

1. **Voice Input**: Direct speech-to-text integration
2. **Multi-language**: Support for multiple languages
3. **Advanced Analytics**: Interaction pattern analysis
4. **Predictive Actions**: Proactive follow-up suggestions
5. **Integration**: EHR system integration
6. **Compliance**: Built-in regulatory compliance checks

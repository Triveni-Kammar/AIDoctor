# AI-First CRM HCP Module - Log Interaction Screen

## Overview
An AI-powered Customer Relationship Management system specifically designed for Healthcare Professional (HCP) interactions. This module enables field representatives to log interactions with HCPs through either a structured form or conversational AI chat interface.

## Tech Stack

### Frontend
- **React** - UI Framework
- **Redux** - State Management
- **TailwindCSS** - Styling
- **Google Inter** - Font
- **Axios** - HTTP Client

### Backend
- **Python** - Language
- **FastAPI** - Web Framework
- **LangGraph** - AI Agent Framework
- **Groq LLM** - llama-3.1-8b-instant / llama-3.3-70b-versatile
- **PostgreSQL** - Database
- **SQLAlchemy** - ORM
- **Pydantic** - Data Validation

## Project Structure

```
PalAss/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI application entry point
│   │   ├── config.py               # Configuration settings
│   │   ├── database.py             # Database connection
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── hcp.py              # HCP model
│   │   │   ├── interaction.py      # Interaction model
│   │   │   └── material.py         # Material/Sample model
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── interaction.py      # Pydantic schemas
│   │   │   └── hcp.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py           # API routes
│   │   │   └── dependencies.py     # Dependencies
│   │   ├── agent/
│   │   │   ├── __init__.py
│   │   │   ├── graph.py            # LangGraph agent definition
│   │   │   ├── nodes.py            # Agent nodes
│   │   │   ├── tools.py            # Agent tools
│   │   │   └── state.py            # Agent state
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── interaction_service.py
│   │       └── llm_service.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── index.js
│   │   ├── App.js
│   │   ├── store/
│   │   │   ├── index.js
│   │   │   ├── reducers.js
│   │   │   └── actions.js
│   │   ├── components/
│   │   │   ├── LogInteraction/
│   │   │   │   ├── index.js
│   │   │   │   ├── LogInteraction.js
│   │   │   │   ├── InteractionForm.js
│   │   │   │   ├── AIChatPanel.js
│   │   │   │   └── LogInteraction.css
│   │   │   └── common/
│   │   │       ├── Input.js
│   │   │       ├── Select.js
│   │   │       ├── TextArea.js
│   │   │       └── Button.js
│   │   ├── services/
│   │   │   └── api.js
│   │   └── utils/
│   │       └── constants.js
│   ├── package.json
│   └── .env.example
├── README.md
└── .gitignore
```

## LangGraph Agent Architecture

### Agent Role
The LangGraph agent acts as an intelligent assistant that:
1. Processes natural language descriptions of HCP interactions
2. Extracts structured data from unstructured text
3. Automatically fills form fields based on conversation
4. Identifies and corrects errors in logged data
5. Suggests follow-up actions based on interaction context
6. Maintains conversation context for multi-turn interactions

### Agent Tools (Minimum 5 Required)

1. **log_interaction** - Captures interaction data using LLM for summarization and entity extraction
2. **edit_interaction** - Allows modification of logged data with AI validation
3. **search_hcp** - Searches and retrieves HCP information from database
4. **extract_entities** - Extracts key entities (names, dates, topics, sentiment) from natural language
5. **suggest_followups** - Generates AI-suggested follow-up actions based on interaction context
6. **validate_interaction** - Validates interaction data for completeness and accuracy

## Features

### Log Interaction Screen
- **Dual Interface**: Structured form + AI Chat
- **AI-Powered Form Filling**: Describe interaction in chat, AI fills the form
- **Auto-Correction**: AI identifies and fixes mistakes automatically
- **Voice Note Support**: Summarize from voice notes (with consent)
- **Material/Sample Tracking**: Track shared materials and distributed samples
- **Sentiment Analysis**: Auto-detect HCP sentiment
- **Smart Follow-ups**: AI-suggested follow-up actions

## Setup Instructions

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your Groq API key and database credentials
uvicorn app.main:app --reload
```

### Frontend Setup
```bash
cd frontend
npm install
cp .env.example .env
# Edit .env with backend API URL
npm start
```

## Environment Variables

### Backend (.env)
```
GROQ_API_KEY=your_groq_api_key
DATABASE_URL=postgresql://user:password@localhost/palass
LLM_MODEL=llama-3.1-8b-instant
```

### Frontend (.env)
```
REACT_APP_API_URL=http://localhost:8000
```

## API Endpoints

- `POST /api/interactions/log` - Log a new interaction
- `PUT /api/interactions/{id}` - Edit an interaction
- `GET /api/interactions/{id}` - Get interaction details
- `POST /api/agent/chat` - Chat with AI agent
- `POST /api/agent/fill-form` - AI fills form from description
- `POST /api/agent/correct` - AI corrects form errors

## Database Schema

### HCP Table
- id, name, specialty, organization, contact_info, created_at, updated_at

### Interaction Table
- id, hcp_id, interaction_type, date, time, attendees, topics_discussed, 
  sentiment, outcomes, follow_up_actions, materials_shared, samples_distributed, 
  ai_suggested_followups, created_at, updated_at

### Material Table
- id, name, type, description

### Sample Table
- id, name, batch_number, quantity

## License
Proprietary - Assignment Submission

# JQL Analyzer Chat Participant

A sophisticated chat participant that analyzes natural language queries and converts them into JQL (JIRA Query Language) queries. It uses RAG (Retrieval Augmented Generation) with LangChain to provide accurate JIRA query results.

## Features

- Natural language to JQL query conversion
- RAG system using JIRA documentation and JQL cheat sheets
- Historical JIRA summaries integration
- Semantic chunking for better context understanding
- Real-time JIRA API integration
- FastAPI-based REST API

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file from `.env.example`:
   ```bash
   cp .env.example .env
   ```
4. Fill in your environment variables in `.env`

## Project Structure

```
.
├── src/
│   └── jql_analyzer/
│       ├── __init__.py
│       ├── api.py              # FastAPI endpoints
│       └── chat_participant.py # Main chat participant implementation
├── data/
│   ├── docs/                   # JIRA documentation and cheat sheets
│   └── chroma_db/             # Vector store persistence
├── requirements.txt
├── .env.example
└── README.md
```

## Usage

1. Start the API server:
   ```bash
   uvicorn src.jql_analyzer.api:app --reload
   ```

2. Send a POST request to `/analyze`:
   ```bash
   curl -X POST "http://localhost:8000/analyze" \
        -H "Content-Type: application/json" \
        -d '{"text": "show me all high priority bugs assigned to me"}'
   ```

## Environment Variables

- `JIRA_SERVER`: Your JIRA server URL
- `JIRA_API_TOKEN`: JIRA API token
- `JIRA_EMAIL`: JIRA account email
- `OPENAI_API_KEY`: OpenAI API key for embeddings and LLM

## Documentation Structure

Place your JIRA documentation and JQL cheat sheets in the `data/docs` directory. The system will automatically index and use them for the RAG system.

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

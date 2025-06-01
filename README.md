# Multi-Format Intake Agent with Intelligent Routing & Context Memory

This project implements a multi-agent AI system that accepts data in PDF, JSON, or Email (text) format, intelligently classifies the input type and purpose, and routes it to the appropriate specialized agent for extraction. The system maintains context (e.g., sender, topic, last extracted fields) to support downstream chaining or audits.

## System Overview

The system consists of the following core components:

1. **Classifier Agent**: Receives raw input, classifies format & intent, and routes to the appropriate agent.
2. **JSON Agent**: Handles JSON input, extracts data to a defined FlowBit schema, and identifies anomalies or missing fields.
3. **Email Parser Agent**: Handles email body text, extracts sender, request intent, urgency, and returns a formatted CRM-style record.
4. **Shared Memory Module**: Stores input metadata, extracted fields, and thread/conversation IDs, accessible by all agents.

## Tech Stack

- **Python** (with FastAPI for API endpoints)
- **LLM** (OpenAI API, can be swapped for Gemini or open-source)
- **Memory**: SQLite (simple, file-based, cross-platform, no external dependencies)
- **Langchain** (optional, for LLM orchestration and memory abstraction)

## Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd multi-format-intake-agent
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the FastAPI server:
   ```bash
   uvicorn main:app --reload
   ```

## Usage

Send a POST request to the `/intake` endpoint with one of the following:

- **File Upload**: Send a file (PDF, JSON, or email text).
- **JSON Data**: Send JSON data in the request body.
- **Email Text**: Send email text in the request body.

Example using `curl`:

```bash
# File Upload
curl -X POST -F "file=@/path/to/file.pdf" http://localhost:8000/intake

# JSON Data
curl -X POST -H "Content-Type: application/json" -d '{"invoice": "data"}' http://localhost:8000/intake

# Email Text
curl -X POST -F "email_text=From: sender@example.com\nSubject: RFQ\nBody: This is an urgent RFQ." http://localhost:8000/intake
```

## End-to-End Flow

1. User uploads an email body → Classifier detects "email + RFQ intent"
2. Routed to Email Parser → Extracts sender, request, urgency
3. Memory stores output
4. If RFQ references an attached JSON → also route to JSON agent
5. Combined structured output is returned (or logged to mock CRM)

## License

This project is licensed under the MIT License.
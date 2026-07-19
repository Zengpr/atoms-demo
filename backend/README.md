# Atoms Demo Backend

AI Agent-driven code generation platform backend.

## Quick Start

```bash
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

The API runs at `http://localhost:8000`. Docs at `/docs`.

## Architecture

- **Agents**: Multi-agent AI system (Leader, PM, Architect, Engineer, Researcher)
- **Modes**: Engineer (direct code gen) and Team (full pipeline)
- **Mock Mode**: Works without OpenAI API key - generates template responses
- **SSE Streaming**: Chat responses stream in real-time via Server-Sent Events

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | /api/auth/register | Register user |
| POST | /api/auth/login | Login |
| GET | /api/auth/me | Current user |
| GET | /api/projects | List projects |
| POST | /api/projects | Create project |
| GET | /api/projects/{id} | Get project |
| PUT | /api/projects/{id} | Update project |
| DELETE | /api/projects/{id} | Delete project |
| GET | /api/projects/{id}/versions | Code versions |
| POST | /api/chat/{id}/message | Send message (SSE) |
| GET | /api/chat/{id}/history | Chat history |
| GET | /api/preview/{id}/html | Preview HTML |
| POST | /api/preview/{id}/deploy | Deploy project |

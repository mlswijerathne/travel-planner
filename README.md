# Sri Lanka Travel Agent - Multi-Agent System

An AI-powered travel planning system for Sri Lanka using **Google Agent Development Kit (ADK)** with **Multi-Agent Architecture** and **Human-in-the-Loop** approval workflow.

## Features

- 🤖 **Multi-Agent Architecture**: Specialized agents for weather, safety, routes, budget, and activities
- 👤 **Human-in-the-Loop**: Critical decisions require human approval before finalizing
- ⚡ **Parallel Processing**: Concurrent data gathering for faster responses
- 🌐 **Real-Time APIs**: OpenWeatherMap, Google Maps, Google Places integration

## Project Structure

```
travel agent/
├── main.py                 # FastAPI entry point
├── config/                 # Configuration settings
│   └── settings.py
├── agents/                 # Agent definitions
│   ├── orchestrator.py     # Multi-agent orchestrator
│   ├── workflow.py         # Sequential/Parallel workflows
│   └── specialists/        # Domain specialist agents
│       ├── weather_agent.py
│       ├── safety_agent.py
│       ├── route_agent.py
│       ├── budget_agent.py
│       ├── activity_agent.py
│       └── plan_reviewer_agent.py
├── tools/                  # Tool implementations
│   ├── weather_tool.py     # OpenWeatherMap API
│   ├── safety_tool.py      # Safety information
│   ├── route_tool.py       # Google Maps API
│   ├── budget_tool.py      # Pricing tools
│   ├── activity_tool.py    # Google Places API
│   └── human_approval_tool.py  # Human-in-the-Loop
└── docs/
    └── ARCHITECTURE.md     # Detailed architecture docs
```

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment variables** in `.env`:
   ```
   GOOGLE_API_KEY=your_gemini_api_key
   GOOGLE_MAPS_API_KEY=your_maps_api_key
   OPENWEATHER_API_KEY=your_openweather_api_key
   ```

## Running the Server

```bash
# Development
uvicorn main:app --reload --port 8000

# Production
python main.py
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/plan` | Full planning with human approval |
| POST | `/quick-plan` | Quick planning without approval |
| POST | `/approve` | Submit approval decision |
| GET | `/pending-approvals` | List pending approvals |
| GET | `/health` | Health check |

## Usage Examples

### Request a Travel Plan
```bash
curl -X POST http://localhost:8000/plan \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Plan a 5-day trip to Kandy and Sigiriya focusing on heritage",
    "require_approval": true
  }'
```

### Submit Approval
```bash
curl -X POST http://localhost:8000/approve \
  -H "Content-Type: application/json" \
  -d '{
    "request_id": "approval_20260101_120000",
    "decision": "APPROVED"
  }'
```

## Architecture

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed multi-agent architecture documentation.

## License

MIT
```

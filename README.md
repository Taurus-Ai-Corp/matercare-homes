# MaterCare Homes

<p align="center">
  <img src="assets/logo.png" alt="MaterCare Homes" width="200"/>
</p>

<p align="center">
  <a href="https://github.com/Taurus-AI-Corp/matercare-homes">
    <img src="https://img.shields.io/badge/GitHub-MaterCare-red" alt="GitHub">
  </a>
  <a href="https://pypi.org/project/matercare-homes/">
    <img src="https://img.shields.io/badge/PyPI-v1.0.0-blue" alt="PyPI">
  </a>
  <a href="LICENSE">
    <img src="https://img.shields.io/badge/License-MIT-green" alt="License">
  </a>
  <a href="https://github.com/Taurus-AI-Corp/matercare-homes/actions">
    <img src="https://github.com/Taurus-AI-Corp/matercare-homes/workflows/CI/badge.svg" alt="CI">
  </a>
  <a href="https://github.com/Taurus-AI-Corp/matercare-homes/security">
    <img src="https://img.shields.io/badge/Security-HIPAA%20Ready-blue" alt="Security">
  </a>
  <a href="https://pypi.org/project/matercare-homes/">
    <img src="https://img.shields.io/badge/Enterprise-White--Label-blue" alt="Enterprise">
  </a>
</p>

> **The "Grandma Test" passed** - No smartphone required. Passive monitoring for elderly that informs caregivers.

## What is MaterCare Homes?

MaterCare Homes is an **AI-powered eldercare platform** designed for the 80% of seniors who don't use smartphones. It combines:

- 🤖 **Agentic AI** - Autonomous decision-making for eldercare
- 📄 **OCR** - Scan prescriptions, medical documents  
- 📚 **RAG** - Healthcare knowledge retrieval
- 📡 **IoT Sensors** - Passive monitoring (mmWave, PIR, door sensors)
- 🔔 **Alerts** - SMS/call to caregivers

### The Problem We Solve

| Traditional Eldercare Tech | MaterCare |
|---------------------------|-----------|
| Senior needs smartphone | Senior does NOTHING |
| Wearable required | Passive sensors |
| App complexity | Caregiver uses app |
| Reactive alerts | Proactive detection |
| Cloud-only | Edge processing |

## Features

### 1. AI Assistant
- Fine-tuned Llama for eldercare
- Answers: dementia, fall prevention, medications, nutrition
- Available via: API, MCP, Voice (Alexa/Google Home)

### 2. Care Plan Generator
- Personalized plans based on conditions
- Daily routines, medications, safety
- Emergency protocols

### 3. Passive Monitoring
- **mmWave Radar** - Fall detection, vital signs
- **PIR Motion** - Activity levels
- **Door Sensors** - Wandering detection
- **Pressure Mats** - Bed/chair occupancy

### 4. Alert System
- Real-time SMS/call to caregivers
- Severity-based routing
- Escalation protocols

### 5. Knowledge Base
- CDC, NIH guidelines
- Drug interactions
- Emergency protocols
- Custom source addition

## Quick Start

### Installation

```bash
pip install matercare-homes
```

### Python Usage

```python
from matercare import MaterCareLLM, SensorGateway, KnowledgeBase

# Chat with eldercare AI
llm = MaterCareLLM()
response = llm.chat("What are signs of dehydration in elderly?")
print(response)

# Set up sensors
gateway = SensorGateway("senior_01")
gateway.register_sensor("mmwave_01", "mmwave")
gateway.register_sensor("door_01", "door")

# Query knowledge base
kb = KnowledgeBase()
results = kb.retrieve("fall prevention")
```

### API Server

```bash
# Run API
matercare-api

# Or programmatically
from matercare.src.api import app
import uvicorn
uvicorn.run(app, port=8000)
```

### MCP Server (For AI Agents)

```bash
# Run MCP server
matercare-mcp

# Now connect Claude Code, Cursor, etc.
```

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    MATERCARE HOMES                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌──────────────┐     ┌──────────────┐     ┌──────────────┐  │
│   │   PASSIVE    │     │   AGENTIC    │     │   ALERT      │  │
│   │   SENSORS    │────▶│   AI CORE    │────▶│   SYSTEM      │  │
│   │              │     │              │     │              │  │
│   │  • mmWave    │     │  • OCR       │     │  • SMS       │  │
│   │  • Motion    │     │  • RAG       │     │  • Call      │  │
│   │  • Door      │     │  • LLM       │     │  • Push      │  │
│   └──────────────┘     └──────────────┘     └──────────────┘  │
│                                                                 │
│   ┌─────────────────────────────────────────────────────┐    │
│   │              MCP CONNECTOR (Plug & Play)            │    │
│   │  • Claude Code  • Cursor  • Copilot  • CrewAI    │    │
│   └─────────────────────────────────────────────────────┘    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Integration

### Connect to Any AI Agent

```python
from matercare.src.mcp import MaterCareMCP, MCPRequest

mcp = MaterCareMCP()

# Works with Claude Code, Cursor, Copilot, etc.
response = mcp.handle(MCPRequest(
    method="chat",
    params={"message": "Elder care advice"}
))
```

### REST API

```bash
# Chat
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Fall prevention tips"}'

# Care plan
curl -X POST http://localhost:8000/care-plan \
  -H "Content-Type: application/json" \
  -d '{"patient_name": "John", "conditions": ["diabetes"], "mobility": "ambulatory", "cognitive_status": "alert"}'

# Sensors
curl http://localhost:8000/sensors/status
```

### Add Custom Knowledge

```python
from matercare import KnowledgeBase, KnowledgeSource

kb = KnowledgeBase()
kb.add_source(KnowledgeSource(
    name="Custom Hospital Protocol",
    content="Our emergency protocol for...",
    source_type="manual"
))
```

## Hardware Setup

### Recommended Sensors

| Sensor | Purpose | Cost |
|--------|---------|------|
| HLK-LD2410 mmWave | Fall detection, vitals | $30 |
| HC-SR501 PIR | Motion detection | $5 |
| RC-51 Door | Wandering detection | $5 |
| Pressure Mat | Bed/chair occupancy | $25 |

### Raspberry Pi Setup

```bash
# Install
pip install matercare-homes

# Run sensor gateway
python -m matercare.sensors.gateway --senior-id "dad"
```

## Environment Variables

```bash
# .env
MATERCARE_MODEL=Taurus-AI-Corp/matercare-llama-3.2-3b
HUGGINGFACE_API_TOKEN=your_token
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_PHONE_NUMBER=+1234567890
ALERT_PHONE_NUMBER=+0987654321
DATABASE_URL=postgresql://...
```

## Documentation

- [Implementation Plan](docs/IMPLEMENTATION_PLAN.md)
- [Tech Stack Research](docs/TECH_STACK_RESEARCH.md)
- [API Reference](docs/API.md)
- [Sensor Integration](docs/SENSORS.md)

## Roadmap

- [ ] V1.0 - Core AI + RAG + Sensors
- [ ] V1.1 - Voice integration (Alexa/Google)
- [ ] V1.2 - Mobile caregiver app
- [ ] V2.0 - Enterprise multi-tenant
- [ ] V2.1 - Hardware companion device

## License

MIT License - see [LICENSE](LICENSE)

## Author

**TAURUS AI Corp** - Quantum-Resistant Fintech & Eldercare Platform

- Website: https://q-grid.taurusai.io
- GitHub: https://github.com/Taurus-AI-Corp
- HuggingFace: https://huggingface.co/Taurus-AI-Corp

---

<p align="center">
Made with ❤️ for our grandparents
</p>

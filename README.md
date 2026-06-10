# Eldercare AI Platform

<p align="center">
  <img src="assets/logo.png" alt="Eldercare AI Platform" width="200"/>
</p>

<p align="center">
  <a href="https://github.com/Taurus-AI-Corp/eldcare-ai-platform">
    <img src="https://img.shields.io/badge/GitHub-Eldercare-red" alt="GitHub">
  </a>
  <a href="https://pypi.org/project/eldcare-ai-platform/">
    <img src="https://img.shields.io/badge/PyPI-v1.0.0-blue" alt="PyPI">
  </a>
  <a href="LICENSE">
    <img src="https://img.shields.io/badge/License-MIT-green" alt="License">
  </a>
  <a href="https://github.com/Taurus-AI-Corp/eldcare-ai-platform/actions">
    <img src="https://github.com/Taurus-AI-Corp/eldcare-ai-platform/workflows/CI/badge.svg" alt="CI">
  </a>
  <a href="https://github.com/Taurus-AI-Corp/eldcare-ai-platform/security">
    <img src="https://img.shields.io/badge/Security-HIPAA%20Ready-blue" alt="Security">
  </a>
</p>

> **The "Grandma Test" passed** - No smartphone required. Passive monitoring for elderly that informs caregivers.

## What is Eldercare AI Platform?

Eldercare AI Platform is an **AI-powered eldercare platform** designed for the 80% of seniors who don't use smartphones. It combines:

- 🤖 **Agentic AI** - Autonomous decision-making via 6-phase Care Loop
- 📄 **OCR** - Scan prescriptions, medical documents  
- 📚 **RAG** - Healthcare knowledge retrieval
- 📡 **IoT Sensors** - Passive monitoring (mmWave, PIR, door sensors)
- 🔔 **Alerts** - SMS/call to caregivers

### The Problem We Solve

| Traditional Eldercare Tech | Eldercare AI |
|---------------------------|--------------|
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
pip install eldcare-ai-platform
```

### CLI Usage

```bash
# Show version
eldcare-cli version

# Start API server
eldcare-cli api --port 8000

# Start MCP server
eldcare-cli mcp --port 9000

# Run care loop orchestrator
eldcare-cli orchestrator --senior-id "john_doe" --heart-rate 72

# Chat with AI
eldcare-cli chat "What are fall prevention tips?"

# Generate care plan
eldcare-cli care-plan --patient "John" --conditions diabetes,hypertension

# Query knowledge base
eldcare-cli knowledge "fall prevention" --k 5

# Check sensor status
eldcare-cli sensors status --senior-id "john_doe"
```

### Python Usage

```python
from eldcare_cli import run_orchestrator
from eldcare_src.model import MaterCareLLM
from eldcare_src.sensors import SensorGateway
from eldcare_src.rag import KnowledgeBase

# Chat with eldercare AI
llm = MaterCareLLM()
response = llm.chat("What are signs of dehydration in elderly?")
print(response)

# Set up sensors
gateway = SensorGateway("senior_01")
gateway.register_sensor("mmwave_01", "mmwave")

# Query knowledge base
kb = KnowledgeBase()
results = kb.retrieve("fall prevention")
```

### API Server

```bash
# Run API (new way)
eldcare-cli api --port 8000

# Or programmatic
from eldcare_cli.api_server import main
main()
```

### MCP Server (For AI Agents)

```bash
# Run MCP server (new way)
eldcare-cli mcp --port 9000
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

## 6-Phase Care Loop Orchestrator

MaterCare features a **novel 6-phase orchestration** that no competitor has:

### Phase 1: SENSE - Collect all data sources
- IoT sensor data (mmWave, PIR, door)
- Voice input
- Documents/prescriptions
- Historical care data

### Phase 2: THINK - Multi-agent analysis
- **TriageAgent**: Overall condition assessment
- **MedicationAgent**: Drug interactions & adherence
- **VitalAgent**: Heart rate, breathing, temperature
- **CognitiveAgent**: Mental status evaluation
- **ActivityAgent**: Daily patterns
- **SocialAgent**: Engagement monitoring
- **EmergencyAgent**: Critical condition detection
- **NutritionAgent**: Dietary needs

### Phase 3: PLAN - Generate care recommendations
Synthesize all agent analyses into actionable recommendations.

### Phase 4: ACT - Execute actions
- Send alerts
- Update care plans
- Trigger interventions

### Phase 5: LEARN - Feedback loop
Learn from outcomes to improve future recommendations.

### Phase 6: REPORT - Notify stakeholders
- Family members
- Caregivers
- Healthcare providers

### Using the Orchestrator

```python
from matercare.src.orchestration import MaterCareOrchestrator
from matercare.src.orchestration.agents import get_care_agent

# Create orchestrator
orchestrator = MaterCareOrchestrator()

# Register care agents
orchestrator.register_agent("triage_agent", get_care_agent("triage"))
orchestrator.register_agent("medication_agent", get_care_agent("medication"))
orchestrator.register_agent("emergency_agent", get_care_agent("emergency"))
orchestrator.register_agent("vital_agent", get_care_agent("vital"))
orchestrator.register_agent("cognitive_agent", get_care_agent("cognitive"))

# Execute care loop
result = await orchestrator.care_loop("senior_123", {
    "sensors": {
        "motion": True,
        "fall": False,
        "heart_rate": 72,
        "temperature": 36.5
    },
    "voice": "I'm feeling tired today"
})

print(f"Priority: {result.priority}")
print(f"Recommendation: {result.recommendation}")
print(f"Actions: {result.actions}")
```

### MCP Server for External Agents

The MCP server exposes MaterCare to external AI agents:

```bash
# Run MCP server
python -m matercare.src.orchestration.mcp_server

# Or run directly
python matercare/src/orchestration/mcp_server.py
```

Available tools:
- `care_loop` - Execute full 6-phase care loop
- `assess_senior` - Get comprehensive assessment
- `check_emergency` - Check for emergencies
- `review_medications` - Review drugs for interactions
- `register_senior` - Register new senior
- `notify_family` - Send family notifications
- `get_knowledge` - Query knowledge base
- `get_care_history` - Get historical data

### Connect to TAURUS Platform MCPs

```python
from matercare.src.orchestration.integrations import create_connector

# Create connector to TAURUS MCPs
connector = await create_connector()

# Use MCP bridge for eldercare-specific operations
bridge = MaterCareMCPBridge(connector)

# Notify family via email, SMS, WhatsApp, Slack
await bridge.notify_family(
    senior_name="John Smith",
    message="Fall detected - please check in",
    priority="urgent",
    channels=["email", "sms", "whatsapp"]
)

# Schedule caregiver visit
from datetime import datetime
await bridge.schedule_caregiver_visit(
    senior_name="John Smith",
    caregiver_name="Mary",
    scheduled_time=datetime(2026, 2, 28, 10, 0),
    notes="Regular wellness check"
)
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

# MaterCare Homes - Skill for AI Agents
# =========================================

## Skill Overview

This skill enables AI agents (Claude Code, Cursor, Copilot, etc.) to interact with the MaterCare Eldercare Platform.

## Capabilities

### 1. Chat with Eldercare AI
```
Query eldercare questions and get AI-powered responses.

Parameters:
- message: str - The question to ask
- model: str (optional) - Model path

Returns: AI response with eldercare information
```

### 2. Generate Care Plans
```
Create personalized care plans for elderly patients.

Parameters:
- patient_name: str
- conditions: List[str] - Medical conditions
- mobility: str - "ambulatory", "wheelchair", "bedridden"
- cognitive_status: str - "alert", "mild_impairment", "dementia"

Returns: Comprehensive care plan
```

### 3. Sensor Management
```
Register and monitor IoT sensors for elderly monitoring.

Actions:
- status: Get all sensor status
- register: Register new sensor
- event: Process sensor event

Sensor Types:
- mmwave: Fall detection radar
- pir: Motion detection
- door: Door sensor
- pressure: Pressure mat
- vital: Vital sign monitor
```

### 4. Alert Processing
```
Process and respond to eldercare alerts.

Alert Types:
- fall: Fall detected
- no_movement: Extended no movement
- vital_abnormal: Abnormal vitals
- door_open: Door opened
- medication_missed: Medication not taken

Severity Levels:
- low, medium, high, critical
```

### 5. Knowledge Base
```
Query healthcare knowledge base or add new sources.

Actions:
- query: Search for relevant information
- add: Add new knowledge source

Sources:
- CDC guidelines
- NIH resources
- Drug interactions
- Care protocols
```

## Integration Examples

### Python Integration
```python
from matercare import MaterCareMCP

mcp = MaterCareMCP()

# Chat
response = mcp.handle(MCPRequest(
    method="chat",
    params={"message": "What are signs of dehydration in elderly?"}
))

# Generate care plan
plan = mcp.handle(MCPRequest(
    method="care_plan",
    params={
        "patient_name": "John Smith",
        "conditions": ["diabetes", "hypertension"],
        "mobility": "ambulatory",
        "cognitive_status": "alert"
    }
))

# Query knowledge
info = mcp.handle(MCPRequest(
    method="knowledge",
    params={"action": "query", "query": "fall prevention"}
))
```

### MCP Protocol (JSON-RPC)
```json
{
  "method": "chat",
  "params": {
    "message": "What are warning signs of stroke?"
  },
  "id": "1"
}
```

### cURL
```bash
# Chat
curl -X POST http://localhost:9000/mcp \
  -H "Content-Type: application/json" \
  -d '{"method": "chat", "params": {"message": "Elderly nutrition tips"}}'

# Health check
curl http://localhost:9000/mcp
```

## Supported AI Platforms

| Platform | Integration |
|----------|-------------|
| Claude Code | MCP Server |
| Cursor | MCP Server |
| GitHub Copilot | MCP Server |
| OpenAI Agents | REST API |
| CrewAI | Python SDK |
| LangGraph | Python SDK |

## Alert Callbacks

Register callbacks for real-time alerts:

```python
gateway = SensorGateway("senior_01")

def on_alert(alert):
    # Send SMS, call, push notification
    send_sms(alert.message)
    call_caregiver(alert)

gateway.on_alert(on_alert)
```

---

*For more info: https://github.com/Taurus-AI-Corp/matercare-homes*

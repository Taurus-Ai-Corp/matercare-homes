"""
MaterCare Homes - MCP Server for External Agents
=================================================
This MCP server exposes MaterCare's care orchestration to external AI agents
(Claude Code, Cursor, Copilot, etc.) via the Model Context Protocol.

Usage:
    python -m src.orchestration.mcp_server
    
Or run directly:
    python src/orchestration/mcp_server.py
"""

from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
import json
import logging
import asyncio
import os
import sys

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
import uvicorn

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from orchestration import (
    MaterCareOrchestrator,
    CarePhase,
    EmergencyLevel,
    SeniorContext,
    SensorData,
    CareRecommendation,
    CareOutcome,
)
from orchestration.agents import (
    get_care_agent,
    TriageAgent,
    MedicationAgent,
    EmergencyAgent,
    CognitiveAgent,
    NutritionAgent,
)
from orchestration.integrations.platform_connector import (
    PlatformConnector,
    MaterCareMCPBridge,
    create_connector,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class MCPTool:
    """MCP Tool definition."""
    
    def __init__(
        self,
        name: str,
        description: str,
        input_schema: Dict,
        handler: callable
    ):
        self.name = name
        self.description = description
        self.input_schema = input_schema
        self.handler = handler


class MCPServer:
    """
    MCP Server for MaterCare Homes.
    
    Exposes care orchestration tools to external AI agents.
    """
    
    def __init__(self):
        self.orchestrator = MaterCareOrchestrator()
        self.platform_connector: Optional[PlatformConnector] = None
        self.mcp_bridge: Optional[MaterCareMCPBridge] = None
        self.seniors: Dict[str, SeniorContext] = {}
        self.tools = self._register_tools()
        self._init_agents()
    
    def _init_agents(self):
        """Initialize care agents."""
        self.orchestrator.register_agent("triage_agent", get_care_agent("triage"))
        self.orchestrator.register_agent("medication_agent", get_care_agent("medication"))
        self.orchestrator.register_agent("emergency_agent", get_care_agent("emergency"))
        self.orchestrator.register_agent("cognitive_agent", get_care_agent("cognitive"))
        self.orchestrator.register_agent("nutrition_agent", get_care_agent("nutrition"))
        logger.info("Care agents initialized")
    
    def _register_tools(self) -> List[MCPTool]:
        """Register all MCP tools."""
        return [
            MCPTool(
                name="care_loop",
                description="Execute the full 6-phase care loop for a senior",
                input_schema={
                    "type": "object",
                    "properties": {
                        "senior_id": {"type": "string", "description": "Unique senior identifier"},
                        "sensor_data": {
                            "type": "object",
                            "description": "IoT sensor readings",
                            "properties": {
                                "motion": {"type": "boolean"},
                                "fall": {"type": "boolean"},
                                "heart_rate": {"type": "number"},
                                "breathing_rate": {"type": "number"},
                                "temperature": {"type": "number"},
                            }
                        },
                        "voice_input": {"type": "string", "description": "Voice transcript"},
                    },
                    "required": ["senior_id"]
                },
                handler=self._tool_care_loop
            ),
            MCPTool(
                name="assess_senior",
                description="Get comprehensive assessment of a senior's current status",
                input_schema={
                    "type": "object",
                    "properties": {
                        "senior_id": {"type": "string"},
                    },
                    "required": ["senior_id"]
                },
                handler=self._tool_assess_senior
            ),
            MCPTool(
                name="check_emergency",
                description="Check for emergency conditions and trigger protocols if needed",
                input_schema={
                    "type": "object",
                    "properties": {
                        "senior_id": {"type": "string"},
                        "sensor_data": {"type": "object"},
                    },
                    "required": ["senior_id"]
                },
                handler=self._tool_check_emergency
            ),
            MCPTool(
                name="review_medications",
                description="Review medications for interactions and adherence",
                input_schema={
                    "type": "object",
                    "properties": {
                        "senior_id": {"type": "string"},
                        "medications": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["senior_id"]
                },
                handler=self._tool_review_medications
            ),
            MCPTool(
                name="register_senior",
                description="Register a new senior in the care system",
                input_schema={
                    "type": "object",
                    "properties": {
                        "senior_id": {"type": "string"},
                        "name": {"type": "string"},
                        "age": {"type": "number"},
                        "conditions": {"type": "array", "items": {"type": "string"}},
                        "medications": {"type": "array", "items": {"type": "string"}},
                        "mobility": {"type": "string", "enum": ["ambulatory", "wheelchair", "bedridden"]},
                        "emergency_contacts": {"type": "array"},
                    },
                    "required": ["senior_id", "name", "age"]
                },
                handler=self._tool_register_senior
            ),
            MCPTool(
                name="notify_family",
                description="Send notification to family members via multiple channels",
                input_schema={
                    "type": "object",
                    "properties": {
                        "senior_id": {"type": "string"},
                        "message": {"type": "string"},
                        "priority": {"type": "string", "enum": ["normal", "high", "urgent"]},
                        "channels": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["senior_id", "message"]
                },
                handler=self._tool_notify_family
            ),
            MCPTool(
                name="get_knowledge",
                description="Query the eldercare knowledge base for best practices",
                input_schema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "k": {"type": "number", "default": 3},
                    },
                    "required": ["query"]
                },
                handler=self._tool_get_knowledge
            ),
            MCPTool(
                name="get_care_history",
                description="Get historical care data for a senior",
                input_schema={
                    "type": "object",
                    "properties": {
                        "senior_id": {"type": "string"},
                        "days": {"type": "number", "default": 7},
                    },
                    "required": ["senior_id"]
                },
                handler=self._tool_get_care_history
            ),
        ]
    
    async def _tool_care_loop(self, params: Dict) -> Dict:
        """Execute care loop tool."""
        senior_id = params["senior_id"]
        input_data = {
            "sensors": params.get("sensor_data", {}),
            "voice": params.get("voice_input", ""),
        }
        
        result = await self.orchestrator.care_loop(senior_id, input_data)
        
        return {
            "senior_id": senior_id,
            "recommendation": result.recommendation,
            "priority": result.priority.value,
            "actions": result.actions,
            "confidence": result.confidence,
            "agents_used": result.agents_used,
        }
    
    async def _tool_assess_senior(self, params: Dict) -> Dict:
        """Assess senior tool."""
        senior_id = params["senior_id"]
        
        sensor_data = {
            "senior_id": senior_id,
            "timestamp": datetime.now(),
            "motion_detected": True,
        }
        
        input_data = {"sensors": sensor_data}
        
        triage = await self.orchestrator.agents["triage_agent"].analyze({
            "sources": {
                "sensors": sensor_data,
                "history": {"past_recommendations": []},
                "voice": {},
                "documents": {}
            }
        })
        
        return {
            "senior_id": senior_id,
            "assessment": triage,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _tool_check_emergency(self, params: Dict) -> Dict:
        """Check emergency tool."""
        senior_id = params["senior_id"]
        sensor_data = params.get("sensor_data", {})
        
        result = await self.orchestrator.agents["emergency_agent"].analyze({
            "sources": {
                "sensors": sensor_data,
                "history": {},
                "voice": {},
                "documents": {}
            }
        })
        
        if result.get("level") == "critical":
            await self.orchestrator.agents["emergency_agent"].trigger_critical(
                senior_id, result
            )
        
        return {
            "senior_id": senior_id,
            "emergency_detected": result.get("emergency_detected", False),
            "type": result.get("emergency_type"),
            "level": result.get("level"),
            "actions": result.get("actions", []),
        }
    
    async def _tool_review_medications(self, params: Dict) -> Dict:
        """Review medications tool."""
        senior_id = params["senior_id"]
        medications = params.get("medications", [])
        
        result = await self.orchestrator.agents["medication_agent"].analyze({
            "context": {"medications": medications},
            "sources": {
                "sensors": {},
                "history": {},
                "voice": {},
                "documents": {}
            }
        })
        
        return {
            "senior_id": senior_id,
            "medications": medications,
            "interactions": result.get("interactions", []),
            "adherence_score": result.get("adherence_score"),
            "issues": result.get("issues", []),
            "recommendation": result.get("recommendation"),
        }
    
    async def _tool_register_senior(self, params: Dict) -> Dict:
        """Register senior tool."""
        senior = SeniorContext(
            senior_id=params["senior_id"],
            name=params["name"],
            age=params["age"],
            conditions=params.get("conditions", []),
            medications=params.get("medications", []),
            mobility=params.get("mobility", "ambulatory"),
            emergency_contacts=params.get("emergency_contacts", [])
        )
        
        self.seniors[senior.senior_id] = senior
        
        return {
            "status": "registered",
            "senior_id": senior.senior_id,
            "name": senior.name,
            "age": senior.age,
            "conditions": senior.conditions,
        }
    
    async def _tool_notify_family(self, params: Dict) -> Dict:
        """Notify family tool."""
        if not self.mcp_bridge:
            self.platform_connector = await create_connector()
            self.mcp_bridge = MaterCareMCPBridge(self.platform_connector)
        
        senior_id = params["senior_id"]
        senior = self.seniors.get(senior_id)
        
        result = await self.mcp_bridge.notify_family(
            senior_name=senior.name if senior else "Senior",
            message=params["message"],
            priority=params.get("priority", "normal"),
            channels=params.get("channels", ["email"])
        )
        
        return {
            "status": "notified",
            "senior_id": senior_id,
            "channels": result,
        }
    
    async def _tool_get_knowledge(self, params: Dict) -> Dict:
        """Get knowledge tool."""
        return {
            "query": params["query"],
            "results": [
                {"content": "Sample knowledge: Monitor seniors for fall risk factors.", "source": "guidelines", "score": 0.95},
                {"content": "Best practice: Check vital signs every 4 hours for at-risk seniors.", "source": "protocols", "score": 0.88},
            ],
            "k": params.get("k", 3),
        }
    
    async def _tool_get_care_history(self, params: Dict) -> Dict:
        """Get care history tool."""
        return {
            "senior_id": params["senior_id"],
            "days": params.get("days", 7),
            "history": [
                {"date": "2026-02-27", "type": "triage", "result": "low_priority"},
                {"date": "2026-02-26", "type": "medication", "result": "adherence_95%"},
            ]
        }
    
    async def handle_request(self, method: str, params: Dict) -> Dict:
        """Handle incoming MCP request."""
        logger.info(f"MCP Request: {method}")
        
        for tool in self.tools:
            if tool.name == method:
                result = await tool.handler(params)
                return {"result": result, "error": None}
        
        raise ValueError(f"Unknown method: {method}")
    
    def get_tools(self) -> List[Dict]:
        """Get list of available tools."""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.input_schema,
            }
            for tool in self.tools
        ]


app = FastAPI(title="MaterCare MCP Server", version="1.0.0")

mcp_server = MCPServer()


@app.get("/")
async def root():
    return {
        "service": "MaterCare MCP Server",
        "version": "1.0.0",
        "status": "running",
        "tools_count": len(mcp_server.tools),
    }


@app.get("/tools")
async def list_tools():
    """List all available MCP tools."""
    return {"tools": mcp_server.get_tools()}


@app.post("/mcp")
async def mcp_endpoint(request: Request):
    """MCP protocol endpoint."""
    body = await request.json()
    
    method = body.get("method")
    params = body.get("params", {})
    
    try:
        result = await mcp_server.handle_request(method, params)
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"MCP error: {e}")
        return JSONResponse(
            content={"result": None, "error": str(e)},
            status_code=500
        )


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "MaterCare MCP",
        "version": "1.0.0",
        "agents": list(mcp_server.orchestrator.agents.keys()),
        "seniors_registered": len(mcp_server.seniors),
    }


@app.get("/seniors")
async def list_seniors():
    """List all registered seniors."""
    return {
        "seniors": [
            asdict(senior)
            for senior in mcp_server.seniors.values()
        ]
    }


@app.post("/seniors")
async def register_senior(senior: SeniorContext):
    """Register a new senior."""
    mcp_server.seniors[senior.senior_id] = senior
    return {"status": "registered", "senior_id": senior.senior_id}


def run_server(host: str = "0.0.0.0", port: int = 9000):
    """Run the MCP server."""
    logger.info(f"Starting MaterCare MCP Server on {host}:{port}")
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run_server()

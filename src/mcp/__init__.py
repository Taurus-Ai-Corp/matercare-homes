"""
MaterCare Homes - MCP Server
============================
Model Context Protocol server for integrating with any AI agent system.
This enables MaterCare to be connected to Claude Code, Cursor, Copilot, etc.
"""

from typing import Any, Dict, List, Optional
import json
import logging
from dataclasses import dataclass, asdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class MCPRequest:
    """MCP request format."""
    method: str
    params: Dict[str, Any]
    id: Optional[str] = None


@dataclass
class MCPResponse:
    """MCP response format."""
    result: Any
    error: Optional[str] = None
    id: Optional[str] = None


class MaterCareMCP:
    """MCP server for MaterCare integration."""
    
    def __init__(self):
        self.handlers = {
            "chat": self._handle_chat,
            "care_plan": self._handle_care_plan,
            "sensors": self._handle_sensors,
            "alert": self._handle_alert,
            "knowledge": self._handle_knowledge,
            "health": self._handle_health,
        }
    
    def handle(self, request: MCPRequest) -> MCPResponse:
        """Handle incoming MCP request."""
        try:
            handler = self.handlers.get(request.method)
            if not handler:
                return MCPResponse(
                    error=f"Unknown method: {request.method}",
                    id=request.id
                )
            
            result = handler(request.params)
            return MCPResponse(result=result, id=request.id)
        
        except Exception as e:
            logger.error(f"MCP error: {e}")
            return MCPResponse(error=str(e), id=request.id)
    
    def _handle_chat(self, params: Dict) -> Dict:
        """Handle chat request."""
        from .model import MaterCareLLM
        
        message = params.get("message", "")
        model_path = params.get("model", "Taurus-AI-Corp/matercare-llama-3.2-3b")
        
        llm = MaterCareLLM(model_path=model_path)
        response = llm.chat(message)
        
        return {"response": response, "model": model_path}
    
    def _handle_care_plan(self, params: Dict) -> Dict:
        """Handle care plan generation."""
        from .model import MaterCareLLM, CarePlanGenerator
        
        llm = MaterCareLLM()
        generator = CarePlanGenerator(llm)
        
        plan = generator.generate(
            patient_name=params.get("patient_name", "Patient"),
            conditions=params.get("conditions", []),
            mobility=params.get("mobility", "ambulatory"),
            cognitive_status=params.get("cognitive_status", "alert")
        )
        
        return plan
    
    def _handle_sensors(self, params: Dict) -> Dict:
        """Handle sensor operations."""
        from .sensors import SensorGateway
        
        action = params.get("action", "status")
        
        if action == "status":
            gateway = SensorGateway(params.get("senior_id", "default"))
            return gateway.get_status()
        
        elif action == "register":
            gateway = SensorGateway(params.get("senior_id", "default"))
            gateway.register_sensor(
                params["sensor_id"],
                params["sensor_type"],
                params.get("config", {})
            )
            return {"status": "registered", "sensor_id": params["sensor_id"]}
        
        return {"error": "Unknown sensor action"}
    
    def _handle_alert(self, params: Dict) -> Dict:
        """Handle alert processing."""
        from .sensors import SensorGateway, Alert, AlertType, AlertSeverity
        
        gateway = SensorGateway(params.get("senior_id", "default"))
        
        alert = Alert(
            alert_id=params.get("alert_id", "manual_alert"),
            senior_id=params.get("senior_id", "default"),
            alert_type=AlertType(params.get("alert_type", "fall")),
            severity=AlertSeverity(params.get("severity", "high")),
            message=params.get("message", ""),
            sensor_id=params.get("sensor_id", "manual"),
            timestamp=0
        )
        
        gateway._trigger_alert(alert)
        
        return {"status": "alert_processed", "alert_id": alert.alert_id}
    
    def _handle_knowledge(self, params: Dict) -> Dict:
        """Handle knowledge base queries."""
        from .rag import KnowledgeBase
        
        action = params.get("action", "query")
        
        kb = KnowledgeBase()
        
        if action == "query":
            results = kb.retrieve(params.get("query", ""), params.get("k", 3))
            return {
                "results": [
                    {"content": r.content, "source": r.source, "score": r.score}
                    for r in results
                ]
            }
        
        elif action == "add":
            from .rag import KnowledgeSource
            source = KnowledgeSource(
                name=params["name"],
                content=params["content"],
                source_type=params.get("source_type", "manual")
            )
            kb.add_source(source)
            return {"status": "source_added", "name": params["name"]}
        
        return {"error": "Unknown knowledge action"}
    
    def _handle_health(self, params: Dict) -> Dict:
        """Health check endpoint."""
        return {
            "status": "healthy",
            "service": "MaterCare MCP",
            "version": "1.0.0"
        }


def run_mcp_server(host: str = "0.0.0.0", port: int = 9000):
    """Run MCP server."""
    import http.server
    import socketserver
    
    mcp = MaterCareMCP()
    
    class MCPHandler(http.server.BaseHTTPRequestHandler):
        def do_POST(self):
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            request = json.loads(body)
            
            mcp_request = MCPRequest(
                method=request.get("method"),
                params=request.get("params", {}),
                id=request.get("id")
            )
            
            response = mcp.handle(mcp_request)
            
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(asdict(response)).encode())
        
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "MaterCare MCP running"}).encode())
    
    with socketserver.TCPServer((host, port), MCPHandler) as httpd:
        logger.info(f"MCP server running on {host}:{port}")
        httpd.serve_forever()


if __name__ == "__main__":
    run_mcp_server()

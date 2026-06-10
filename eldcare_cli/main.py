#!/usr/bin/env python3
"""
Eldercare AI Platform - CLI
============================
Command-line interface for the Eldercare AI Platform.

Usage:
    eldcare-cli --help
    eldcare-cli api --port 8000
    eldcare-cli mcp --port 9000
    eldcare-cli orchestrator --senior-id "john_doe"
    eldcare-cli chat "What are fall prevention tips?"
    eldcare-cli care-plan --patient "John" --conditions diabetes,hypertension
    eldcare-cli sensors status
    eldcare-cli version
"""

import argparse
import asyncio
import sys
import os
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def print_banner():
    """Print ASCII banner."""
    banner = """
╔═══════════════════════════════════════════════════════════╗
║     🤖 ELDCARE AI PLATFORM v1.0.0                         ║
║     AI-Powered Eldercare with 6-Phase Care Loop          ║
║     (c) 2026 TAURUS AI Corp                              ║
╚═══════════════════════════════════════════════════════════╝
    """
    print(banner)


def cmd_version(args):
    """Print version info."""
    print("Eldercare AI Platform v1.0.0")
    print("Python:", sys.version.split()[0])
    print("Location:", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def cmd_api(args):
    """Start API server."""
    from src.api import app
    import uvicorn
    
    print_banner()
    print(f"🚀 Starting API server on port {args.port}...")
    uvicorn.run(app, host=args.host, port=args.port, reload=args.reload)


def cmd_mcp(args):
    """Start MCP server."""
    from src.orchestration.mcp_server import run_server
    
    print_banner()
    print(f"🔌 Starting MCP server on port {args.port}...")
    run_server(host=args.host, port=args.port)


def cmd_orchestrator(args):
    """Run care loop orchestrator."""
    from src.orchestration import MaterCareOrchestrator
    from src.orchestration.agents import get_care_agent
    
    async def run():
        print_banner()
        print(f"🎯 Starting Care Loop for senior: {args.senior_id}")
        
        orchestrator = MaterCareOrchestrator()
        
        agents = ["triage", "medication", "emergency", "vital", "cognitive", "activity", "social", "nutrition"]
        for agent_type in agents:
            try:
                orchestrator.register_agent(f"{agent_type}_agent", get_care_agent(agent_type))
                print(f"  ✓ Registered {agent_type} agent")
            except Exception as e:
                print(f"  ✗ Failed to register {agent_type}: {e}")
        
        sensor_data = {
            "motion": True,
            "fall": False,
            "heart_rate": args.heart_rate or 72,
            "temperature": args.temperature or 36.5,
        }
        
        result = await orchestrator.care_loop(args.senior_id, {"sensors": sensor_data})
        
        print(f"\n📋 Results:")
        print(f"   Priority: {result.priority.value}")
        print(f"   Recommendation: {result.recommendation[:100]}...")
        print(f"   Actions: {', '.join(result.actions)}")
        print(f"   Confidence: {result.confidence:.2f}")
        
    asyncio.run(run())


def cmd_chat(args):
    """Chat with Eldercare AI."""
    from src.model import MaterCareLLM
    
    print_banner()
    print(f"💬 You: {args.message}")
    
    llm = MaterCareLLM()
    response = llm.chat(args.message)
    
    print(f"🤖 Eldercare AI: {response}")


def cmd_care_plan(args):
    """Generate care plan."""
    from src.model import MaterCareLLM, CarePlanGenerator
    
    print_banner()
    print(f"📝 Generating care plan for: {args.patient}")
    
    llm = MaterCareLLM()
    generator = CarePlanGenerator(llm)
    
    conditions = args.conditions.split(",") if args.conditions else []
    
    plan = generator.generate(
        patient_name=args.patient,
        conditions=conditions,
        mobility=args.mobility or "ambulatory",
        cognitive_status=args.cognitive or "alert"
    )
    
    print(f"\n📋 Care Plan:")
    print(plan)


def cmd_sensors(args):
    """Sensor operations."""
    from src.sensors import SensorGateway
    
    gateway = SensorGateway(args.senior_id or "default")
    
    if args.action == "status":
        status = gateway.get_status()
        print(f"\n📡 Sensor Status for {args.senior_id or 'default'}:")
        for key, value in status.items():
            print(f"   {key}: {value}")
    elif args.action == "register":
        gateway.register_sensor(args.sensor_id, args.sensor_type)
        print(f"✓ Registered sensor: {args.sensor_id} ({args.sensor_type})")


def cmd_knowledge(args):
    """Query knowledge base."""
    from src.rag import KnowledgeBase
    
    print_banner()
    print(f"🔍 Searching: {args.query}")
    
    kb = KnowledgeBase()
    results = kb.retrieve(args.query, k=args.k or 3)
    
    print(f"\n📚 Results ({len(results)} found):")
    for i, r in enumerate(results, 1):
        print(f"\n{i}. [{r.source}] (score: {r.score:.2f})")
        print(f"   {r.content[:200]}...")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="eldcare-cli",
        description="Eldercare AI Platform - CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  eldcare-cli version
  eldcare-cli api --port 8000
  eldcare-cli mcp --port 9000
  eldcare-cli orchestrator --senior-id "john_doe"
  eldcare-cli chat "What are fall prevention tips?"
  eldcare-cli care-plan --patient "John" --conditions diabetes
  eldcare-cli sensors status --senior-id "john_doe"
  eldcare-cli knowledge "fall prevention"
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    subparsers.add_parser("version", help="Show version info")
    
    parser_api = subparsers.add_parser("api", help="Start REST API server")
    parser_api.add_argument("--port", type=int, default=8000, help="Port (default: 8000)")
    parser_api.add_argument("--host", type=str, default="0.0.0.0", help="Host (default: 0.0.0.0)")
    parser_api.add_argument("--reload", action="store_true", help="Enable auto-reload")
    
    parser_mcp = subparsers.add_parser("mcp", help="Start MCP server")
    parser_mcp.add_argument("--port", type=int, default=9000, help="Port (default: 9000)")
    parser_mcp.add_argument("--host", type=str, default="0.0.0.0", help="Host (default: 0.0.0.0)")
    
    parser_orch = subparsers.add_parser("orchestrator", help="Run care loop orchestrator")
    parser_orch.add_argument("--senior-id", required=True, help="Senior ID")
    parser_orch.add_argument("--heart-rate", type=int, help="Heart rate")
    parser_orch.add_argument("--temperature", type=float, help="Body temperature")
    
    parser_chat = subparsers.add_parser("chat", help="Chat with Eldercare AI")
    parser_chat.add_argument("message", help="Message to send")
    
    parser_plan = subparsers.add_parser("care-plan", help="Generate care plan")
    parser_plan.add_argument("--patient", required=True, help="Patient name")
    parser_plan.add_argument("--conditions", help="Comma-separated conditions")
    parser_plan.add_argument("--mobility", help="Mobility status")
    parser_plan.add_argument("--cognitive", help="Cognitive status")
    
    parser_sensors = subparsers.add_parser("sensors", help="Sensor operations")
    parser_sensors.add_argument("action", choices=["status", "register"], help="Action")
    parser_sensors.add_argument("--senior-id", help="Senior ID")
    parser_sensors.add_argument("--sensor-id", help="Sensor ID (for register)")
    parser_sensors.add_argument("--sensor-type", help="Sensor type (for register)")
    
    parser_knowledge = subparsers.add_parser("knowledge", help="Query knowledge base")
    parser_knowledge.add_argument("query", help="Search query")
    parser_knowledge.add_argument("--k", type=int, help="Number of results")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    commands = {
        "version": cmd_version,
        "api": cmd_api,
        "mcp": cmd_mcp,
        "orchestrator": cmd_orchestrator,
        "chat": cmd_chat,
        "care-plan": cmd_care_plan,
        "sensors": cmd_sensors,
        "knowledge": cmd_knowledge,
    }
    
    cmd = commands.get(args.command)
    if cmd:
        cmd(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

"""Orchestrator entry point."""

import asyncio
import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.orchestration import MaterCareOrchestrator
from src.orchestration.agents import get_care_agent


async def run_care_loop(senior_id: str, sensor_data: dict):
    """Run the care loop for a senior."""
    print(f"🎯 Starting Care Loop for senior: {senior_id}")
    
    orchestrator = MaterCareOrchestrator()
    
    agents = ["triage", "medication", "emergency", "vital", "cognitive", "activity", "social", "nutrition"]
    for agent_type in agents:
        try:
            orchestrator.register_agent(f"{agent_type}_agent", get_care_agent(agent_type))
            print(f"  ✓ Registered {agent_type} agent")
        except Exception as e:
            print(f"  ✗ Failed to register {agent_type}: {e}")
    
    result = await orchestrator.care_loop(senior_id, {"sensors": sensor_data})
    
    print(f"\n📋 Results:")
    print(f"   Priority: {result.priority.value}")
    print(f"   Recommendation: {result.recommendation[:200]}")
    print(f"   Actions: {', '.join(result.actions)}")
    print(f"   Confidence: {result.confidence:.2f}")
    print(f"   Agents Used: {', '.join(result.agents_used)}")
    
    return result


def run():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Run Eldercare orchestrator")
    parser.add_argument("--senior-id", required=True, help="Senior ID")
    parser.add_argument("--heart-rate", type=int, help="Heart rate")
    parser.add_argument("--temperature", type=float, help="Body temperature")
    parser.add_argument("--motion", type=bool, default=True, help="Motion detected")
    parser.add_argument("--fall", type=bool, default=False, help="Fall detected")
    
    args = parser.parse_args()
    
    sensor_data = {
        "motion": args.motion,
        "fall": args.fall,
        "heart_rate": args.heart_rate or 72,
        "temperature": args.temperature or 36.5,
    }
    
    asyncio.run(run_care_loop(args.senior_id, sensor_data))


if __name__ == "__main__":
    run()

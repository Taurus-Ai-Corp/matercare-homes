"""
MaterCare Homes - Eldercare AI Platform
========================================
A plug-and-play eldercare AI system with OCR, Agentic AI, RAG, and IoT sensors.

Author: TAURUS AI Corp
License: MIT
GitHub: https://github.com/Taurus-AI-Corp/matercare-homes
"""

__version__ = "1.0.0"
__author__ = "TAURUS AI Corp"

# Import main components
from .model import MaterCareLLM, CarePlanGenerator, get_default_system_prompt
from .sensors import SensorGateway, Alert, AlertType, AlertSeverity, MockSensorEmulator
from .rag import KnowledgeBase, KnowledgeSource, RetrievedContext

__all__ = [
    # Model
    "MaterCareLLM",
    "CarePlanGenerator",
    "get_default_system_prompt",
    # Sensors
    "SensorGateway",
    "Alert",
    "AlertType", 
    "AlertSeverity",
    "MockSensorEmulator",
    # RAG
    "KnowledgeBase",
    "KnowledgeSource",
    "RetrievedContext",
    # Version
    "__version__",
]

"""
MaterCare Homes - FastAPI Backend
=================================
REST API for MaterCare Eldercare Platform.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
import logging

from ..model import MaterCareLLM, CarePlanGenerator, get_default_system_prompt

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="MaterCare Homes API",
    description="AI-powered eldercare assistance platform",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

llm: Optional[MaterCareLLM] = None


def get_llm() -> MaterCareLLM:
    global llm
    if llm is None:
        model_path = os.getenv("MATERCARE_MODEL", "Taurus-AI-Corp/matercare-llama-3.2-3b")
        llm = MaterCareLLM(model_path=model_path)
    return llm


class ChatRequest(BaseModel):
    message: str
    system_prompt: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    response: str
    sources: Optional[List[str]] = None
    model: str


class CarePlanRequest(BaseModel):
    patient_name: str
    conditions: List[str]
    mobility: str
    cognitive_status: str


class AlertRequest(BaseModel):
    sensor_id: str
    alert_type: str
    severity: str
    message: str
    senior_id: str


@app.get("/")
async def root():
    return {
        "service": "MaterCare Homes API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, model: MaterCareLLM = Depends(get_llm)):
    """Chat with MaterCare AI assistant."""
    try:
        system = request.system_prompt or get_default_system_prompt()
        response = model.chat(request.message, system_prompt=system)
        return ChatResponse(response=response, model=model.model_path)
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/care-plan")
async def create_care_plan(request: CarePlanRequest, model: MaterCareLLM = Depends(get_llm)):
    """Generate a personalized care plan."""
    try:
        generator = CarePlanGenerator(model)
        plan = generator.generate(
            patient_name=request.patient_name,
            conditions=request.conditions,
            mobility=request.mobility,
            cognitive_status=request.cognitive_status
        )
        return plan
    except Exception as e:
        logger.error(f"Care plan error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/alert")
async def receive_alert(request: AlertRequest):
    """Receive and process sensor alerts."""
    logger.warning(f"ALERT: {request.alert_type} - {request.message}")
    return {"status": "received", "alert_id": f"alert_{request.sensor_id}"}


@app.get("/sensors/status")
async def sensors_status():
    """Get status of all connected sensors."""
    return {
        "sensors": [
            {"id": "mmwave_01", "type": "mmwave", "status": "online"},
            {"id": "motion_01", "type": "pir", "status": "online"},
            {"id": "door_01", "type": "door", "status": "online"},
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

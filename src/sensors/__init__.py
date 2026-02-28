"""
MaterCare Homes - IoT Sensor Gateway
=====================================
Passive monitoring for elderly using mmWave radar, PIR, door sensors.
"""

from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import threading
import time
import json
import logging

logger = logging.getLogger(__name__)


class AlertSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertType(str, Enum):
    FALL = "fall"
    NO_MOVEMENT = "no_movement"
    VITAL_ABNORMAL = "vital_abnormal"
    DOOR_OPEN = "door_open"
    MEDICATION_MISSED = "medication_missed"
    WANDERING = "wandering"


@dataclass
class SensorEvent:
    sensor_id: str
    sensor_type: str
    event_type: str
    data: Dict
    timestamp: float


@dataclass
class Alert:
    alert_id: str
    senior_id: str
    alert_type: AlertType
    severity: AlertSeverity
    message: str
    sensor_id: str
    timestamp: float


class SensorGateway:
    """Central hub for all IoT sensors."""
    
    def __init__(self, senior_id: str = "default"):
        self.senior_id = senior_id
        self.sensors: Dict[str, Dict] = {}
        self.alert_callbacks: List[Callable[[Alert], None]] = []
        self.last_movement: Dict[str, float] = {}
        self.running = False
    
    def register_sensor(
        self,
        sensor_id: str,
        sensor_type: str,
        config: Optional[Dict] = None
    ):
        """Register a new sensor."""
        self.sensors[sensor_id] = {
            "type": sensor_type,
            "config": config or {},
            "status": "online",
            "registered_at": time.time()
        }
        logger.info(f"Registered sensor: {sensor_id} ({sensor_type})")
    
    def on_alert(self, callback: Callable[[Alert], None]):
        """Register alert callback."""
        self.alert_callbacks.append(callback)
    
    def _trigger_alert(self, alert: Alert):
        """Trigger alert to all callbacks."""
        logger.warning(f"ALERT [{alert.severity.value}]: {alert.message}")
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"Alert callback error: {e}")
    
    def process_event(self, event: SensorEvent):
        """Process incoming sensor event."""
        self.last_movement[event.sensor_id] = time.time()
        
        if event.event_type == "fall_detected":
            alert = Alert(
                alert_id=f"fall_{int(time.time())}",
                senior_id=self.senior_id,
                alert_type=AlertType.FALL,
                severity=AlertSeverity.CRITICAL,
                message="Fall detected! Immediate attention required.",
                sensor_id=event.sensor_id,
                timestamp=time.time()
            )
            self._trigger_alert(alert)
        
        elif event.event_type == "no_movement":
            alert = Alert(
                alert_id=f"nomove_{int(time.time())}",
                senior_id=self.senior_id,
                alert_type=AlertType.NO_MOVEMENT,
                severity=AlertSeverity.HIGH,
                message="No movement detected for extended period.",
                sensor_id=event.sensor_id,
                timestamp=time.time()
            )
            self._trigger_alert(alert)
        
        elif event.event_type == "vital_abnormal":
            alert = Alert(
                alert_id=f"vital_{int(time.time())}",
                senior_id=self.senior_id,
                alert_type=AlertType.VITAL_ABNORMAL,
                severity=AlertSeverity.MEDIUM,
                message=f"Abnormal vitals: {event.data}",
                sensor_id=event.sensor_id,
                timestamp=time.time()
            )
            self._trigger_alert(alert)
        
        elif event.event_type == "door_opened":
            alert = Alert(
                alert_id=f"door_{int(time.time())}",
                senior_id=self.senior_id,
                alert_type=AlertType.DOOR_OPEN,
                severity=AlertSeverity.LOW,
                message="Door opened - may indicate wandering.",
                sensor_id=event.sensor_id,
                timestamp=time.time()
            )
            self._trigger_alert(alert)
    
    def check_movement_timeout(self, timeout_seconds: int = 3600):
        """Check if no movement for specified timeout."""
        now = time.time()
        for sensor_id, last_time in self.last_movement.items():
            if now - last_time > timeout_seconds:
                event = SensorEvent(
                    sensor_id=sensor_id,
                    sensor_type="timeout_check",
                    event_type="no_movement",
                    data={"last_movement": last_time},
                    timestamp=now
                )
                self.process_event(event)
    
    def get_status(self) -> Dict:
        """Get gateway status."""
        return {
            "senior_id": self.senior_id,
            "sensors": self.sensors,
            "last_movement": self.last_movement,
            "registered_alerts": len(self.alert_callbacks)
        }


class MockSensorEmulator:
    """Emulate sensors for testing."""
    
    def __init__(self, gateway: SensorGateway):
        self.gateway = gateway
    
    def simulate_fall(self):
        event = SensorEvent(
            sensor_id="mmwave_01",
            sensor_type="mmwave",
            event_type="fall_detected",
            data={"confidence": 0.95},
            timestamp=time.time()
        )
        self.gateway.process_event(event)
    
    def simulate_no_movement(self):
        event = SensorEvent(
            sensor_id="motion_01",
            sensor_type="pir",
            event_type="no_movement",
            data={"duration_seconds": 7200},
            timestamp=time.time()
        )
        self.gateway.process_event(event)

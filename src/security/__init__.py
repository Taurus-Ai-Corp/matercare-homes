"""
MaterCare Homes - Security Module
================================
Enterprise-grade security with encryption, auth, and audit.
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime, timedelta
import hashlib
import secrets
import logging

logger = logging.getLogger(__name__)


@dataclass
class User:
    """User model with role-based access."""
    user_id: str
    email: str
    role: str  # "admin", "caregiver", "family", "senior"
    senior_id: Optional[str]
    created_at: datetime
    mfa_enabled: bool = False
    last_login: Optional[datetime] = None


@dataclass
class AuditLog:
    """Audit log entry."""
    log_id: str
    user_id: str
    action: str
    resource: str
    timestamp: datetime
    ip_address: Optional[str]
    success: bool


class SecurityManager:
    """Enterprise security manager."""
    
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.sessions: Dict[str, Dict] = {}
        self.api_keys: Dict[str, Dict] = {}
        self.audit_logs: List[AuditLog] = []
        self._encryption_key: Optional[bytes] = None
    
    def generate_api_key(self, user_id: str, name: str, permissions: List[str]) -> str:
        """Generate API key for enterprise access."""
        api_key = f"mckey_{secrets.token_urlsafe(32)}"
        
        self.api_keys[api_key] = {
            "user_id": user_id,
            "name": name,
            "permissions": permissions,
            "created_at": datetime.now(),
            "last_used": None,
            "active": True
        }
        
        self._log_audit(user_id, "CREATE_API_KEY", f"api_key:{name}", True)
        
        return api_key
    
    def verify_api_key(self, api_key: str) -> Optional[Dict]:
        """Verify API key and return permissions."""
        key_data = self.api_keys.get(api_key)
        
        if not key_data:
            return None
        
        if not key_data.get("active"):
            return None
        
        key_data["last_used"] = datetime.now()
        
        return {
            "user_id": key_data["user_id"],
            "permissions": key_data["permissions"]
        }
    
    def revoke_api_key(self, api_key: str, user_id: str) -> bool:
        """Revoke an API key."""
        if api_key in self.api_keys:
            self.api_keys[api_key]["active"] = False
            self._log_audit(user_id, "REVOKE_API_KEY", api_key, True)
            return True
        return False
    
    def create_session(
        self,
        user_id: str,
        ip_address: Optional[str] = None,
        device_info: Optional[Dict] = None
    ) -> str:
        """Create authenticated session."""
        session_token = secrets.token_urlsafe(32)
        
        self.sessions[session_token] = {
            "user_id": user_id,
            "created_at": datetime.now(),
            "expires_at": datetime.now() + timedelta(hours=24),
            "ip_address": ip_address,
            "device_info": device_info,
            "active": True
        }
        
        self._log_audit(user_id, "LOGIN", "session", True, ip_address)
        
        return session_token
    
    def verify_session(self, session_token: str) -> Optional[str]:
        """Verify session and return user_id."""
        session = self.sessions.get(session_token)
        
        if not session:
            return None
        
        if not session.get("active"):
            return None
        
        if session["expires_at"] < datetime.now():
            session["active"] = False
            return None
        
        return session["user_id"]
    
    def revoke_session(self, session_token: str, user_id: str):
        """Revoke a session."""
        if session_token in self.sessions:
            self.sessions[session_token]["active"] = False
            self._log_audit(user_id, "LOGOUT", "session", True)
    
    def _log_audit(
        self,
        user_id: str,
        action: str,
        resource: str,
        success: bool,
        ip_address: Optional[str] = None
    ):
        """Log audit event."""
        log = AuditLog(
            log_id=secrets.token_urlsafe(16),
            user_id=user_id,
            action=action,
            resource=resource,
            timestamp=datetime.now(),
            ip_address=ip_address,
            success=success
        )
        self.audit_logs.append(log)
    
    def get_audit_logs(
        self,
        user_id: Optional[str] = None,
        action: Optional[str] = None,
        limit: int = 100
    ) -> List[AuditLog]:
        """Query audit logs."""
        logs = self.audit_logs
        
        if user_id:
            logs = [l for l in logs if l.user_id == user_id]
        
        if action:
            logs = [l for l in logs if l.action == action]
        
        return logs[-limit:]


class EncryptionManager:
    """Data encryption manager."""
    
    def __init__(self, key: Optional[bytes] = None):
        self._key = key or self._generate_key()
    
    def _generate_key(self) -> bytes:
        """Generate encryption key."""
        return secrets.token_bytes(32)  # AES-256
    
    def encrypt(self, data: str) -> str:
        """Encrypt sensitive data."""
        try:
            from cryptography.fernet import Fernet
            f = Fernet(self._key)
            return f.encrypt(data.encode()).decode()
        except ImportError:
            logger.warning("cryptography not installed, using basic encoding")
            import base64
            return base64.b64encode(data.encode()).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt data."""
        try:
            from cryptography.fernet import Fernet
            f = Fernet(self._key)
            return f.decrypt(encrypted_data.encode()).decode()
        except ImportError:
            import base64
            return base64.b64decode(encrypted_data.encode()).decode()


class RBACManager:
    """Role-Based Access Control."""
    
    PERMISSIONS = {
        "admin": ["*"],
        "caregiver": [
            "read:sensors",
            "write:sensors",
            "read:alerts",
            "write:alerts",
            "read:care_plans",
            "write:care_plans",
            "read:chat",
            "write:chat"
        ],
        "family": [
            "read:sensors",
            "read:alerts",
            "read:care_plans",
            "write:chat"
        ],
        "senior": [
            "read:chat",
            "write:chat"
        ]
    }
    
    def __init__(self):
        self.user_roles: Dict[str, str] = {}
    
    def assign_role(self, user_id: str, role: str):
        """Assign role to user."""
        if role not in self.PERMISSIONS:
            raise ValueError(f"Invalid role: {role}")
        self.user_roles[user_id] = role
    
    def has_permission(self, user_id: str, permission: str) -> bool:
        """Check if user has permission."""
        role = self.user_roles.get(user_id)
        
        if not role:
            return False
        
        perms = self.PERMISSIONS.get(role, [])
        
        # Admin has all permissions
        if "*" in perms:
            return True
        
        return permission in perms
    
    def get_permissions(self, user_id: str) -> List[str]:
        """Get all permissions for user."""
        role = self.user_roles.get(user_id)
        return self.PERMISSIONS.get(role, [])

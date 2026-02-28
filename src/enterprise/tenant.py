"""
MaterCare Homes - Multi-Tenant Enterprise
========================================
White-label and multi-tenant support for enterprise deployment.
"""

from typing import Dict, Optional, List, Any
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class Tenant:
    """Tenant model for multi-tenant deployment."""
    tenant_id: str
    name: str
    slug: str  # URL-friendly identifier
    plan: str  # "professional", "enterprise", "white_label"
    custom_domain: Optional[str]
    branding: Dict[str, str]  # colors, logo, name
    settings: Dict[str, Any]
    created_at: datetime
    active: bool = True


@dataclass
class WhiteLabelConfig:
    """White-label configuration."""
    tenant_id: str
    company_name: str
    company_logo: Optional[str]
    primary_color: str
    secondary_color: str
    accent_color: str
    email_from: str
    support_email: str
    privacy_policy_url: str
    terms_url: str


class TenantManager:
    """Manage multi-tenant deployments."""
    
    def __init__(self):
        self.tenants: Dict[str, Tenant] = {}
        self.white_labels: Dict[str, WhiteLabelConfig] = {}
    
    def create_tenant(
        self,
        name: str,
        plan: str,
        custom_domain: Optional[str] = None,
        branding: Optional[Dict] = None
    ) -> Tenant:
        """Create new tenant."""
        tenant_id = f"tenant_{len(self.tenants) + 1}"
        slug = name.lower().replace(" ", "-")
        
        tenant = Tenant(
            tenant_id=tenant_id,
            name=name,
            slug=slug,
            plan=plan,
            custom_domain=custom_domain,
            branding=branding or {},
            settings={},
            created_at=datetime.now()
        )
        
        self.tenants[tenant_id] = tenant
        
        logger.info(f"Created tenant: {tenant_id} ({name})")
        
        return tenant
    
    def get_tenant(self, tenant_id: str) -> Optional[Tenant]:
        """Get tenant by ID."""
        return self.tenants.get(tenant_id)
    
    def get_tenant_by_domain(self, domain: str) -> Optional[Tenant]:
        """Get tenant by custom domain."""
        for tenant in self.tenants.values():
            if tenant.custom_domain == domain:
                return tenant
        return None
    
    def configure_white_label(
        self,
        tenant_id: str,
        config: WhiteLabelConfig
    ):
        """Configure white-label for tenant."""
        self.white_labels[tenant_id] = config
        logger.info(f"Configured white-label for tenant: {tenant_id}")
    
    def get_white_label(self, tenant_id: str) -> Optional[WhiteLabelConfig]:
        """Get white-label config."""
        return self.white_labels.get(tenant_id)
    
    def apply_branding(self, tenant_id: str, content: Dict) -> Dict:
        """Apply tenant branding to content."""
        tenant = self.tenants.get(tenant_id)
        
        if not tenant:
            return content
        
        # Inject branding into content
        branded = {
            **content,
            "branding": {
                "name": tenant.branding.get("name", "MaterCare"),
                "logo": tenant.branding.get("logo"),
                "colors": tenant.branding.get("colors", {}),
                "custom_domain": tenant.custom_domain
            }
        }
        
        return branded


class UsageQuotaManager:
    """Manage usage quotas per tenant."""
    
    def __init__(self):
        self.quotas: Dict[str, Dict] = {}
        self.usage: Dict[str, Dict] = {}
    
    def set_quota(
        self,
        tenant_id: str,
        resource: str,
        limit: int,
        period: str = "month"
    ):
        """Set quota for tenant resource."""
        if tenant_id not in self.quotas:
            self.quotas[tenant_id] = {}
        
        self.quotas[tenant_id][resource] = {
            "limit": limit,
            "period": period,
            "reset_at": self._get_next_reset(period)
        }
    
    def check_quota(
        self,
        tenant_id: str,
        resource: str,
        quantity: int = 1
    ) -> bool:
        """Check if tenant can use resource."""
        quota = self.quotas.get(tenant_id, {}).get(resource)
        
        if not quota:
            return True  # No quota set, allow
        
        if quota["limit"] == -1:
            return True  # Unlimited
        
        current = self.usage.get(tenant_id, {}).get(resource, 0)
        
        return (current + quantity) <= quota["limit"]
    
    def record_usage(
        self,
        tenant_id: str,
        resource: str,
        quantity: int = 1
    ):
        """Record resource usage."""
        if tenant_id not in self.usage:
            self.usage[tenant_id] = {}
        
        self.usage[tenant_id][resource] = (
            self.usage[tenant_id].get(resource, 0) + quantity
        )
    
    def get_usage(self, tenant_id: str) -> Dict:
        """Get usage report for tenant."""
        usage = self.usage.get(tenant_id, {})
        quotas = self.quotas.get(tenant_id, {})
        
        report = {}
        for resource in set(list(usage.keys()) + list(quotas.keys())):
            current = usage.get(resource, 0)
            quota = quotas.get(resource, {})
            limit = quota.get("limit", 0)
            
            report[resource] = {
                "current": current,
                "limit": limit,
                "remaining": max(0, limit - current) if limit > 0 else "unlimited",
                "period": quota.get("period", "month")
            }
        
        return report
    
    def _get_next_reset(self, period: str) -> datetime:
        """Calculate next quota reset date."""
        from datetime import timedelta
        
        if period == "month":
            # Reset at end of month
            now = datetime.now()
            if now.month == 12:
                return datetime(now.year + 1, 1, 1)
            return datetime(now.year, now.month + 1, 1)
        
        return datetime.now() + timedelta(days=30)

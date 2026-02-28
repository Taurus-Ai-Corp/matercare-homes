"""
MaterCare Homes - Billing & Revenue Module
==========================================
Subscription management, payments, and revenue tracking.
"""

from typing import Dict, Optional, List
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class PlanTier(str, Enum):
    COMMUNITY = "community"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    WHITE_LABEL = "white_label"


@dataclass
class Subscription:
    """Subscription model."""
    sub_id: str
    user_id: str
    tier: PlanTier
    started_at: datetime
    renews_at: datetime
    cancelled_at: Optional[datetime]
    status: str  # "active", "past_due", "cancelled"
    monthly_price: float


@dataclass
class UsageRecord:
    """Usage tracking for billing."""
    record_id: str
    user_id: str
    metric: str
    quantity: int
    timestamp: datetime


class BillingManager:
    """Subscription and billing management."""
    
    PRICING = {
        PlanTier.COMMUNITY: 0,
        PlanTier.PROFESSIONAL: 29,
        PlanTier.ENTERPRISE: 199,
        PlanTier.WHITE_LABEL: 5000,
    }
    
    LIMITS = {
        PlanTier.COMMUNITY: {
            "seniors": 1,
            "ai_queries": 100,
            "sms_alerts": 0,
            "api_calls": 0,
        },
        PlanTier.PROFESSIONAL: {
            "seniors": 5,
            "ai_queries": -1,  # unlimited
            "sms_alerts": 100,
            "api_calls": 1000,
        },
        PlanTier.ENTERPRISE: {
            "seniors": -1,  # unlimited
            "ai_queries": -1,
            "sms_alerts": -1,
            "api_calls": -1,
        },
        PlanTier.WHITE_LABEL: {
            "seniors": -1,
            "ai_queries": -1,
            "sms_alerts": -1,
            "api_calls": -1,
        },
    }
    
    def __init__(self):
        self.subscriptions: Dict[str, Subscription] = {}
        self.usage: List[UsageRecord] = []
    
    def create_subscription(
        self,
        user_id: str,
        tier: PlanTier,
        stripe_customer_id: Optional[str] = None
    ) -> Subscription:
        """Create new subscription."""
        sub_id = f"sub_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        sub = Subscription(
            sub_id=sub_id,
            user_id=user_id,
            tier=tier,
            started_at=datetime.now(),
            renews_at=datetime.now() + timedelta(days=30),
            cancelled_at=None,
            status="active",
            monthly_price=self.PRICING[tier]
        )
        
        self.subscriptions[sub_id] = sub
        
        logger.info(f"Created subscription {sub_id} for user {user_id} at ${self.PRICING[tier]}/mo")
        
        return sub
    
    def get_subscription(self, user_id: str) -> Optional[Subscription]:
        """Get user's active subscription."""
        for sub in self.subscriptions.values():
            if sub.user_id == user_id and sub.status == "active":
                return sub
        return None
    
    def check_limit(self, user_id: str, metric: str, quantity: int = 1) -> bool:
        """Check if user has exceeded limit."""
        sub = self.get_subscription(user_id)
        
        if not sub:
            return False
        
        limits = self.LIMITS[sub.tier]
        
        # -1 means unlimited
        if limits.get(metric, 0) == -1:
            return True
        
        # Calculate current usage
        current_usage = sum(
            r.quantity for r in self.usage
            if r.user_id == user_id and r.metric == metric
        )
        
        return (current_usage + quantity) <= limits.get(metric, 0)
    
    def record_usage(self, user_id: str, metric: str, quantity: int = 1):
        """Record usage for billing."""
        record = UsageRecord(
            record_id=f"usr_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
            user_id=user_id,
            metric=metric,
            quantity=quantity,
            timestamp=datetime.now()
        )
        
        self.usage.append(record)
    
    def get_usage_summary(self, user_id: str) -> Dict:
        """Get usage summary for user."""
        sub = self.get_subscription(user_id)
        
        if not sub:
            return {}
        
        limits = self.LIMITS[sub.tier]
        
        summary = {}
        for metric in limits:
            current = sum(
                r.quantity for r in self.usage
                if r.user_id == user_id and r.metric == metric
            )
            limit = limits[metric]
            
            if limit == -1:
                summary[metric] = {"current": current, "limit": "unlimited"}
            else:
                summary[metric] = {
                    "current": current,
                    "limit": limit,
                    "remaining": max(0, limit - current)
                }
        
        return summary
    
    def calculate_mrr(self) -> float:
        """Calculate monthly recurring revenue."""
        total = 0
        for sub in self.subscriptions.values():
            if sub.status == "active":
                total += sub.monthly_price
        return total
    
    def get_active_subscribers(self) -> int:
        """Count active subscribers."""
        return sum(1 for s in self.subscriptions.values() if s.status == "active")


class RevenueTracker:
    """Track revenue metrics."""
    
    def __init__(self):
        self.transactions: List[Dict] = []
    
    def record_transaction(
        self,
        user_id: str,
        amount: float,
        transaction_type: str,  # "subscription", "api", "hardware"
        description: str
    ):
        """Record revenue transaction."""
        self.transactions.append({
            "id": f"txn_{len(self.transactions)}",
            "user_id": user_id,
            "amount": amount,
            "type": transaction_type,
            "description": description,
            "timestamp": datetime.now()
        })
    
    def get_revenue_by_type(self) -> Dict[str, float]:
        """Get revenue breakdown by type."""
        revenue = {}
        for txn in self.transactions:
            t = txn["type"]
            revenue[t] = revenue.get(t, 0) + txn["amount"]
        return revenue
    
    def get_ltv(self, user_id: str) -> float:
        """Calculate customer lifetime value."""
        total = sum(
            txn["amount"] for txn in self.transactions
            if txn["user_id"] == user_id
        )
        return total
    
    def get_mrr_by_tier(self) -> Dict[str, float]:
        """Get MRR breakdown by tier."""
        billing = BillingManager()
        revenue = {}
        
        for sub in billing.subscriptions.values():
            if sub.status == "active":
                tier = sub.tier.value
                revenue[tier] = revenue.get(tier, 0) + sub.monthly_price
        
        return revenue

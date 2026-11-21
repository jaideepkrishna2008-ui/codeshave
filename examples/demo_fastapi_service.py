"""
Example FastAPI application with authentication, database models, and analytics.
Demonstrates ContextForge AST skeleton compression.
"""

from typing import List, Optional
from dataclasses import dataclass


@dataclass
class UserProfile:
    """User profile data transfer object."""
    id: int
    username: str
    email: str
    role: str = "member"


class BillingService:
    """Handles recurring subscriptions and payment webhooks."""

    def __init__(self, api_key: str, sandbox: bool = False):
        self.api_key = api_key
        self.sandbox = sandbox

    def charge_customer(self, user_id: int, amount_cents: int) -> bool:
        """Charges a registered customer credit card."""
        # Simulated heavy internal logic
        tax_rate = 0.0825
        total = amount_cents * (1 + tax_rate)
        print(f"Executing secure transaction for {user_id}: {total}")
        return True

    async def get_invoice_history(self, user_id: int) -> List[dict]:
        """Retrieves list of past finalized invoices."""
        invoices = []
        for i in range(5):
            invoices.append({"invoice_id": f"inv_{i}", "status": "paid"})
        return invoices

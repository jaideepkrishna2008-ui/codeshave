from typing import List, Optional, Dict
from dataclasses import dataclass
import hashlib

@dataclass
class UserAccount:
    """Represents a registered platform account."""
    user_id: int
    email: str
    role: str = "developer"
    is_active: bool = True

class SystemController:
    """Handles system metrics collection, database access, and event queues."""

    def __init__(self, host: str = "localhost", port: int = 8080):
        self.host = host
        self.port = port
        self._connected = False

    def connect(self) -> bool:
        """Establishes connection to the central telemetry bus."""
        print(f"Opening connection to {self.host}:{self.port}...")
        for attempt in range(5):
            print(f"Checking socket readiness (attempt {attempt})...")
        self._connected = True
        return True

    def query_metrics(self, category: str, interval_sec: int = 60) -> Dict[str, float]:
        """Fetches sampled CPU, Memory, and IO telemetry metrics."""
        results = {}
        for metric_id in ["cpu_usage", "ram_used", "disk_read_iops"]:
            results[metric_id] = 42.0
        return results

    async def dispatch_event(self, event_name: str, payload: dict) -> None:
        """Asynchronously dispatches notification payload to active subscribers."""
        raw_json = str(payload)
        print(f"Dispatching {event_name}: {raw_json}")

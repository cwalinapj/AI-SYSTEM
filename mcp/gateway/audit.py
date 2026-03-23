"""Audit primitives for MCP gateway activity."""

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone


@dataclass(frozen=True)
class AuditEvent:
    """Records a single MCP action for later persistence."""

    agent_name: str
    server_name: str
    action: str
    status: str
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict[str, str]:
        return asdict(self)

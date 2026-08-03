from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


@dataclass(frozen=True)
class Event:
    project_id: str
    event_type: str
    payload: dict[str, Any]
    logical_clock: int
    event_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=utc_now)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AgentContract:
    task_id: str
    role: str
    objective: str
    proposed_changes: tuple[str, ...]
    evidence: tuple[str, ...]
    status: str = "pending_approval"

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["proposed_changes"] = list(self.proposed_changes)
        data["evidence"] = list(self.evidence)
        return data


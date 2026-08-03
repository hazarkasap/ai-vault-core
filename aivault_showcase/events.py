from __future__ import annotations

import json
import re
from collections.abc import Iterable
from pathlib import Path

from .models import Event

SAFE_ID = re.compile(r"^[a-z][a-z0-9_-]{1,63}$")
EVENT_TYPES = {
    "project_created", "goal_created", "iteration_started",
    "agent_response_received", "approval_requested", "approval_granted",
    "patch_previewed", "patch_applied", "verification_passed", "iteration_completed",
}


def validate_id(value: str, label: str = "identifier") -> str:
    if not SAFE_ID.fullmatch(value):
        raise ValueError(f"invalid {label}")
    return value


def validate_event(event: Event) -> None:
    validate_id(event.project_id, "project_id")
    if event.event_type not in EVENT_TYPES:
        raise ValueError("unsupported event_type")
    if event.logical_clock < 1:
        raise ValueError("logical_clock must be positive")
    if not isinstance(event.payload, dict):
        raise ValueError("payload must be an object")


class EventStore:
    """Append-only JSONL event store with deterministic logical clocks."""

    def __init__(self, path: Path) -> None:
        self.path = path

    def read(self) -> list[Event]:
        if not self.path.exists():
            return []
        events = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                event = Event(**json.loads(line))
                validate_event(event)
                events.append(event)
        self._validate_sequence(events)
        return events

    def append(self, project_id: str, event_type: str, payload: dict) -> Event:
        events = self.read()
        event = Event(project_id, event_type, payload, len(events) + 1)
        validate_event(event)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event.to_dict(), sort_keys=True) + "\n")
        return event

    @staticmethod
    def _validate_sequence(events: Iterable[Event]) -> None:
        seen = set()
        for expected, event in enumerate(events, 1):
            if event.logical_clock != expected:
                raise ValueError("non-contiguous logical clock")
            if event.event_id in seen:
                raise ValueError("duplicate event_id")
            seen.add(event.event_id)

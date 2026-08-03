from __future__ import annotations

from typing import Any

from .events import validate_id
from .models import AgentContract

ROLES = {"planner", "executor", "reviewer"}


def parse_contract(data: dict[str, Any]) -> AgentContract:
    required = {"task_id", "role", "objective", "proposed_changes", "evidence"}
    if set(data) != required:
        raise ValueError("contract fields do not match the schema")
    task_id = validate_id(str(data["task_id"]), "task_id")
    role = str(data["role"])
    if role not in ROLES:
        raise ValueError("unsupported agent role")
    objective = str(data["objective"]).strip()
    changes = tuple(str(item).strip() for item in data["proposed_changes"])
    evidence = tuple(str(item).strip() for item in data["evidence"])
    if not objective or not changes or any(not item for item in changes):
        raise ValueError("objective and proposed_changes are required")
    return AgentContract(task_id, role, objective, changes, evidence)

from __future__ import annotations

from dataclasses import dataclass

from .events import EventStore
from .models import AgentContract


@dataclass
class WorkflowState:
    project_id: str
    goal: str | None = None
    iteration_status: str = "idle"
    pending_task: str | None = None
    approved_task: str | None = None
    patch_status: str | None = None
    verification: str | None = None


def project_state(events: list) -> WorkflowState:
    state = WorkflowState(events[0].project_id if events else "demo_project")
    for event in events:
        payload = event.payload
        if event.event_type == "goal_created":
            state.goal = payload["goal"]
        elif event.event_type == "iteration_started":
            state.iteration_status = "active"
        elif event.event_type == "approval_requested":
            state.pending_task = payload["task_id"]
        elif event.event_type == "approval_granted":
            state.approved_task, state.pending_task = payload["task_id"], None
        elif event.event_type == "patch_previewed":
            state.patch_status = "previewed"
        elif event.event_type == "patch_applied":
            state.patch_status = "applied"
        elif event.event_type == "verification_passed":
            state.verification = "passed"
        elif event.event_type == "iteration_completed":
            state.iteration_status = "completed"
    return state


class Workflow:
    def __init__(self, store: EventStore, project_id: str) -> None:
        self.store, self.project_id = store, project_id

    def start(self, goal: str) -> None:
        if self.store.read():
            raise ValueError("workflow already initialized")
        self.store.append(self.project_id, "project_created", {"source": "synthetic_demo"})
        self.store.append(self.project_id, "goal_created", {"goal": goal})
        self.store.append(self.project_id, "iteration_started", {"iteration_id": "iteration_1"})

    def submit(self, contract: AgentContract) -> None:
        state = project_state(self.store.read())
        if state.iteration_status != "active" or state.pending_task:
            raise ValueError("workflow is not accepting a contract")
        self.store.append(
            self.project_id,
            "agent_response_received",
            {"task_id": contract.task_id, "role": contract.role},
        )
        self.store.append(
            self.project_id,
            "approval_requested",
            {"task_id": contract.task_id, "changes": list(contract.proposed_changes)},
        )

    def approve(self, task_id: str) -> None:
        if project_state(self.store.read()).pending_task != task_id:
            raise ValueError("task is not pending approval")
        self.store.append(self.project_id, "approval_granted", {"task_id": task_id})

    def preview_patch(self, task_id: str) -> None:
        if project_state(self.store.read()).approved_task != task_id:
            raise ValueError("task is not approved")
        self.store.append(self.project_id, "patch_previewed", {"task_id": task_id})

    def apply_patch(self, task_id: str) -> None:
        state = project_state(self.store.read())
        if state.approved_task != task_id or state.patch_status != "previewed":
            raise ValueError("patch must be approved and previewed")
        self.store.append(self.project_id, "patch_applied", {"task_id": task_id})

    def verify_and_complete(self) -> None:
        if project_state(self.store.read()).patch_status != "applied":
            raise ValueError("patch has not been applied")
        self.store.append(self.project_id, "verification_passed", {"checks": ["demo_test"]})
        self.store.append(self.project_id, "iteration_completed", {"outcome": "verified"})

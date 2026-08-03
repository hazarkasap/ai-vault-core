import hashlib
import json

from .workflow import project_state


def replay(events: list) -> dict:
    state = project_state(events)
    projection = {
        "project_id": state.project_id, "goal": state.goal,
        "iteration_status": state.iteration_status, "pending_task": state.pending_task,
        "approved_task": state.approved_task, "patch_status": state.patch_status,
        "verification": state.verification, "event_count": len(events),
    }
    canonical = json.dumps(projection, sort_keys=True, separators=(",", ":"))
    projection["replay_hash"] = hashlib.sha256(canonical.encode()).hexdigest()
    return projection


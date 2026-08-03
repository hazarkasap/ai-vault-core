from pathlib import Path

import pytest

from aivault_showcase.contracts import parse_contract
from aivault_showcase.events import EventStore
from aivault_showcase.replay import replay
from aivault_showcase.workflow import Workflow, project_state


def contract():
    return parse_contract({
        "task_id": "task_demo_1", "role": "executor",
        "objective": "Implement deterministic ordering",
        "proposed_changes": ["Sort synthetic records"], "evidence": ["Unit test"],
    })


def test_human_approval_and_patch_lifecycle(tmp_path: Path) -> None:
    store = EventStore(tmp_path / "events.jsonl")
    flow = Workflow(store, "demo_project")
    flow.start("Improve the synthetic note tool")
    flow.submit(contract())
    assert project_state(store.read()).pending_task == "task_demo_1"
    flow.approve("task_demo_1")
    flow.preview_patch("task_demo_1")
    flow.apply_patch("task_demo_1")
    flow.verify_and_complete()
    state = project_state(store.read())
    assert state.iteration_status == "completed"
    assert state.verification == "passed"


def test_patch_cannot_apply_without_approval(tmp_path: Path) -> None:
    store = EventStore(tmp_path / "events.jsonl")
    flow = Workflow(store, "demo_project")
    flow.start("Synthetic goal")
    flow.submit(contract())
    with pytest.raises(ValueError, match="approved"):
        flow.preview_patch("task_demo_1")


def test_replay_is_deterministic(tmp_path: Path) -> None:
    store = EventStore(tmp_path / "events.jsonl")
    Workflow(store, "demo_project").start("Synthetic goal")
    assert replay(store.read()) == replay(store.read())


def test_contract_rejects_unknown_fields() -> None:
    data = contract().to_dict()
    data["unexpected"] = True
    data.pop("status")
    with pytest.raises(ValueError, match="fields"):
        parse_contract(data)

from __future__ import annotations

import argparse
import json
from pathlib import Path

from aiohttp import web

from .api import create_app
from .contracts import parse_contract
from .events import EventStore
from .intelligence import build_overview
from .workflow import Workflow


def runtime_store(root: Path) -> EventStore:
    return EventStore(root / ".runtime" / "demo_project" / "events.jsonl")


def seed_demo(root: Path) -> None:
    store = runtime_store(root)
    if store.path.exists():
        store.path.unlink()
    flow = Workflow(store, "demo_project")
    flow.start("Improve a small command-line note tool")
    contract = parse_contract({
        "task_id": "task_demo_1", "role": "executor",
        "objective": "Add deterministic note ordering",
        "proposed_changes": ["Sort note records by creation sequence"],
        "evidence": ["Synthetic unit scenario"],
    })
    flow.submit(contract)
    flow.approve(contract.task_id)
    flow.preview_patch(contract.task_id)
    flow.apply_patch(contract.task_id)
    flow.verify_and_complete()


def main() -> None:
    parser = argparse.ArgumentParser(description="AI workflow showcase")
    parser.add_argument("command", choices=["seed-demo", "status", "serve"])
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8765, type=int)
    args = parser.parse_args()
    root = Path.cwd()
    if args.command == "seed-demo":
        seed_demo(root)
        print("Synthetic demo initialized.")
    elif args.command == "status":
        print(json.dumps(build_overview(runtime_store(root).read()), indent=2))
    else:
        web.run_app(create_app(runtime_store(root).path), host=args.host, port=args.port)


if __name__ == "__main__":
    main()


from collections import Counter

from .replay import replay


def build_overview(events: list) -> dict:
    projection = replay(events)
    counts = Counter(event.event_type for event in events)
    return {**projection, "event_types": dict(sorted(counts.items())),
            "pending_approvals": int(projection["pending_task"] is not None),
            "human_in_the_loop": True, "autonomous_model_provider": False}


def timeline(events: list) -> list[dict]:
    return [{"clock": event.logical_clock, "event_type": event.event_type,
             "created_at": event.created_at} for event in events]

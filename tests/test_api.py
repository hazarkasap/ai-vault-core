from pathlib import Path

from aiohttp.test_utils import TestClient, TestServer

from aivault_showcase.api import create_app
from aivault_showcase.cli import seed_demo


async def test_health_and_read_only_projection(tmp_path: Path) -> None:
    seed_demo(tmp_path)
    app = create_app(tmp_path / ".runtime" / "demo_project" / "events.jsonl")
    async with TestClient(TestServer(app)) as client:
        health = await client.get("/health")
        assert health.status == 200
        assert await health.json() == {"status": "ok"}
        body = await (await client.get("/api/overview")).json()
        assert body["project_id"] == "demo_project"
        assert body["human_in_the_loop"] is True
        assert body["autonomous_model_provider"] is False


async def test_websocket_sends_snapshot(tmp_path: Path) -> None:
    seed_demo(tmp_path)
    app = create_app(tmp_path / ".runtime" / "demo_project" / "events.jsonl")
    async with TestClient(TestServer(app)) as client:
        socket = await client.ws_connect("/ws")
        message = await socket.receive_json()
        assert message["type"] == "snapshot"
        assert message["data"]["event_count"] == 10
        await socket.close()

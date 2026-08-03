from __future__ import annotations

import json
from pathlib import Path

from aiohttp import WSMsgType, web

from .events import EventStore
from .intelligence import build_overview, timeline


def create_app(event_path: Path) -> web.Application:
    app, store = web.Application(), EventStore(event_path)

    async def health(_: web.Request) -> web.Response:
        return web.json_response({"status": "ok"})

    async def overview(_: web.Request) -> web.Response:
        return web.json_response(build_overview(store.read()))

    async def events(_: web.Request) -> web.Response:
        return web.json_response({"events": timeline(store.read())})

    async def stream(request: web.Request) -> web.WebSocketResponse:
        ws = web.WebSocketResponse(heartbeat=30)
        await ws.prepare(request)
        await ws.send_str(json.dumps({"type": "snapshot", "data": build_overview(store.read())}))
        async for message in ws:
            if message.type == WSMsgType.TEXT and message.data == "refresh":
                snapshot = {"type": "snapshot", "data": build_overview(store.read())}
                await ws.send_str(json.dumps(snapshot))
            elif message.type == WSMsgType.ERROR:
                break
        return ws

    app.router.add_get("/health", health)
    app.router.add_get("/api/overview", overview)
    app.router.add_get("/api/events", events)
    app.router.add_get("/ws", stream)
    return app

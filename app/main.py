"""FastAPI app: dashboard, health, and a WebSocket of annotated frames."""

from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import Settings
from app.detector import HogPersonDetector
from app.pipeline import Pipeline

logger = logging.getLogger("sentri")
STATIC = Path(__file__).resolve().parents[1] / "static"


def create_app(settings: Settings | None = None, detector=None) -> FastAPI:
    settings = settings or Settings.from_env()
    if detector is None:
        detector = HogPersonDetector()
    pipeline = Pipeline(settings, detector)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        pipeline.start()
        try:
            yield
        finally:
            pipeline.stop()

    app = FastAPI(title="Sentri", lifespan=lifespan)
    app.state.pipeline = pipeline
    app.state.settings = settings

    @app.get("/health")
    def health() -> dict:
        snap = pipeline.snapshot()
        if snap is None:
            status = "starting"
        elif "error" in snap and "frame_jpeg" not in snap:
            status = "error"
        else:
            status = "ok"
        body = {
            "status": status,
            "detector": "hog",
            "video": str(settings.video_path),
            "alert_threshold": settings.alert_threshold,
            "count": snap.get("count") if snap and "count" in snap else None,
        }
        if snap and "error" in snap:
            body["error"] = snap["error"]
        return body

    @app.get("/")
    def index() -> FileResponse:
        return FileResponse(STATIC / "index.html")

    @app.websocket("/ws")
    async def stream(websocket: WebSocket) -> None:
        await websocket.accept()
        try:
            while True:
                snap = pipeline.snapshot()
                if snap is None:
                    await asyncio.sleep(0.05)
                    continue
                await websocket.send_json(snap)
                await asyncio.sleep(0.1)
        except WebSocketDisconnect:
            return
        except Exception:
            logger.exception("websocket closed")

    app.mount("/static", StaticFiles(directory=STATIC), name="static")
    return app


app = create_app()

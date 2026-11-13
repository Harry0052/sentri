import base64
import time
from pathlib import Path

import cv2
import numpy as np
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app


def _write_video(path: Path, frames: int = 12) -> None:
    writer = cv2.VideoWriter(
        str(path), cv2.VideoWriter_fourcc(*"MJPG"), 20, (160, 120)
    )
    assert writer.isOpened()
    image = np.full((120, 160, 3), 30, np.uint8)
    for _ in range(frames):
        writer.write(image)
    writer.release()


class OnePerson:
    def detect(self, frame):
        return [(20, 10, 36, 80)]


def test_dashboard_and_health_and_websocket(tmp_path):
    video = tmp_path / "people.avi"
    _write_video(video)
    settings = Settings(
        video_path=video,
        alert_threshold=0,
        pace=False,
        loop=False,
        max_missed=2,
        confirm_hits=1,
        max_match_distance=40,
    )
    app = create_app(settings, OnePerson())

    with TestClient(app) as client:
        page = client.get("/")
        assert page.status_code == 200
        assert "Sentri" in page.text
        assert "/static/dashboard.js" in page.text

        body = {}
        deadline = time.time() + 2
        while time.time() < deadline:
            body = client.get("/health").json()
            if body["status"] == "ok" and body["count"] == 1:
                break
            time.sleep(0.02)
        assert body["status"] == "ok"
        assert body["detector"] == "hog"
        assert body["alert_threshold"] == 0
        assert body["count"] == 1

        with client.websocket_connect("/ws") as socket:
            message = socket.receive_json()
            raw = base64.b64decode(message["frame_jpeg"])
            assert raw[:2] == b"\xff\xd8"
            assert message["count"] == 1
            assert message["alert"] is True
            assert message["threshold"] == 0
            assert set(message["boxes"][0]) == {"id", "x", "y", "w", "h"}
            entered = [event for event in message["events"] if event["type"] == "entered"]
            assert entered
            assert set(entered[0]) == {"id", "type", "track_id", "time_sec"}


def test_missing_video_is_an_error(tmp_path):
    settings = Settings(video_path=tmp_path / "missing.avi", pace=False, loop=False)
    app = create_app(settings, OnePerson())
    with TestClient(app) as client:
        body = {}
        deadline = time.time() + 2
        while time.time() < deadline:
            body = client.get("/health").json()
            if body["status"] == "error":
                break
            time.sleep(0.02)
        assert body["status"] == "error"
        assert "fetch_sample.py" in body["error"]

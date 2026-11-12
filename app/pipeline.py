"""Read a video file, detect people, and keep the latest dashboard snapshot."""

from __future__ import annotations

import base64
import logging
import threading
import time
from typing import Any

import cv2

from app.config import Settings
from app.tracker import CentroidTracker, Track

logger = logging.getLogger("sentri")

BOX_COLOR = (41, 180, 240)  # BGR amber
LABEL_COLOR = (16, 19, 16)


class Pipeline:
    def __init__(self, settings: Settings, detector: Any) -> None:
        self.settings = settings
        self.detector = detector
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._latest: dict[str, Any] | None = None
        self._events: list[dict[str, Any]] = []
        self._seq = 0
        self.error: str | None = None

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._loop, name="sentri-pipeline", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=2)

    def snapshot(self) -> dict[str, Any] | None:
        with self._lock:
            if self.error and self._latest is None:
                return {"error": self.error}
            if self._latest is None:
                return None
            payload = dict(self._latest)
            if self.error:
                payload["error"] = self.error
            return payload

    def _loop(self) -> None:
        path = self.settings.video_path
        if not path.is_file():
            self.error = (
                f"Video not found at {path}. Run: python scripts/fetch_sample.py"
            )
            logger.error(self.error)
            return

        capture = cv2.VideoCapture(str(path))
        if not capture.isOpened():
            self.error = f"Could not open video at {path}"
            logger.error(self.error)
            capture.release()
            return

        fps = float(capture.get(cv2.CAP_PROP_FPS) or 0) or 10.0
        logger.info("playing %s at %.2f fps", path, fps)
        tracker = CentroidTracker(
            max_distance=self.settings.max_match_distance,
            max_missed=self.settings.max_missed,
            confirm_hits=self.settings.confirm_hits,
        )
        frame_index = 0
        last_frame = None

        while not self._stop.is_set():
            started = time.perf_counter()
            ok, frame = capture.read()
            if not ok:
                if last_frame is None:
                    self.error = f"Video has no frames: {path}"
                    logger.error(self.error)
                    break
                if not self.settings.loop:
                    self._stop.wait()
                    break
                events = tracker.drop_all(frame_index)
                self._publish(last_frame, tracker, events, frame_index, fps)
                capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
                frame_index = 0
                if self._stop.wait(0.05):
                    break
                continue

            last_frame = frame
            try:
                boxes = list(self.detector.detect(frame))
            except Exception:
                logger.exception("detector failed on frame %s", frame_index)
                boxes = []
            events = tracker.update(boxes, frame_index)
            self._publish(frame, tracker, events, frame_index, fps)
            frame_index += 1

            if self.settings.pace:
                delay = (1.0 / fps) - (time.perf_counter() - started)
                if delay > 0 and self._stop.wait(delay):
                    break

        capture.release()

    def _publish(self, frame, tracker: CentroidTracker, events, frame_index: int, fps: float) -> None:
        annotated = _draw(frame, tracker.announced())
        ok, encoded = cv2.imencode(
            ".jpg", annotated, [int(cv2.IMWRITE_JPEG_QUALITY), 75]
        )
        if not ok:
            return
        jpeg = base64.b64encode(encoded.tobytes()).decode("ascii")
        visible = tracker.announced()
        count = tracker.count
        with self._lock:
            for event in events:
                self._seq += 1
                self._events.append(
                    {
                        "id": self._seq,
                        "type": event.type,
                        "track_id": event.track_id,
                        "time_sec": round(event.frame_index / fps, 2),
                    }
                )
            if len(self._events) > 200:
                self._events = self._events[-200:]
            self._latest = {
                "frame_jpeg": jpeg,
                "width": int(frame.shape[1]),
                "height": int(frame.shape[0]),
                "count": count,
                "threshold": self.settings.alert_threshold,
                "alert": count > self.settings.alert_threshold,
                "boxes": [
                    {
                        "id": track.id,
                        "x": int(track.bbox[0]),
                        "y": int(track.bbox[1]),
                        "w": int(track.bbox[2]),
                        "h": int(track.bbox[3]),
                    }
                    for track in visible
                ],
                "events": list(self._events[-40:]),
                "time_sec": round(frame_index / fps, 2),
                "frame_index": frame_index,
                "detector": "hog",
            }


def _draw(frame, tracks: list[Track]):
    canvas = frame.copy()
    for track in tracks:
        x, y, w, h = track.bbox
        cv2.rectangle(canvas, (x, y), (x + w, y + h), BOX_COLOR, 2)
        label = f"P{track.id}"
        (tw, th), _baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        top = y - th - 8
        if top < 0:
            top = y
        cv2.rectangle(canvas, (x, top), (x + tw + 8, top + th + 8), BOX_COLOR, -1)
        cv2.putText(
            canvas,
            label,
            (x + 4, top + th + 2),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            LABEL_COLOR,
            1,
            cv2.LINE_AA,
        )
    return canvas

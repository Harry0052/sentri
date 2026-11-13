from pathlib import Path

import cv2
import numpy as np
import pytest

from app.detector import HogPersonDetector


def test_blank_frame_returns_a_list():
    detector = HogPersonDetector()
    frame = np.zeros((240, 320, 3), np.uint8)
    boxes = detector.detect(frame)
    assert isinstance(boxes, list)
    assert boxes == []


def test_sample_clip_contains_a_person():
    path = Path("demo-videos/sample.avi")
    if not path.is_file():
        pytest.skip("sample clip is not downloaded")
    detector = HogPersonDetector()
    capture = cv2.VideoCapture(str(path))
    found = False
    try:
        for _ in range(20):
            ok, frame = capture.read()
            if not ok:
                break
            if detector.detect(frame):
                found = True
                break
    finally:
        capture.release()
    assert found, "HOG found no person in the first 20 frames of the sample clip"

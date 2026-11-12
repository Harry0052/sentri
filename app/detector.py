"""Person detector using the HOG+SVM model shipped with OpenCV 4.

OpenCV 5 removed ``HOGDescriptor``, so this project pins ``opencv-python-headless``
to 4.11. The detector is the library default (a 64×128 people window). It is
not trained on retail cameras. Upright, mostly full-body people are what it
was built to find.
"""

from __future__ import annotations

import cv2


class HogPersonDetector:
    def __init__(self) -> None:
        hog = cv2.HOGDescriptor()
        hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
        self._hog = hog

    def detect(self, frame) -> list[tuple[int, int, int, int]]:
        if frame is None or getattr(frame, "size", 0) == 0:
            return []
        rects, _weights = self._hog.detectMultiScale(
            frame,
            hitThreshold=0,
            winStride=(8, 8),
            padding=(8, 8),
            scale=1.05,
            groupThreshold=2,
        )
        return [(int(x), int(y), int(w), int(h)) for x, y, w, h in rects]

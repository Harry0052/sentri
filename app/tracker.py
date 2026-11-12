"""Match person boxes across frames and emit entered/left events.

A detection becomes a person after it is seen on ``confirm_hits`` frames, so a
single-frame false positive does not show up in the log. A person leaves after
they are missing for more than ``max_missed`` frames.
"""

from __future__ import annotations

import math
from dataclasses import dataclass


Box = tuple[int, int, int, int]


@dataclass
class Track:
    id: int
    bbox: Box
    missed: int = 0
    hits: int = 1
    announced: bool = False


@dataclass(frozen=True)
class TrackEvent:
    type: str
    track_id: int
    frame_index: int


def _center(box: Box) -> tuple[float, float]:
    x, y, w, h = box
    return x + w / 2.0, y + h / 2.0


def _distance(a: Box, b: Box) -> float:
    ax, ay = _center(a)
    bx, by = _center(b)
    return math.hypot(ax - bx, ay - by)


class CentroidTracker:
    def __init__(
        self,
        max_distance: float = 90.0,
        max_missed: int = 6,
        confirm_hits: int = 2,
    ) -> None:
        self.max_distance = max_distance
        self.max_missed = max_missed
        self.confirm_hits = confirm_hits
        self._tracks: dict[int, Track] = {}
        self._next_id = 1

    @property
    def count(self) -> int:
        return sum(1 for track in self._tracks.values() if track.announced)

    def announced(self) -> list[Track]:
        return [track for track in self._tracks.values() if track.announced]

    def update(self, boxes: list[Box], frame_index: int) -> list[TrackEvent]:
        events: list[TrackEvent] = []
        pairings: list[tuple[float, int, int]] = []
        track_ids = list(self._tracks)
        for track_id in track_ids:
            track = self._tracks[track_id]
            for index, box in enumerate(boxes):
                pairings.append((_distance(track.bbox, box), track_id, index))
        pairings.sort()

        matched_tracks: set[int] = set()
        matched_boxes: set[int] = set()
        for distance, track_id, index in pairings:
            if distance > self.max_distance:
                break
            if track_id in matched_tracks or index in matched_boxes:
                continue
            matched_tracks.add(track_id)
            matched_boxes.add(index)
            track = self._tracks[track_id]
            track.bbox = boxes[index]
            track.missed = 0
            track.hits += 1
            self._announce(track, frame_index, events)

        for track_id in track_ids:
            if track_id in matched_tracks:
                continue
            track = self._tracks[track_id]
            track.missed += 1
            if track.missed > self.max_missed:
                if track.announced:
                    events.append(TrackEvent("left", track.id, frame_index))
                del self._tracks[track_id]

        for index, box in enumerate(boxes):
            if index in matched_boxes:
                continue
            track = Track(id=self._next_id, bbox=box)
            self._next_id += 1
            self._tracks[track.id] = track
            self._announce(track, frame_index, events)

        return events

    def drop_all(self, frame_index: int) -> list[TrackEvent]:
        events = [
            TrackEvent("left", track.id, frame_index)
            for track in self._tracks.values()
            if track.announced
        ]
        self._tracks.clear()
        return events

    def _announce(self, track: Track, frame_index: int, events: list[TrackEvent]) -> None:
        if track.announced or track.hits < self.confirm_hits:
            return
        track.announced = True
        events.append(TrackEvent("entered", track.id, frame_index))

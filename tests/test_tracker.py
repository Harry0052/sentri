from app.tracker import CentroidTracker


def test_enter_requires_two_sightings():
    tracker = CentroidTracker(max_distance=50, max_missed=3, confirm_hits=2)
    box = (0, 0, 40, 80)
    assert tracker.update([box], 0) == []
    assert tracker.count == 0

    events = tracker.update([(2, 1, 40, 80)], 1)
    assert [(event.type, event.track_id) for event in events] == [("entered", 1)]
    assert tracker.count == 1
    assert tracker.announced()[0].id == 1


def test_one_frame_false_positive_is_silent():
    tracker = CentroidTracker(max_distance=40, max_missed=1, confirm_hits=2)
    assert tracker.update([(0, 0, 10, 20)], 0) == []
    assert tracker.update([], 1) == []
    assert tracker.update([], 2) == []
    assert tracker.count == 0


def test_leave_after_missing_frames():
    tracker = CentroidTracker(max_distance=50, max_missed=2, confirm_hits=1)
    entered = tracker.update([(0, 0, 10, 20)], 0)
    assert entered[0].type == "entered"

    assert tracker.update([], 1) == []
    assert tracker.update([], 2) == []
    left = tracker.update([], 3)
    assert [(event.type, event.track_id) for event in left] == [("left", 1)]
    assert tracker.count == 0


def test_two_people_keep_separate_ids():
    tracker = CentroidTracker(max_distance=30, max_missed=2, confirm_hits=1)
    tracker.update([(0, 0, 10, 10), (100, 0, 10, 10)], 0)
    tracker.update([(2, 0, 10, 10), (102, 1, 10, 10)], 1)
    assert sorted(track.id for track in tracker.announced()) == [1, 2]
    assert tracker.count == 2


def test_drop_all_emits_left_for_visible_people():
    tracker = CentroidTracker(max_distance=30, max_missed=4, confirm_hits=1)
    tracker.update([(0, 0, 10, 10)], 4)
    events = tracker.drop_all(5)
    assert [(event.type, event.track_id, event.frame_index) for event in events] == [
        ("left", 1, 5)
    ]
    assert tracker.count == 0

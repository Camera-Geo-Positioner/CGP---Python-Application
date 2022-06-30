# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software Project course.
# © Copyright Utrecht University (Department of Information and Computing Sciences)
from unittest.mock import Mock

from FrameAnalyzer.DeepSocialDetector import *
from IO import Pathing
# from Windowing.CameraWindow import *

frame = cv2.imread(str(Pathing.AssureAbsolutePath('Testing/Assets/person.jpg')))
frame = cv2.resize(frame, (960, 540))


# Test if testImage is loaded
def test_TestImage():
    if frame is None:
        raise TypeError("No TestImage")


# Test the detector with normal input
def test_Normal():
    detector = DeepSocialDetector()
    detections, frameIndex = detector.GetHumanPositions(frame, 0)
    assert len(detections) == 1


# Test if the id's stay the same
def test_KeepID():
    # Setup
    detector = DeepSocialDetector()

    # Detect at least 4 times, cause then the tracking kicks in
    detections, frameIndex = detector.GetHumanPositions(frame, 0)
    detections, frameIndex = detector.GetHumanPositions(frame, 1)
    detections, frameIndex = detector.GetHumanPositions(frame, 2)
    detections, frameIndex = detector.GetHumanPositions(frame, 3)

    currentID = 0
    for detection in detections:
        currentID = detection.id

    # Second click
    detections, frameIndex = detector.GetHumanPositions(frame, 4)
    for detection in detections:
        assert currentID == detection.id


# Test if the id's change when the position of tracked objects changes much
def test_DifferentID():
    # Setup
    detector = DeepSocialDetector()

    frameLeft = cv2.imread(str(Pathing.AssureAbsolutePath('Testing/Assets/man-walking-left.jpg')))
    frameLeft = cv2.resize(frameLeft, (960, 540))

    frameRight = cv2.imread(str(Pathing.AssureAbsolutePath('Testing/Assets/man-walking-right.jpg')))
    frameRight = cv2.resize(frameRight, (960, 540))

    # Detect at least 4 times, cause then the tracking kicks in
    detections, frameIndex = detector.GetHumanPositions(frameLeft, 0)
    detections, frameIndex = detector.GetHumanPositions(frameLeft, 1)
    detections, frameIndex = detector.GetHumanPositions(frameLeft, 2)
    detections, frameIndex = detector.GetHumanPositions(frameLeft, 3)
    detections, frameIndex = detector.GetHumanPositions(frameLeft, 4)

    currentID = 0
    for detection in detections:
        currentID = detection.id

    # Mirrored image, so the walking man has a completely different position, and therfore should have a different ID
    detections, frameIndex = detector.GetHumanPositions(frameRight, 5)
    for detection in detections:
        assert currentID != detection.id


# Test the showDetections function of the detector
def test_ShowDetections():
    detector = DeepSocialDetector(showDetections=False)
    detector.GetHumanPositions(frame, 0)


# Test if the detector does not crash without a frame
def test_NullFrame():
    detector = DeepSocialDetector()
    detector.GetHumanPositions(None, 0)

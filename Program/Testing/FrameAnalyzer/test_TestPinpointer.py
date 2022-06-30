# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software Project course.
# © Copyright Utrecht University (Department of Information and Computing Sciences)
from unittest.mock import Mock

from FrameAnalyzer.TestPinpointer import *
from IO import Pathing
from Windowing.Sub.CameraSubWindow import *
import cv2


frame = cv2.imread(
    str(Pathing.AssureAbsolutePath('Testing/Assets/testImage.png'))
)


def mockPyGame():
    pygame.init = Mock()
    pygame.display_set_mode = Mock()
    pygame.display = Mock()
    pygame.display.get_init = Mock(return_value=False)
    pygame.display.get_surface = Mock()
    pygame.display.get_surface().get_size = Mock(return_value=(100, 100))
    pygame.event.get = Mock(return_value=[])


# Test if testImage is loaded
def test_TestImage():
    if frame is None:
        raise TypeError("No TestImage")


# Test the pinpointer with normal input
def test_Normal():
    mockPyGame()

    cameraWindow = CameraSubWindow()
    pinpointer = TestPinpointer(cameraWindow, True)
    pinpointer.GetHumanPositions(frame, 0)


# Test if the id's stay the same
def test_KeepID():
    mockPyGame()

    # Setup
    cameraWindow = CameraSubWindow()
    pinpointer = TestPinpointer(cameraWindow, True)

    # First click
    cameraWindow.MouseClick(pygame.MOUSEBUTTONDOWN, 10, 10)
    detections, frameIndex = pinpointer.GetHumanPositions(frame, 0)
    currentID = 0
    for detection in detections:
        currentID = detection.id

    # Second click
    cameraWindow.MouseClick(pygame.MOUSEBUTTONDOWN, 10, 10)
    detections, frameIndex = pinpointer.GetHumanPositions(frame, 0)
    for detection in detections:
        assert currentID == detection.id


# Test if the id's change
def test_NoKeepID():
    mockPyGame()

    # Setup
    cameraWindow = CameraSubWindow()
    pinpointer = TestPinpointer(cameraWindow, False)

    # First click
    cameraWindow.MouseClick(pygame.MOUSEBUTTONDOWN, 10, 10)
    detections, frameIndex = pinpointer.GetHumanPositions(frame, 0)
    currentID = 0
    for detection in detections:
        currentID = detection.id

    # Second click
    cameraWindow.MouseClick(pygame.MOUSEBUTTONDOWN, 10, 10)
    detections, frameIndex = pinpointer.GetHumanPositions(frame, 0)
    for detection in detections:
        assert currentID != detection.id


# Test if the pinpointer does not crash without a frame
def test_NullFrame():
    mockPyGame()

    cameraWindow = CameraSubWindow()
    pinpointer = TestPinpointer(cameraWindow, True)
    pinpointer.GetHumanPositions(None, 0)


# Test if the output of the pinpointer is the same as the mouse position
def test_NormalOutput():
    mockPyGame()

    cameraWindow = CameraSubWindow()
    pinpointer = TestPinpointer(cameraWindow, True)
    cameraWindow.MouseClick(pygame.MOUSEBUTTONDOWN, 10, 10)
    detections, frameIndex = pinpointer.GetHumanPositions(frame, 0)
    for detection in detections:
        assert detection.x == 10
        assert detection.y == 10


# Test if the output of negative position is also possible
def test_NegativeOutput():
    mockPyGame()

    cameraWindow = CameraSubWindow()
    pinpointer = TestPinpointer(cameraWindow, False)
    cameraWindow.MouseClick(pygame.MOUSEBUTTONDOWN, -10, -10)
    detections, frameIndex = pinpointer.GetHumanPositions(frame, 0)
    for detection in detections:
        assert detection.x == -10
        assert detection.y == -10

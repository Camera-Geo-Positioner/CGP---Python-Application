# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software Project course.
# © Copyright Utrecht University (Department of Information and Computing Sciences)

import cv2

from FrameAnalyzer.IDetector import *
from Windowing.Sub.CameraSubWindow import *


class TestPinpointer(IDetector):
    """
    An implementation of the IDetector interface.
    Uses the screen and the user to manually detect objects.
    """
    numberClicked: int = 0
    lastX: int = 0
    lastY: int = 0
    cameraWindow: CameraSubWindow = None

    # Constructor of the TestPinpointer, takes the name of the window to be used.
    # uses the window name to set up an opencv window
    def __init__(self, cameraWindow: CameraSubWindow, keepID: bool):
        """
        Constructor of the TestPinpointer, takes a CameraWindow to be used in the manual detection.

        Parameters
        ----------
        cameraWindow : CameraWindow
            The CameraWindow object used to create OpenCV windows for use in the manual detection.
        keepID : bool
            Boolean that indicates if new detections also need a new id.
        """
        self.numberClicked = 0
        self.lastX = 0
        self.lastY = 0
        self.cameraWindow = cameraWindow
        self.keepID = keepID

        if self.cameraWindow is not None:
            self.cameraWindow.SetShowPressed(True)

    def GetHumanPositions(self, inputFrame: numpy.ndarray, frameIndex: int):
        """
        Use the given frame and frameIndex to detect objects and return them as DetectedObject[].

        Parameters
        ----------
        inputFrame : numpy.ndarray
            The frame that is analyzed.
        frameIndex : int
            The index of the frame being analyzed.

        Returns
        -------
        DetectedObject[]
            An array of DetectedObject objects of type 'human'.
        """
        if inputFrame is None or self.cameraWindow is None:
            return [], frameIndex

        self.cameraWindow.ShowFrame(inputFrame)

        # Get the scaled and the absolute mouse position,
        # the scaled mouse position is used for rendering
        # purposes - the absolute mouse position is used for
        # pinpointing purposes
        mouseX, mouseY = self.cameraWindow.MousePosition()
        aMouseX, aMouseY = self.cameraWindow.ImageMousePosition()
        if self.cameraWindow.pressed and (self.lastX is not mouseX or self.lastY is not mouseY):
            mouseX, mouseY = self.cameraWindow.MousePosition()
            self.lastX = mouseX
            self.lastY = mouseY

            objectID = 1 if self.keepID else self.numberClicked
            self.numberClicked += 1

            # return a detected object with the mouse position - use the absolute
            # mouse position for this
            return [DetectedObject(aMouseX, aMouseY, objectID, 'human')], frameIndex

        return [], frameIndex

    def Close(self):
        return

# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software Project course.
# © Copyright Utrecht University (Department of Information and Computing Sciences)

"""
Interface for the different detection methods and the objects it returns.
"""

from collections import namedtuple
import numpy

DetectedObject = namedtuple('DetectionObject', ['x', 'y', 'id', 'type'])
"""
A detected object is a named tuple containing the X and Y coordinates,
an ID and the type of the object ('human', 'UFO', ...).
"""


class IDetector:
    """
    Interface for the different detector methods used in the MainFrameAnalyzer.
    """

    def GetHumanPositions(self, frame: numpy.ndarray, frameIndex: int):
        """
        Uses the given frame and frameIndex to detect objects and return them as DetectedObject[].

        Parameters
        ----------
        frame : numpy.ndarray
            The frame that is analyzed.
        frameIndex : int
            The index of the frame being analyzed.

        Returns
        -------
        DetectedObject[]
            An array of detected objects.
        """
        return [DetectedObject(1, 1, frameIndex, 0), DetectedObject(5, 5, frameIndex, 0)], frameIndex     # test output

    def Close(self):
        """
        Close any running processes of the detector.
        """
        pass

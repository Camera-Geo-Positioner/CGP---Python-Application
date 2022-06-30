# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software Project course.
# © Copyright Utrecht University (Department of Information and Computing Sciences)

import threading
from typing import Dict, Any

from FrameAnalyzer.IDetector import IDetector
from FrameAnalyzer.TestPinpointer import TestPinpointer
from Windowing.Sub.CameraSubWindow import CameraSubWindow


class DetectionFactory:
    """
    The Factory is used to create and retrieve a type of IDetector.
    """

    @staticmethod
    def CreateDetector(arguments: Dict[str, Any], videoAnalyzerCancelEvent: threading.Event,
                       subWindow: CameraSubWindow = None) -> IDetector:
        """
        Static function that returns a type of Detector based on the program arguments.

        Parameters
        ----------
        arguments: Dict[str, Any]
            The arguments passed to the program on startup.
        videoAnalyzerCancelEvent: threading.Event or None
            The cancel event is used to signal that the Frame Analyzer should clean up and close.
        subWindow : CameraSubWindow
            The subWindow used by the detection method

        Returns
        -------
        IDetector
            The Detector used to detect objects in videoframes.
        """
        detectorType = arguments['detector']

        if detectorType == "Manual":
            if videoAnalyzerCancelEvent is None:
                raise ValueError(__class__.__name__ + "No videoAnalyzerCancelEvent was passed to the Factory Method.")

            return TestPinpointer(subWindow, arguments['keepID'])

        elif detectorType == "DeepSocial":  # pragma: no cover
            from FrameAnalyzer.DeepSocialDetector import DeepSocialDetector
            return DeepSocialDetector(
                arguments["showDetections"],
                arguments["analyzeWidth"],
                arguments["analyzeHeight"],
                arguments["detectionThreshold"],
                subWindow
            )

        return IDetector()

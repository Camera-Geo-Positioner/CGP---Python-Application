# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software Project course.
# © Copyright Utrecht University (Department of Information and Computing Sciences)

"""
Pipeline object that handles the analyzing of the frames and detecting objects in these frames.
"""
import argparse
from typing import Dict, Any

import numpy
from datetime import datetime

from FrameAnalyzer.IDataWriteConnection import *
from FrameAnalyzer.IDetector import *


class MainFrameAnalyzer:
    """
    The main connecting component for analyzing frames.
    Analyzes the frames with the detectionMethod and sends the data via the dataWriteConnection.
    """
    dataWriteConnection: IDataWriteConnection = None
    detectionMethod: IDetector = None

    def __init__(self, detectionMethod: IDetector, dataWriteConnection: IDataWriteConnection):
        """

        Parameters
        ----------
        detectionMethod : IDetector
            One of the detection methods, e.g. DeepSocial.
        dataWriteConnection : IDataWriteConnection
            Connection to the API to send the data with.
        """
        self.dataWriteConnection = dataWriteConnection
        self.detectionMethod = detectionMethod

    def AnalyzeFrame(self, frame: numpy.ndarray, frameIndex: int, frameReadDatetime: datetime):
        """
        Uses the detectionMethod to create DetectedObject[] and sends this via the dataWriteConnection.

        Parameters
        ----------
        frame : numpy.ndarray
            The frame that is analyzed.
        frameIndex : int
            The index of the frame being analyzed.
        frameReadDatetime : datetime
            The time at which the frame was initially loaded into the system
        """
        # Detect positions if frame
        if self.detectionMethod is None or frame is None:
            return
        (detections, frameIndex) = self.detectionMethod.GetHumanPositions(frame, frameIndex)

        # Send data to next part
        if self.dataWriteConnection is None:
            return
        self.dataWriteConnection.WriteData(detections, frameIndex, frameReadDatetime)

    @staticmethod
    def AddFrameAnalyzerArguments(parser: argparse.ArgumentParser):  # pragma: no cover
        """
        Adds the arguments for the frame analyzer to the parser.

        Parameters
        ----------
        parser : argparse.ArgumentParser
            The parser that is used to add the arguments.
        """

        if parser is None:
            raise TypeError("Parser is none.")

        parser.add_argument("-d", "--detector", type=str, default='Manual',
                            help="The detector to use. Manual for TestPinpointer, DeepSocial for DeepSocial.")
        parser.add_argument("-sd", "--showDetections", action="store_true", default=False,
                            help="Whether to show the detections.")
        parser.add_argument("-dt", "--detectionThreshold", type=float, default=0.5,
                            help="The threshold for the confidence of the detections.")
        parser.add_argument("-k", "--keepID", action="store_true", default=False,
                            help="Boolean whether to keep using the same object ID during manual detection")

    @staticmethod
    def ValidateFrameAnalyzerArguments(arguments: Dict[str, Any]):
        """
        Validate the parsed arguments.

        Parameters
        ----------
        arguments : Dict[str, Any]
            The arguments that are validated
        """

        if arguments is None or not arguments:
            raise TypeError("Arguments are empty or None.")
        if arguments["detector"] not in ["Manual", "DeepSocial"]:
            raise ValueError("Detector must be Manual or DeepSocial.")
        if arguments["detectionThreshold"] < 0 or arguments["detectionThreshold"] > 1:
            raise ValueError("Detection threshold must be between 0 and 1.")
        if type(arguments["showDetections"]) is not bool:
            raise ValueError("Show detections must be a boolean (True or False).")
        if arguments["keepID"] == "" or arguments["keepID"] is None:
            raise ValueError("Object ID setting cannot be empty/none.")

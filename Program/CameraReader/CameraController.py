# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software Project course.
# © Copyright Utrecht University (Department of Information and Computing Sciences)

"""
Controller object for the Camera Video Reader.
Contains the actual video analyzer loop for running the pipeline.
"""

from threading import Event
from typing import Dict, Any

from CameraReader.CameraVideoReader import *
from FrameAnalyzer.MainFrameAnalyzer import *
import hashlib
import argparse


class CameraController:
    """Object to control the CameraVideoReader."""
    videoReader: VideoCapture = None

    def __init__(self):
        self.videoReader = None

    @staticmethod
    def AddVideoReaderArguments(parser: argparse.ArgumentParser):  # pragma: no cover
        """
        Parse the default video reader arguments.

        Parameters
        ----------
        parser : argparse.ArgumentParser
            The parser that parses the arguments
        """

        if parser is None:
            raise TypeError("Parser is none.")

        parser.add_argument("-l", "--fileOrStreamLocation",
                            # default="rtsp://user1:2D3Dproject@192.168.0.200:554/profile3/media.smp",
                            default="Testing/Assets/OxfordTownCentreDataset.mp4",
                            help="path to the video file or camera stream (rtsp)")
        parser.add_argument("-ah", "--analyzeHeight", type=int, default=540,
                            help="height of the output video stream")
        parser.add_argument("-aw", "--analyzeWidth", type=int, default=960, help="width of the output video stream")
        parser.add_argument("-v", "--isStream", action="store_true", default=False,
                            help="boolean whether the input is a camera-stream (True) or a video-file (False)")

    @staticmethod
    def ValidateReaderArguments(arguments: Dict[str, Any]):
        """
        Validate the parsed arguments.

        Parameters
        ----------
        arguments : Dict[str, Any]
            The arguments that are validated
        """
        if arguments is None or not arguments:
            raise TypeError("Arguments are empty or None.")
        if arguments["analyzeWidth"] < 1 or arguments["analyzeHeight"] < 1:
            raise ValueError("Video width or height cannot be smaller than 1.")
        if arguments["fileOrStreamLocation"] == "" or arguments["fileOrStreamLocation"] is None:
            raise ValueError("File or stream location cannot be empty/none.")
        if arguments["detector"] == "" or arguments["detector"] is None:
            raise ValueError("Detector type cannot be empty/none.")

    def StartVideoReader(self, arguments: Dict[str, Any]):
        """
        Create a video reader and start the video reader.

        Parameters
        ----------
        arguments : Dict[str, Any]
            The arguments needed to start the VideoReader

        Returns
        -------
        bool
            Successfully started
        """
        if arguments is None or not arguments:
            raise TypeError("Options are empty or None.")
        if "fileOrStreamLocation" not in arguments or "isStream" not in arguments:
            raise ValueError("Options does not contain required keys.")
        if arguments['fileOrStreamLocation'] is None or arguments['fileOrStreamLocation'] is "":
            return False
        self.videoReader = VideoCapture()
        self.videoReader.ConnectCaptureObject(arguments['fileOrStreamLocation'], arguments['isStream'])
        return self.videoReader.IsOpened()

    def StopVideoReader(self):
        """Stop the video reader."""
        if self.videoReader is None:
            return
        self.videoReader.ReleaseCaptureObject()
        self.videoReader = None

    def StartVideoAnalyzer(self, frameAnalyzer: MainFrameAnalyzer, targetWidth=960, targetHeight=540,
                           shouldStop: Event = None):
        """
        Start the video analyzer.
        Read frames from the CameraVideoReader in a loop and send them to the frameAnalyzer to analyze.

        Parameters
        ----------
        frameAnalyzer : MainFrameAnalyzer
            The MainFrameAnalyzer that is used for analyzing the frames
        targetWidth : int
            The targetWidth of the frame for analyzing
        targetHeight : int
            The targetHeight of the frame for analyzing
        shouldStop : Event
            Event that handles if the analyzing loop should stop
        """
        if frameAnalyzer is None:
            raise TypeError("Frame analyzer is none.")
        if self.videoReader is None:
            raise TypeError("Video reader is none.")
        if (targetWidth < 1) or (targetHeight < 1):
            raise ValueError("Video width or height cannot be smaller than 1.")
        if not self.videoReader.IsOpened():
            return

        # Loop through the video
        while shouldStop is None or not shouldStop.is_set():  # pragma: no cover
            videoStatus, frameRead, frameIndex, frameReadDatetime = self.videoReader.ReadLastFrame()
            if not videoStatus:
                break
            frameResized = cv2.resize(frameRead, (targetWidth, targetHeight), interpolation=cv2.INTER_LINEAR)
            frameAnalyzer.AnalyzeFrame(frameResized, frameIndex, frameReadDatetime)

    # analyze a single frame of the video
    def AnalyzeSingleFrame(self, frameAnalyzer: MainFrameAnalyzer, targetWidth=960, targetHeight=540):
        """
        Analyze a single frame from the CameraVideoReader.

        Parameters
        ----------
        frameAnalyzer : MainFrameAnalyzer
            The MainFrameAnalyzer that is used for analyzing the frames
        targetWidth : int
            The targetWidth of the frame for analyzing
        targetHeight : int
            The targetHeight of the frame for analyzing
        """
        if frameAnalyzer is None:
            raise TypeError("Frame analyzer is none.")
        if self.videoReader is None:
            raise TypeError("Video reader is none.")
        if (targetWidth < 1) or (targetHeight < 1):
            raise ValueError("Video width or height cannot be smaller than 1.")
        if not self.videoReader.IsOpened():
            return

        # Analyzer single frame
        if self.videoReader.IsOpened():  # pragma: no cover
            videoStatus, frameRead, frameIndex, frameReadDatetime = self.videoReader.ReadLastFrame()
            frameResized = cv2.resize(frameRead, (targetWidth, targetHeight), interpolation=cv2.INTER_LINEAR)
            frameAnalyzer.AnalyzeFrame(frameResized, frameIndex, frameReadDatetime)

    # determines unique identifier for the camera controller
    def GetUniqueIdentifier(self) -> str or None:
        """
        Generate a unique ID for the Camera Controller.

        Returns
        -------
        string
            The unique ID in string form
        """
        if self.videoReader is None:
            return None

        return hashlib.md5(self.videoReader.fileOrStreamLocation.encode('utf-8')).hexdigest()

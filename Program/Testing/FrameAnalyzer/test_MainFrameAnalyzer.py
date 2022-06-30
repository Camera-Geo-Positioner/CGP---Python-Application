# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software Project course.
# © Copyright Utrecht University (Department of Information and Computing Sciences)


import cv2
from datetime import datetime
from unittest import TestCase
import pytest
from FrameAnalyzer.MainFrameAnalyzer import *
from FrameAnalyzer.IDetector import *
from FrameAnalyzer.IDataWriteConnection import *


class TestMainFrameAnalyzer(TestCase):

    def setUp(self):
        self.argumentParser = argparse.ArgumentParser()
        self.detector = IDetector()
        self.dataWriteConnection = IDataWriteConnection()
        self.frame = cv2.imread('Testing/Assets/testImage.png', 1)
        if self.frame is None:
            self.frame = cv2.imread('Program/Testing/Assets/testImage.png', 1)

    def test_AddArguments(self):
        self.assertRaises(TypeError, MainFrameAnalyzer.AddFrameAnalyzerArguments, None)

        addArgs = MainFrameAnalyzer.AddFrameAnalyzerArguments(self.argumentParser)
        assert(addArgs is None)

    def test_ValidateArguments(self):
        self.assertRaises(TypeError, MainFrameAnalyzer.ValidateFrameAnalyzerArguments, None)

    def test_ValidateArgumentsValueError(self):
        arguments = {
            'detector': 'wrong',
            'showDetections': True,
            'detectionThreshold': 0.5
        }
        self.assertRaises(ValueError, MainFrameAnalyzer.ValidateFrameAnalyzerArguments, arguments)
        arguments = {
            'detector': 'Manual',
            'showDetections': "notabool",
            'detectionThreshold': 0.5
        }
        self.assertRaises(ValueError, MainFrameAnalyzer.ValidateFrameAnalyzerArguments, arguments)
        arguments = {
            'detector': 'Manual',
            'showDetections': False,
            'detectionThreshold': -0.1
        }
        self.assertRaises(ValueError, MainFrameAnalyzer.ValidateFrameAnalyzerArguments, arguments)
        arguments = {
            'detector': 'Manual',
            'showDetections': True,
            'detectionThreshold': 1.1
        }
        self.assertRaises(ValueError, MainFrameAnalyzer.ValidateFrameAnalyzerArguments, arguments)

    # Test if frame analyzer works with normal input
    def test_Normal(self):
        frameAnalyzer = MainFrameAnalyzer(self.detector, self.dataWriteConnection)
        frameAnalyzer.AnalyzeFrame(self.frame, 0, datetime.now())

    # Test if frame analyzer does not crash without a frame
    def test_NullFrame(self):
        frameAnalyzer = MainFrameAnalyzer(self.detector, self.dataWriteConnection)
        frameAnalyzer.AnalyzeFrame(None, 0, datetime.now())

    # Test if frame analyzer does not crash without a detector
    def test_NullDetector(self):
        frameAnalyzer = MainFrameAnalyzer(None, self.dataWriteConnection)
        frameAnalyzer.AnalyzeFrame(self.frame, 0, datetime.now())

    # Test if frame analyzer does not crash without a data write connection
    def test_NullWriteConnection(self):
        frameAnalyzer = MainFrameAnalyzer(self.detector, None)
        frameAnalyzer.AnalyzeFrame(self.frame, 0, datetime.now())

    # Test if frame analyzer does not crash when there is an empty return from the detector
    def test_EmptyReturn(self):
        emptyDetector = EmptyDetector()
        frameAnalyzer = MainFrameAnalyzer(emptyDetector, self.dataWriteConnection)
        frameAnalyzer.AnalyzeFrame(self.frame, 0, datetime.now())


# Test implementation of the IDetector
class EmptyDetector(IDetector):

    # Test implementation that returns an empty list
    def GetHumanPositions(self, f, frameIndex: int):
        return [], frameIndex     # test output

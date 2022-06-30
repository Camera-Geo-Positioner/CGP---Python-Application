# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software Project course.
# © Copyright Utrecht University (Department of Information and Computing Sciences)
import threading

import pytest

from FrameAnalyzer.IDetector import IDetector
from FrameAnalyzer.TestPinpointer import TestPinpointer
from FrameAnalyzer.DetectionFactory import DetectionFactory


class TestDetectionFactory:

    @pytest.mark.parametrize("arguments", [
        {
            'analyzeWidth': 960,
            'analyzeHeight': 540,
            'fileOrStreamLocation': 'loc',
            'isStream': False,
            'detector': 'Manual',
            'keepID': True,
        }
    ])
    def test_CreateTestPinpointer(self, arguments):

        with pytest.raises(ValueError):
            DetectionFactory.CreateDetector(arguments, None)

        detector = DetectionFactory.CreateDetector(arguments, threading.Event())

        assert(type(detector) is TestPinpointer)

    @pytest.mark.parametrize("arguments", [
        {
            'detector': 'randomString',
        }
    ])
    def test_CreateIDetector(self, arguments):
        detector = DetectionFactory.CreateDetector(arguments, None)

        assert(type(detector) is IDetector)

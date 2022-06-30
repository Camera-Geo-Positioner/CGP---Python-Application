# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software Project course.
# © Copyright Utrecht University (Department of Information and Computing Sciences)
import builtins

import Main as ma
from Main import *
from CameraReader.CameraController import *
from CameraReader.CameraVideoReader import *
from Calibrator.MainCalibrator import *
import pytest
import unittest
from unittest.mock import Mock, MagicMock, patch
import asyncio
import numpy as np
import random


@pytest.mark.last
class MyTestCase(unittest.TestCase):

    @staticmethod
    def MockObjects():
        videoAnalyzerCancelEvent.clear()
        videoAnalyzerCancelEvent.clear()

        # video reader
        VideoCapture.ConnectCaptureObject = Mock()
        VideoCapture.ReadLastFrame = MagicMock()
        VideoCapture.ReadLastFrame.return_value = [None, None]
        VideoCapture.IsOpened = Mock()
        VideoCapture.IsOpened.return_value = True
        CameraController.GetUniqueIdentifier = Mock()
        CameraController.GetUniqueIdentifier.return_value = 0

        # calibrator
        MainCalibrator.Calibrate = Mock()
        MainCalibrator.Calibrate.return_value = None

        # CameraWindow
        MasterWindow.instance = None
        MasterWindow.Open = Mock()

    @pytest.mark.order(2)
    @patch('cv2.resize', MagicMock(return_value=np.array([[[255, 255, 255]]])))
    def test_PositionerPipelineObjectCreation(self):
        self.MockObjects()
        pipeline = PositionerPipeline()
        MainCalibrator.calibrated = True

        arguments = {
            'analyzeWidth': 960,
            'analyzeHeight': 540,
            'fileOrStreamLocation': 'loc',
            'isStream': False,
            'detector': 'Manual',
            'keepID': True,
            'noEncryption': True
        }
        CameraController.ValidateReaderArguments(arguments)

        api = Mock()

        pipeline._Startup(api, arguments)

        assert pipeline.cameraController is not None
        assert pipeline.mainWindow is not None
        assert pipeline.frameAnalyzer is not None
        assert calibrationDoneEvent.is_set()
        assert not videoAnalyzerCancelEvent.is_set()

        pipeline._Cleanup()

        assert calibrationDoneEvent.is_set()
        assert videoAnalyzerCancelEvent.is_set()
        assert pipeline.cameraController.videoReader is None

    @pytest.mark.order(1)
    @patch('cv2.resize', MagicMock(return_value=np.array([[[255, 255, 255]]])))
    def test_CalibrationFail(self):
        self.MockObjects()
        pipeline = PositionerPipeline()
        MainCalibrator.calibrated = False

        arguments = {
            'analyzeWidth': 960,
            'analyzeHeight': 540,
            'fileOrStreamLocation': 'loc',
            'isStream': False,
            'detector': 'Manual',
            'keepID': True,
            'noEncryption': True
        }
        CameraController.ValidateReaderArguments(arguments)

        api = Mock()

        pipeline._Startup(api, arguments)

        assert pipeline.cameraController is not None
        assert pipeline.cameraController.videoReader is None
        assert calibrationDoneEvent.is_set()
        assert videoAnalyzerCancelEvent.is_set()

        pipeline._Cleanup()

        assert calibrationDoneEvent.is_set()
        assert videoAnalyzerCancelEvent.is_set()
        assert pipeline.cameraController.videoReader is None

    @pytest.mark.order(3)
    @patch('cv2.resize', MagicMock(return_value=np.array([[[255, 255, 255]]])))
    def test_NoCamera(self):
        self.MockObjects()
        pipeline = PositionerPipeline()
        MainCalibrator.calibrated = False
        VideoCapture.IsOpened.return_value = False

        arguments = {
            'analyzeWidth': 960,
            'analyzeHeight': 540,
            'fileOrStreamLocation': 'loc',
            'isStream': False,
            'detector': 'Manual',
            'keepID': True,
            'noEncryption': True
        }
        CameraController.ValidateReaderArguments(arguments)

        api = Mock()

        pipeline._Startup(api, arguments)

        assert pipeline.cameraController is not None
        assert pipeline.cameraController.videoReader is None
        assert calibrationDoneEvent.is_set()
        assert videoAnalyzerCancelEvent.is_set()

        pipeline._Cleanup()

        assert calibrationDoneEvent.is_set()
        assert videoAnalyzerCancelEvent.is_set()
        assert pipeline.cameraController.videoReader is None

    @pytest.mark.order(4)
    @patch('cv2.resize', MagicMock(return_value=np.array([[[255, 255, 255]]])))
    def test_Main(self):
        self.MockObjects()
        MainCalibrator.calibrated = False
        poort = random.randint(11000, 12000)

        arguments = {
            'analyzeWidth': 960,
            'analyzeHeight': 540,
            'fileOrStreamLocation': 'loc',
            'isStream': False,
            'detector': 'Manual',
            'detectionThreshold': 0.5,
            'showDetections': True,
            'calibrator': 'None',
            'forceRecalibrate': False,
            'keepID': True,
            'port': poort,
            'displayArgsGUI': False,
            'noEncryption': True
        }
        CameraController.ValidateReaderArguments(arguments)
        ma.CommandInput = self.CommandInput2

        argparse.ArgumentParser.parse_args = Mock(return_value=arguments)
        builtins.vars = Mock(return_value=arguments)
        testProgram = Program()
        asyncio.run(testProgram.Main())

    @staticmethod
    async def CommandInput2(api: APIController):
        try:
            calibrationDoneEvent.wait()

            while True:
                break
        except concurrent.futures.CancelledError:
            return

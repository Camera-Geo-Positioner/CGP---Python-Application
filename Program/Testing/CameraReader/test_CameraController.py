# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software Project course.
# © Copyright Utrecht University (Department of Information and Computing Sciences)


from unittest import TestCase
from unittest.mock import Mock
from CameraReader.CameraController import *
import pytest


class TestCameraController(TestCase):

    def setUp(self):
        self.cameraController = CameraController()

    def test_add_video_reader_arguments_none(self):
        self.assertRaises(TypeError, self.cameraController.AddVideoReaderArguments, None)

    def test_start_video_analyzer(self):
        self.assertRaises(TypeError, self.cameraController.StartVideoAnalyzer, None)

    def test_start_video_reader_valid_check(self):
        cameraController = CameraController()
        cameraController.videoReader = Mock()
        try:
            cameraController.StartVideoReader({"fileOrStreamLocation": "location", "isStream": True})
        except TypeError:
            assert False
        assert True


start_video_reader_data = [({"test: 0"}, ValueError),
                           ({"fileOrStreamLocation": "location"}, ValueError),
                           ({"isStream": True}, ValueError),
                           (None, TypeError),
                           ({}, TypeError)]


@pytest.mark.parametrize("options,expected", start_video_reader_data)
def test_start_video_reader_exceptions(options, expected):
    cameraController = CameraController()
    pytest.raises(expected, cameraController.StartVideoReader, options)


validate_reader_arguments_data = [({"analyzeWidth": 0, "analyzeHeight": 10, "fileOrStreamLocation": "loc"}, ValueError),
                                  ({"analyzeWidth": 10, "analyzeHeight": 0, "fileOrStreamLocation": "loc"}, ValueError),
                                  ({"analyzeWidth": 10, "analyzeHeight": 10, "fileOrStreamLocation": ""}, ValueError),
                                  ({"analyzeWidth": 10, "analyzeHeight": 10, "fileOrStreamLocation": None}, ValueError),
                                  ({}, TypeError),
                                  (None, TypeError)]


@pytest.mark.parametrize("arguments,expected", validate_reader_arguments_data)
def test_validate_reader_arguments(arguments, expected):
    cameraController = CameraController()
    pytest.raises(expected, cameraController.ValidateReaderArguments, arguments)


def test_stop_video_reader_none():
    cameraController = CameraController()
    cameraController.videoReader = None
    cameraController.StopVideoReader()
    assert cameraController.videoReader is None


def test_stop_video_reader_some():
    cameraController = CameraController()
    cameraController.videoReader = Mock()
    cameraController.StopVideoReader()
    assert cameraController.videoReader is None


start_video_analyzer_data = [(None, 0, 0, TypeError),
                             (MainFrameAnalyzer, 0, 0, ValueError),
                             (MainFrameAnalyzer, 1, 0, ValueError),
                             (MainFrameAnalyzer, 0, 1, ValueError)]


@pytest.mark.parametrize("mainFrameAnalyzer,analyzeWidth,analyzeHeight,expected", start_video_analyzer_data)
def test_start_video_analyzer_exceptions(mainFrameAnalyzer, analyzeWidth, analyzeHeight, expected):
    cameraController = CameraController()
    cameraController.videoReader = VideoCapture
    pytest.raises(expected, cameraController.StartVideoAnalyzer, mainFrameAnalyzer, analyzeWidth, analyzeHeight)


def test_start_video_analyzer_video_none():
    cameraController = CameraController()
    cameraController.videoReader = None
    pytest.raises(TypeError, cameraController.StartVideoAnalyzer, MainFrameAnalyzer, 1, 1)


def test_start_video_analyzer_video_none():
    cameraController = CameraController()
    videoReader = Mock()
    cameraController.videoReader = videoReader
    pytest.raises(ValueError, cameraController.StartVideoAnalyzer, MainFrameAnalyzer, -1, -1)


def test_start_video_analyzer_video_check():
    cameraController = CameraController()
    mainFrameAnalyzer = Mock()
    videoReader = Mock()
    cameraController.videoReader = videoReader
    mainFrameAnalyzer.AnalyzeFrame.return_value = None
    videoReader.IsOpened.return_value = False
    try:
        cameraController.StartVideoAnalyzer(mainFrameAnalyzer, 1, 1)
    except TypeError:
        assert False


def test_analyze_single_frame_video_none():
    cameraController = CameraController()
    cameraController.videoReader = None
    pytest.raises(TypeError, cameraController.AnalyzeSingleFrame, MainFrameAnalyzer, 1, 1)


def test_analyzer_single_frame_video_negative_size():
    cameraController = CameraController()
    videoReader = Mock()
    cameraController.videoReader = videoReader
    pytest.raises(ValueError, cameraController.AnalyzeSingleFrame, MainFrameAnalyzer, -1, -1)


def test_analyze_single_frame_video_check():
    cameraController = CameraController()
    mainFrameAnalyzer = Mock()
    videoReader = Mock()
    cameraController.videoReader = videoReader
    mainFrameAnalyzer.AnalyzeFrame.return_value = None
    videoReader.IsOpened.return_value = False
    try:
        cameraController.AnalyzeSingleFrame(mainFrameAnalyzer, 1, 1)
    except TypeError:
        assert False


def test_GetUniqueIdentifier():
    cameraController = CameraController()
    assert cameraController.GetUniqueIdentifier() is None

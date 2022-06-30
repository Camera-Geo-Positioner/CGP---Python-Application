# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software Project course.
# © Copyright Utrecht University (Department of Information and Computing Sciences)

import argparse
import pytest
from unittest import TestCase
from unittest.mock import Mock, MagicMock, patch

import Calibrator.Configurations.ICalibrationConfiguration
from Calibrator.Configurations.HomographyCalibrationConfiguration import HomographyCalibrationConfiguration
from Calibrator.Configurations.ICalibrationConfiguration import ICalibrationConfiguration
from Calibrator.MainCalibrator import MainCalibrator, CalibrationMethods, CalibrationConfigurations
from Calibrator.Methods.HomographyCalibrationMethod import HomographyCalibrationMethod


class TestMainCalibrator(TestCase):

    def setUp(self):
        self.argumentParser = argparse.ArgumentParser()

    def test_AddArguments(self):
        self.assertRaises(TypeError, MainCalibrator.AddCalibratorArguments, None)

        addArgs = MainCalibrator.AddCalibratorArguments(self.argumentParser)
        assert(addArgs is None)

    def test_ValidateArguments(self):
        self.assertRaises(TypeError, MainCalibrator.ValidateCalibratorArguments, None)

    def test_ValidateArgumentsValueError(self):
        arguments = {
            'calibrator': 'randomString',
            'forceRecalibrate': True
        }
        self.assertRaises(ValueError, MainCalibrator.ValidateCalibratorArguments, arguments)
        arguments = {
            'calibrator': 'None',
            'forceRecalibrate': 'notABool',
        }
        self.assertRaises(ValueError, MainCalibrator.ValidateCalibratorArguments, arguments)
        arguments = {
            'calibrator': 'Homography',
            'forceRecalibrate': True
        }
        result = MainCalibrator.ValidateCalibratorArguments(arguments)
        assert(result is None)

    def test_Calibrate1(self):
        for calibrationMethod in CalibrationMethods.__members__.keys():
            if not (calibrationMethod in CalibrationConfigurations.__members__.keys()):
                assert \
                    False, \
                    "Calibration method " + str(calibrationMethod) + " is not in the CalibrationConfigurations."

        for calibrationConfiguration in CalibrationConfigurations.__members__.keys():
            if not (calibrationConfiguration in CalibrationMethods.__members__.keys()):
                assert \
                    False, \
                    "Calibration configuration " + str(calibrationConfiguration) + " is not in the CalibrationMethods."

    def test_Calibrate2(self):
        arguments = {
            'calibrator': 'None',
            'forceRecalibrate': False
        }
        result = MainCalibrator.Calibrate(Mock(), Mock(), Mock(), arguments)

        assert(result is None)

    def test_Calibrate3(self):
        arguments = {
            'calibrator': 'Homography',
            'forceRecalibrate': False
        }
        configuration = HomographyCalibrationConfiguration()
        p = patch(
            "Calibrator.MainCalibrator.MainCalibrator.GetConfiguredCalibrationMethod",
            new=MagicMock(return_value=configuration))
        p.start()
        result = MainCalibrator.Calibrate(Mock(), Mock, Mock(), arguments)

        assert(result == configuration)

        p.stop()

    def test_Calibrate4(self):
        arguments = {
            'calibrator': 'Homography',
            'forceRecalibrate': True
        }
        configuration = HomographyCalibrationConfiguration()
        p = patch(
            "Calibrator.MainCalibrator.MainCalibrator.PerformCalibrationMethod",
            new=MagicMock(return_value=configuration)
        )
        p.start()
        result = MainCalibrator.Calibrate(Mock(), Mock(), Mock(), arguments)

        assert MainCalibrator.calibrated
        assert result == configuration
        p.stop()

    # def test_PerformCalibrationMethod(self):
    #     # Mock and test all calibration methods, check if they return the correct type of data.
    #     for calibrationMethod in CalibrationMethods.__members__.keys():
    #         CalibrationConfigurations[calibrationMethod].value.Save = Mock()
    #         configuration = CalibrationConfigurations[calibrationMethod].value()
    #         CalibrationMethods[calibrationMethod].value.MakeWorldRepresentation = MagicMock(
    #             return_value=configuration
    #         )
    #
    #         result = MainCalibrator.PerformCalibrationMethod(calibrationMethod, None, None, None)
    #         assert \
    #             result == configuration, \
    #             "Calibration method " + str(calibrationMethod) + " did not calibrate with identity."

    def test_PerformCalibrationMethod1(self):
        # Test the first return path
        p = patch(
            "Calibrator.Methods.HomographyCalibrationMethod.HomographyCalibrationMethod.MakeWorldRepresentation",
            new=MagicMock(return_value=None)
        )
        p.start()
        result = MainCalibrator.PerformCalibrationMethod("Homography", "123", None, None)
        assert(result is None)
        p.stop()

    def test_PerformCalibrationMethod2(self):
        # Test the second return path
        configuration = HomographyCalibrationConfiguration()
        configuration.Save = Mock()
        p = patch(
            "Calibrator.Methods.HomographyCalibrationMethod.HomographyCalibrationMethod.MakeWorldRepresentation",
            new=MagicMock(return_value=configuration)
        )
        p.start()

        result = MainCalibrator.PerformCalibrationMethod("Homography", "123", None, None)
        assert(result is configuration)

        p.stop()

    def test_GetConfiguredCalibrationMethod(self):
        # p = patch(
        #     "Calibrator.Configurations.ICalibrationConfiguration.ICalibrationConfiguration.Exists",
        #     new=MagicMock(return_value=False)
        # )
        # p.start()
        result = MainCalibrator.GetConfiguredCalibrationMethod(None, "Homography", MagicMock())
        assert(result is None)
        # p.stop()

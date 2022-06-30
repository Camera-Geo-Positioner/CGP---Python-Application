# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software Project course.
# © Copyright Utrecht University (Department of Information and Computing Sciences)

"""
Controller object for the calibration, handles the choosing of different calibration methods.
"""
import argparse
from enum import Enum
from typing import Dict, Any

import cv2

from Calibrator.Configurations.ICalibrationConfiguration import ICalibrationConfiguration

# Calibration methods - Imports
from Calibrator.Methods.HomographyCalibrationMethod import HomographyCalibrationMethod

# Calibration configuration - Imports
from Calibrator.Configurations.HomographyCalibrationConfiguration import HomographyCalibrationConfiguration


# Calibration methods - Enum
class CalibrationMethods(Enum):
    Homography = HomographyCalibrationMethod


# Calibration configurations - Enum
class CalibrationConfigurations(Enum):
    Homography = HomographyCalibrationConfiguration


# Calibrator class which contains the calibration methods and the configuration handling
class MainCalibrator:
    calibrated = False

    @staticmethod
    def Calibrate(cameraId, srcImage, masterWindow, arguments) -> ICalibrationConfiguration or None:
        """Enter UI menu where the user can specify the calibration method and perform the calibration

            Parameters
            ----------
            cameraId: string
                The camera id of the camera to calibrate.
            srcImage: numpy.ndarray
                The source image to perform the calibration on.
            masterWindow: MasterWindow
                The master window object
            arguments : Dict[str, Any]
                The arguments of the program.

            Returns
            -------
            ICalibrationConfiguration or None
                The configuration of the calibration method or None if the calibration failed.
        """
        # Retrieve the program arguments that are relevant for calibration.
        # The calibration method is either 'Homography' or 'None'
        calibrationMethod = arguments['calibrator']
        forceRecalibrate = arguments['forceRecalibrate']

        if calibrationMethod == 'None':
            MainCalibrator.calibrated = True
            return None

        if not forceRecalibrate:
            # Try to find a configured calibration method
            # print('[Calibrator] Searching for calibration configurations of camera #' + str(cameraId))
            configuration = MainCalibrator.GetConfiguredCalibrationMethod(cameraId, calibrationMethod, arguments)

            # If a configuration exists, use it.
            if configuration is not None:
                MainCalibrator.calibrated = True
                return configuration

        # Perform calibration with the chosen method.
        newConfiguration = MainCalibrator.PerformCalibrationMethod(calibrationMethod, cameraId, srcImage, masterWindow)
        if newConfiguration is not None:
            # If the calibration was successful, we return the configuration
            MainCalibrator.calibrated = True
            return newConfiguration

        # Calibration failed.
        return None

    @staticmethod
    def PerformCalibrationMethod(method, cameraId, srcImage, masterWindow) -> ICalibrationConfiguration or None:
        """ Perform the calibration method

            Parameters
            ----------
            method: string
                The name of the calibration method to perform
            cameraId: string
                The camera id of the camera to calibrate
            srcImage: numpy.ndarray
                The source image to perform the calibration on
            masterWindow: MasterWindow
                The master window object

            Returns
            -------
            ICalibrationConfiguration or None

            The configuration of the calibration method or None if the calibration failed
        """

        # Create the calibration method and perform the calibration
        calibrator = CalibrationMethods[method].value()
        configuration = calibrator.MakeWorldRepresentation(srcImage, masterWindow)
        if configuration is None:
            # print('[Calibrator] Calibration with method ' + str(method) + ' failed!')
            return None

        # Save the configuration
        configuration.Save(cameraId)

        # Return the configuration
        # print('[Calibrator] Calibration with method ' + str(method) + ' succeeded!')
        return configuration

    @staticmethod
    def GetConfiguredCalibrationMethod(cameraId, calibrationMethod, arguments) -> ICalibrationConfiguration or None:
        """ Get a configured calibration method

            Parameters
            ----------
            cameraId: string
                The camera id of the camera to get the calibration method for
            calibrationMethod: string
                The name of the calibration method to get

            Returns
            -------
            ICalibrationConfiguration or None
                The configuration of the calibration method or None if the calibration method is not configured
        """

        # Check if the calibration method configuration exists
        exists = ICalibrationConfiguration.Exists(CalibrationConfigurations[calibrationMethod].value, cameraId)

        # If the configuration does not exist, return nothing
        if not exists:
            return None

        # Return the configuration
        configuration = CalibrationConfigurations[calibrationMethod].value()

        try:
            configuration.Load(cameraId, arguments)
        except:
            return None
        return configuration

    @staticmethod
    def AddCalibratorArguments(parser: argparse.ArgumentParser):
        """ Add the arguments for the calibrator to the parser

            Parameters
            ----------
            parser: argparse.ArgumentParser
                The parser to add the arguments to
        """
        if parser is None:
            raise TypeError("Parser is none.")

        # Add the calibrator arguments
        parser.add_argument('-c', '--calibrator', default='Homography', help='Calibration method (None or Homography)')
        parser.add_argument('-f', '--forceRecalibrate', action="store_true", default=False,
                            help='Use an existing calibration (if exists)')

    @staticmethod
    def ValidateCalibratorArguments(arguments: Dict[str, Any]):
        """ Validate the calibrator arguments.

            Parameters
            ----------
            arguments: Dict[str, Any]
                The arguments to validate.
        """
        # Check if the calibrator is valid
        if arguments['calibrator'] not in ['None', 'Homography']:
            raise ValueError('Calibrator must be None or Homography')
        if type(arguments['forceRecalibrate']) is not bool:
            raise ValueError('forceRecalibrate must be a boolean')

        # print(arguments['forceRecalibrate'])

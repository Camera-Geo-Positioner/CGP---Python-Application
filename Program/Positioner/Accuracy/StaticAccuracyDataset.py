# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software Project course.
# © Copyright Utrecht University (Department of Information and Computing Sciences)

import argparse
import os
from types import SimpleNamespace
from typing import Dict

from Calibrator.Configurations.HomographyCalibrationConfiguration import HomographyGeoData, GeoPosition
from Calibrator.Configurations.ICalibrationConfiguration import ICalibrationConfiguration
from Calibrator.ImageReceiver.MapBoxAPI import MapBoxAPI
from Calibrator.ImageReceiver.CycloMedia import CycloMedia
from Calibrator.ImageReceiver.SmartImage import SmartImage
from IO.SerializableJSON import SerializableJSON
from Windowing.MasterWindow import MasterWindow
from Calibrator.Methods.HomographyCalibrationMethod import HomographyCalibrationMethod
from CameraReader.CameraController import *


class StaticAccuracyDataset(SerializableJSON):
    viewImagePath = None
    topDownImagePath = None
    origin = None
    resolution: float = None
    entries = []
    calibrationConfigurations = {}

    @staticmethod
    def RunStaticAccuracyDataSet(arguments):
        # We should calibrate a static dataset
        print(
            "Calibrating static dataset with path \"{}\" and method '{}'.".format(
                arguments["calibrateDataSet"],
                arguments["calibrateDataSetMethod"]
            )
        )
        # Setup CameraWindow
        mainWindow = MasterWindow(1080, 640, "Watchful Eye")
        mainWindow.Open(True, None)

        # Setup Camera
        cameraController = CameraController()
        connected = cameraController.StartVideoReader(arguments)
        if connected:
            StaticAccuracyDataset.CalibrateDatasetWithMethod(
                arguments["calibrateDataSet"], arguments["calibrateDataSetMethod"],
                mainWindow
            )
        mainWindow.Close()
        return

    def GetCalibrationConfiguration(self, calibrationConfiguration):
        """ Returns the calibration configuration with the given name.

         Parameters
         ----------
         calibrationConfiguration : str
             The name of the calibration configuration.

         Returns
         -------
         CalibrationConfiguration
             The calibration configuration with the given name.
         """

        # Check if the calibration configuration exists.
        if calibrationConfiguration not in self.calibrationConfigurations:
            raise KeyError("The calibration configuration '" + calibrationConfiguration + "' does not exist.")

        # Nested parsing to simple namespace object
        def parse(d):
            x = SimpleNamespace()
            _ = [setattr(x, k, parse(v)) if isinstance(v, dict) else setattr(x, k, v) for k, v in d.items()]
            return x

        return parse(self.calibrationConfigurations[calibrationConfiguration])

    @staticmethod
    def Load(path):
        """ Loads the StaticAccuracyDataset from the given path.

         Parameters
         ----------
         path : str
             The path to the StaticAccuracyDataset.

         Returns
         -------
         StaticAccuracyDataset
             The StaticAccuracyDataset loaded from the given path.
         """

        staticAccuracyDataset = StaticAccuracyDataset()
        staticAccuracyDataset.FromJSON(path)
        return staticAccuracyDataset

    @staticmethod
    def AddStaticAccuracyDatasetArguments(parser: argparse.ArgumentParser):
        """
        Parse the default static accuracy dataset arguments.

        Parameters
        ----------
        parser : argparse.ArgumentParser
            The parser that parses the arguments
        """
        parser.add_argument("-cds", "--calibrateDataSet", default="",
                            help="path to the dataset that should be calibrated")
        parser.add_argument("-cdsm", "--calibrateDataSetMethod", default="",
                            help="method of the dataset that should be calibrated")

    @staticmethod
    def ValidateStaticAccuracyDatasetArguments(arguments: Dict[str, Any]) -> bool:
        """
        Validate the parsed arguments.

        Parameters
        ----------
        arguments : Dict[str, Any]
            The arguments that are validated
        """
        if arguments is None or not arguments:
            raise TypeError("Arguments are empty or None.")
        if arguments.__contains__("calibrateDataSet") \
                and arguments["calibrateDataSet"] is not "":
            if not arguments.__contains__("calibrateDataSetMethod") \
                    or arguments["calibrateDataSetMethod"] is "":
                raise ValueError("The method of the dataset that should be calibrated is not set.")
            if not os.path.exists(arguments["calibrateDataSet"]):
                raise ValueError("The dataset that should be calibrated does not exist.")
            return True
        return False

    @staticmethod
    def CalibrateDatasetWithMethod(path: str, methodName: str, masterWindow: MasterWindow):  # pragma: no cover
        """

        Parameters
        ----------
        path :
            filepath of dataset
        methodName : str
            name of method to do the calibration
        masterWindow : MasterWindow
            The window that the calibration uses

        """
        # Load the dataset
        dataset = StaticAccuracyDataset.Load(path)

        # Get the origin and resolution in screen space
        origin = dataset.origin  # Screen space coordinate, where (0, 0) world space coordinate
        resolution = dataset.resolution  # The amount of units per pixel, from the topdown image

        # Load the view and topdown image
        viewImage = cv2.imread(dataset.viewImagePath)
        topDownImage = cv2.imread(dataset.topDownImagePath)

        # Switch on method
        configuration = None
        print("Calibrating dataset with method '" + methodName + "'.")

        if methodName.lower() == "homography":
            methodName = "HomographyCalibrationConfiguration"
            # Overwrite the MapBox default call to create
            # a geo smart image based on the dataset
            MapBoxAPI.CreateGeoSmartImage = lambda _: (
                SmartImage(topDownImage),
                HomographyGeoData(
                    (origin[0], origin[1]),
                    GeoPosition(
                        latitude=0,
                        longitude=0,
                        altitude=0
                    ),
                    resolution
                )
            )
            CycloMedia.CreateGeoSmartImage = lambda _, __: (
                SmartImage(topDownImage),
                HomographyGeoData(
                    (origin[0], origin[1]),
                    GeoPosition(
                        latitude=0,
                        longitude=0,
                        altitude=0
                    ),
                    resolution
                )
            )

            # Make the world representation
            method = HomographyCalibrationMethod()
            configuration = method.MakeWorldRepresentation(viewImage, masterWindow)

        # No valid method found
        else:
            raise ValueError("The calibration method '" + methodName + "' does not exist.")

        # Check if configuration is valid
        if configuration is None:
            print("No valid configuration was created, exiting..")
            return

        # Overwrite the default ICalibrationConfiguration save call
        # to save the configuration to the dataset
        ICalibrationConfiguration.Save = lambda x, y: dataset.ToJSON(path, 1)

        # Set the configuration as a reference
        dataset.calibrationConfigurations[methodName] = configuration

        # Save the configuration using its custom saving method,
        # this handles necessary data conversion
        configuration.Save(-1)
        print("Calibration with dataset at \"{}\" with method '{}' successful!".format(path, methodName))


class StaticAccuracyError:
    maxError = 0
    averageError = 0
    numberOfErrors = 0

    def AddError(self, nextError):
        """ Adds two StaticAccuracyErrors, and averages the results.

        Parameters
        ----------
        nextError : float
            new error in meters
        """

        self.numberOfErrors += 1
        self.averageError += nextError

        if nextError > self.maxError:
            self.maxError = nextError

    def AverageErrors(self):
        """
        Turns the accumulated error into an average error
        """
        self.averageError /= self.numberOfErrors

    def GetMaxError(self):
        """
        Returns
        -------
        the max error attribute
        """
        return self.maxError

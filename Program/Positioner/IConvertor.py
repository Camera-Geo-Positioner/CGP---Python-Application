# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software Project course.
# © Copyright Utrecht University (Department of Information and Computing Sciences)

"""
Interface for the different conversion methods.
"""

import os
import geopy.distance
import math
import numpy as np

from Calibrator.Configurations.ICalibrationConfiguration import ICalibrationConfiguration
from FrameAnalyzer.IDetector import DetectedObject
from IO import Pathing
from Positioner.Accuracy.StaticAccuracyDataset import StaticAccuracyDataset, StaticAccuracyError
from Positioner.DetectedObjectPosition import DetectedObjectPosition


class IConvertor:
    """
    Interface for the different conversion methods used in the MainPositioner.
    """
    configuration: ICalibrationConfiguration = None
    staticError: StaticAccuracyError = None

    def __init__(self, configuration: ICalibrationConfiguration):
        """
        Constructor of the IConvertor, takes a worldRepresentation to convert data.

        Parameters
        ----------
        configuration : ICalibrationConfiguration|None
            The configuration used for conversion.
        """

        # Set the configuration
        self.configuration = configuration

        # Call calculate static error by default
        if self.configuration is not None and isinstance(self.configuration, ICalibrationConfiguration):
            self._CalculateStaticError()

    def Convert2DTo3D(self, detectedObjects: [DetectedObject], frameIndex: int, showConversions=False):
        """
        This function converts a screenspace (2D) position to a worldspace (3D) position.
        It uses the worldRepresentation to convert the given DetectedObject[] data to detectedObjectPosition[] data.
        This function is meant to be abstract and to recieve specific implementation depending on the conversion method


        Parameters
        ----------
        detectedObjects : [DetectedObject]
            The DetectedObject[] data to be converted.
        frameIndex : int
            The index belonging to the DetectedObject[] data.
        showConversions : bool
            Whether conversions are shown on the map

        Returns
        -------
        DetectedObjectPosition[]
            An array of named tuples containing X, Y and Z coordinates, ID
            and the type of detected and to 3D converted objects.
        """
        detectedObjectPositions = []

        for detectedObject in detectedObjects:
            x = (detectedObject.x - 540) / 40
            y = (250 - detectedObject.y) / 30
            objectID = detectedObject.id
            objectType = detectedObject.type
            detectedObjectPositions.append(DetectedObjectPosition(y, x, 0, objectID, objectType))

        return detectedObjectPositions

    def _CalculateStaticError(self):  # pragma: no cover
        """
        Calculates the static error for the given configuration based
        on all available static error datasets.
        """

        # Read all static error datasets
        folder = Pathing.AssureAbsolutePath("Testing/Assets/Datasets")
        staticErrorDatasets = []
        for file in os.listdir(folder):
            if file.endswith(".json"):
                staticErrorDatasets.append(StaticAccuracyDataset.Load(folder / file))

        # Save configuration for now
        savedConfiguration = self.configuration

        # Calculate the static error for all datasets
        for staticErrorDataset in staticErrorDatasets:
            # Get the configuration for the dataset, and
            # use it temporarily
            self.configuration = staticErrorDataset.GetCalibrationConfiguration(
                savedConfiguration.__class__.__name__
            )

            # Calculate the static error for the dataset
            for e in range(len(staticErrorDataset.entries)):
                entry = staticErrorDataset.entries[e]
                validationWorldPosition = self.Convert2DTo3D(
                    [DetectedObject(
                        float(entry['screenPosition'][0]),
                        float(entry['screenPosition'][1]),
                        -1, None
                    )],
                    -1
                )[0]
                validationLongitude = validationWorldPosition.longitude
                validationLatitude = validationWorldPosition.latitude

                # Calculate the error
                if self.staticError is None:
                    self.staticError = StaticAccuracyError()

                actualPos = IConvertor._WorldPosToGeoPos(entry['worldPosition'])
                validationPos = (validationLatitude, validationLongitude)
                newError = IConvertor.MetersBetweenGeoPositions(actualPos, validationPos)
                self.staticError.AddError(newError)

        self.staticError.AverageErrors()

        # Print the static error
        print("Method static max error:", self.staticError.GetMaxError())
        print("Method static average error:", self.staticError.averageError)

        # Restore the configuration
        self.configuration = savedConfiguration

    @staticmethod
    def _WorldPosToGeoPos(worldPos):  # pragma: no cover
        """

        Parameters
        ----------
        worldPos: [float]
            list in form [x, y, z] in meters

        Returns
        -------
        geoPos in form [float, float]
        """
        [x, y, z] = worldPos
        angle = IConvertor.GetAngleToNorthFromVector(x, z)
        meters = math.sqrt(x * x + z * z)
        [lat, lon] = IConvertor.MoveGeoByBearing(0, 0, np.rad2deg(angle), meters)
        return lat, lon

    def ConversionSinglePixelError(self, detectedObjects: [DetectedObject], frameIndex: int):
        """
        This function does the same as Convert2DTo3D but also checks how much the position would change for each point,
        if it was shifted by a single pixel
        (it picks the largest error per point of all four cardinal directions and passes that)

        Parameters
        ----------
        detectedObjects : [DetectedObject]
                A list items, each holding the information of a single point to be transformed from 2D to 3D

        frameIndex : int
                the index of the frame in the video on which this list of objects, and these positions, were detected

        Returns
        -------
        [DetectedObjectPosition]
                A list containing for each entry the result of that entry in Convert2DTo3D and its metadata (e.g. error)
        """
        detectedObjectPositionsWithError = []

        if detectedObjects == []:
            return []

        mainResults = self.Convert2DTo3D(detectedObjects, frameIndex, True)

        for i in range(len(mainResults)):
            mainResult = mainResults[i]
            mainPosition = (mainResult.latitude, mainResult.longitude)
            shiftedObjects = self.PrepareShiftedPositionList(detectedObjects[i])
            shiftedObjectResults = self.Convert2DTo3D(shiftedObjects, frameIndex)
            errorDistance = []
            for obj in shiftedObjectResults:
                errorDistance.append(self.MetersBetweenGeoPositions((obj.latitude, obj.longitude), mainPosition))

            objectLat = mainResult.latitude
            objectLon = mainResult.longitude
            objectAlt = mainResult.altitude
            objectID = mainResult.id
            objectType = mainResult.type
            objectEr = 0
            if self.staticError is not None:
                objectEr = max(errorDistance) + self.staticError.GetMaxError()
            objectRdX = mainResult.rijksdriehoekX
            objectRdY = mainResult.rijksdriehoekY
            final = DetectedObjectPosition(objectLat, objectLon, objectAlt, objectID,
                                           objectType, objectEr, objectRdX, objectRdY)
            detectedObjectPositionsWithError.append(final)

        return detectedObjectPositionsWithError

    @staticmethod
    def PrepareShiftedPositionList(object: DetectedObject):
        """
        Given a single DetectedObject it returns the list of all single pixel shifted (in cardinal directions) positions
        In other words, it takes the position of the detected object, and makes a list of x+1, X-1 etc. versions of that
        object and converts them using the 2DTo3D function. It discards the original point in this process,
        it is a helper function for ConversionSinglePixelError

        Parameters
        ----------
        object : DetectedObject
                The single detected object which is to be duplicated and shifted

        Returns
        -------
        [DetectedObject]
                Four copies of the input, each shifted one pixel in a different direction.
        """
        singlePixelShiftList = []
        objectID = object.id
        objectType = object.type
        objectXPosition = object.x
        objectYPosition = object.y
        singlePixelShiftList.append(DetectedObject(objectXPosition + 5, objectYPosition, objectID, objectType))
        singlePixelShiftList.append(DetectedObject(objectXPosition - 5, objectYPosition, objectID, objectType))
        singlePixelShiftList.append(DetectedObject(objectXPosition, objectYPosition + 5, objectID, objectType))
        singlePixelShiftList.append(DetectedObject(objectXPosition, objectYPosition - 5, objectID, objectType))
        return singlePixelShiftList

    @staticmethod
    def MetersBetweenGeoPositions(position1: (float, float), position2: (float, float)):
        """"
        This is a very simple function that returns the distance between to coordinates in meters

        Parameters
        ----------
        position1: (float, float)
                The position of the first point in (latitude, longitude) format

        position2: (float, float)
                The second position, to wich the distance is calulated from the first point

        Returns
        -------
        distance: float
                The distance between the points in meters
        """
        if len(position1) != len(position2):
            raise RuntimeError("Points don't have the same amount of dimensions")
        elif len(position1) != 2:
            raise RuntimeError("Coordinates do not contain the expected two dimensions, it has " + str(len(position1)))
        elif (position1[0] < -90) or (position1[0] > 90) or (position2[0] < -90) or (position2[0] > 90):
            lat1 = str(position1[0])
            lat2 = str(position2[0])
            raise RuntimeError("latitude must be in [-90, 90] range, instead they are 1: " + lat1 + " and 2: " + lat2)
        return geopy.distance.distance(position1, position2).meters

    @staticmethod
    def MoveGeoByBearing(startLatDegrees, startLonDegrees, angleToNorth, metersToMove, earthRadius=6378.1):
        """
        This function lets you calculate the new position given how many meters you move from a certain position.

        Parameters
        ----------
        startLatDegrees : double
            a known latitude
        startLonDegrees : double
            a known longitude
        angleToNorth : double
            angle to go in (since pixels either 0 or 90 degrees)
        metersToMove : double
            use the scale to get convert the scale to degrees per pixel
        earthRadius : double
            the radius of the earth

        Returns
        -------
        the new gps position, given the input

        """
        startLat = math.radians(startLatDegrees)
        startLon = math.radians(startLonDegrees)
        distance = metersToMove / 1000
        bearing = math.radians(angleToNorth)
        lengthRatio = distance / earthRadius
        newLat = math.asin(
            math.sin(startLat) * math.cos(lengthRatio) + math.cos(startLat) * math.sin(lengthRatio) * math.cos(bearing))
        newLon = startLon + math.atan2(math.sin(bearing) * math.sin(lengthRatio) * math.cos(startLat),
                                       math.cos(lengthRatio) - math.sin(startLat) * math.sin(newLat))
        return [math.degrees(newLat), math.degrees(newLon)]

    @staticmethod
    def GetAngleToNorthFromVector(deltaLon, deltaLat):
        """
        This function converts a vector to an angle compared to north in radians

        Parameters
        ----------
        deltaLon: int
            difference in longitude
        deltaLat: int
            difference in latitude

        Returns
        -------
        Angle to north in radians
        """

        if deltaLon == 0 and deltaLat == 0:
            return 0

        # Calculate vector from anchorPixelPos to new pixelPos
        vector = np.array([deltaLon, deltaLat])
        # Divide by length to get unit vector (vector of length 1)
        unitVector = vector / np.linalg.norm(vector)
        north = np.array([0, 1])
        # cos(theta) = vector1 * vector2. where theta is the angle between vectors
        dotProduct = np.dot(unitVector, north)
        # calculate angle to north
        angle = np.arccos(dotProduct)

        if deltaLon < 0:
            angle = 2 * math.pi - angle

        return angle

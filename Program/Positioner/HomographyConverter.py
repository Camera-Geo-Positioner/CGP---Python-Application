# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software Project course.
# © Copyright Utrecht University (Department of Information and Computing Sciences)

"""
Implementation of the IConverter.
Uses the HomographyCalibrationConfiguration to convert the 2D positions to 3D positions.
"""

import math
import numpy as np
from rijksdriehoek import rijksdriehoek

from Positioner.IConvertor import *
from FrameAnalyzer.IDetector import DetectedObject
from Calibrator.Configurations.HomographyCalibrationConfiguration import GeoPosition, HomographyCalibrationConfiguration
from Windowing.Sub.CameraSubWindow import *
import cv2


# uses linear algebra to convert pixel coordinates and a 3x3 matrix to get top down pixel coordinates
class HomographyConverter(IConvertor):
    configuration: HomographyCalibrationConfiguration = None
    cameraWindow: CameraSubWindow = None

    def __init__(self, homographyCalibrationConfiguration: HomographyCalibrationConfiguration,
                 cameraWindow: CameraSubWindow):
        """ Constructor for the HomographyConverter class.

        Parameters
        ----------
        homographyCalibrationConfiguration : HomographyCalibrationConfiguration
            The configuration for the homography converter.
        """
        self.cameraWindow = cameraWindow

        if homographyCalibrationConfiguration is None:
            raise TypeError("No Convertor given in HomographyConvertor.")

        super().__init__(homographyCalibrationConfiguration)

        # show first image
        if self.configuration.smartImage is not None:
            self._ShowConversions([], self.configuration.smartImage.GetImage())

    def Convert2DTo3D(self, detectedObjects: [DetectedObject], frameIndex: int, showConversions=False) \
            -> [DetectedObjectPosition]:
        """
        Takes objects with 2d pixel positions in the camera view and
        transforms those into geo positions (lon, lat).

        It does this with a transformation matrix and some info about the environment of
        the topdown view picture (see HomographyCalibrationConfiguration).

        Parameters
        ----------
        detectedObjects : [DetectedObject]
            objects that have been detected by the camera
        frameIndex : int
            what frame they were detected in
        showConversions : bool
            Whether conversions are shown on the map

        Returns
        -------
        [DetectedObjectPosition]
            A list of DetectedObjectPositions, which contain the geo coordinates of the detected object
        """

        detectedObjectGeoPositions = []
        detectedObjectPixelPositions = []
        M = self.configuration.homographyMatrix
        smartImage = self.configuration.smartImage

        for detectedObject in detectedObjects:
            x = detectedObject.x
            y = detectedObject.y
            objectID = detectedObject.id
            objectType = detectedObject.type

            # transform point to topdown pixel coordinates
            homo_pos = np.dot(M, np.array([[x], [y], [1]]))
            homo_pos = homo_pos.flatten()
            [[[x2, y2]]] = cv2.convertPointsFromHomogeneous(np.array([homo_pos]))

            # convert to geo-position
            geoPos = self._Convert2DTopDownToGeo(round(x2), round(y2))

            # convert to Rd position
            (rdX, rdY) = self._Convert2DTopDownToRd(round(x2), round(y2))

            detectedObjectGeoPositions.append(
                DetectedObjectPosition(
                    geoPos.latitude, geoPos.longitude, geoPos.altitude,
                    objectID, objectType,
                    0,
                    rdX, rdY
                )
            )
            detectedObjectPixelPositions.append(
                DetectedObjectPosition(
                    int(y2), int(x2), 0,
                    objectID, objectType
                )
            )

        if smartImage is not None and showConversions:
            self._ShowConversions(detectedObjectPixelPositions, smartImage.GetImage())

        return detectedObjectGeoPositions

    def _Convert2DTopDownToRd(self, x, y) -> (float, float):
        """
        This function converts the top-down view pixel position to rijksdriehoek coordinates. It uses the
        anchor rijksdriehoek position from the configuration. If that's 0, it calculates it from the gps -> rd.

        Parameters
        ----------
        x : int
            x position in the top-down view
        y : int
            y position in the top-down view

        Returns
        -------
        (float, float)
            The Rd coordinate
        """
        # if no Rd coord is set, we convert it from gps (wgs84)
        if self.configuration.homographyGeoData.anchorRdPosition is None:
            rd = rijksdriehoek.Rijksdriehoek()
            rd.from_wgs(self.configuration.homographyGeoData.anchorGeoPosition.latitude,
                        self.configuration.homographyGeoData.anchorGeoPosition.longitude)
            self.configuration.homographyGeoData.anchorRdPosition = (rd.rd_x, rd.rd_y)

        # for better readability
        (anchorX, anchorY) = self.configuration.homographyGeoData.anchorRdPosition
        scale = self.configuration.homographyGeoData.pixelScale

        return anchorX + (x * scale), anchorY - (y * scale)

    def _Convert2DTopDownToGeo(self, x, y):
        """
        takes 2 pixel coordinates in the image and turns them into longitude and latitude based on the metadata
        saved in this object.

        Parameters
        ----------
        x : int
            an x coordinate on the image saved in this object
        y : int
            a respective y coordinate

        Returns
        -------
        GpsPosition
            the actual lon and lat coordinates that the pixel coordinates represent
        """

        # calculate the difference in pixel coordinates
        deltaX = x - self.configuration.homographyGeoData.anchorPixelPosition[0]
        deltaY = self.configuration.homographyGeoData.anchorPixelPosition[1] - y

        angle = self.GetAngleToNorthFromVector(deltaX, deltaY)

        meters = self._VectorToMeters(deltaX, deltaY)

        [newLat, newLon] = IConvertor.MoveGeoByBearing(
            self.configuration.homographyGeoData.anchorGeoPosition.latitude,
            self.configuration.homographyGeoData.anchorGeoPosition.longitude,
            np.rad2deg(angle),
            meters
        )

        return GeoPosition(
            longitude=newLon,
            latitude=newLat,
            altitude=self.configuration.homographyGeoData.anchorGeoPosition.altitude
        )

    def _VectorToMeters(self, deltaX, deltaY):
        """
        this function returns the length in meters of a vector in the image,
        using the pythagorean formula.
        Parameters
        ----------
        deltaX : int
            difference in x coordinates in the image
        deltaY : int
            difference in y coordinates in the image
        Returns
        -------
        the length in
        """
        return \
            np.sqrt(deltaX * deltaX + deltaY * deltaY) * \
            self.configuration.homographyGeoData.pixelScale

    def _ShowConversions(self, detectedObjectPixelPositions, image):  # pragma: no cover
        """
        A quick function for demoing to show the converted pixel point in the topdown view
        Parameters
        ----------
        detectedObjectPixelPositions : a list of pixel coordinates (of the topdown image) representing detected objects
        image: the topdown image

        """
        if self.cameraWindow is None:
            return

        copyImage = image.copy()

        # draw circles for each object
        for detectedObject in detectedObjectPixelPositions:
            cv2.circle(copyImage, (detectedObject.longitude, detectedObject.latitude), 5, (50, 50, 255), -1)
        self.cameraWindow.ShowFrame(copyImage)

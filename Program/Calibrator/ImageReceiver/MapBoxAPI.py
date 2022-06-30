# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software Project course.
# © Copyright Utrecht University (Department of Information and Computing Sciences)

"""
Implementation of the IImageReceiver.
Uses the MapBoxAPI together with the camera gps coordinates to get an image.
"""

from Calibrator.Configurations.HomographyCalibrationConfiguration import HomographyGeoData, GeoPosition
from Calibrator.ImageReceiver.IImageReceiver import IImageReceiver
from Calibrator.ImageReceiver.SmartImage import SmartImage
from Windowing.Sub.GpsInputSubWindow import GpsInputSubWindow
from Windowing.MasterWindow import MasterWindow, SubWindowPosition
from IO import Pathing

import time
from typing import Tuple
from mapbox import Static, Geocoder
import numpy as np
import cv2


MAP_BOX_ACCESS_TOKEN = "pk.eyJ1IjoiMmQzZHByb2plY3QiLCJhIjoiY2wyN2U3a29iMDBuZTNpbGQ5cXc0bGgyaSJ9.GGX0T0gtL6I4SYG-9TOVPQ"
EARTH_CIRCUMFERENCE = 40075.016686


class MapBoxAPI(IImageReceiver):
    def CreateGeoSmartImage(self, zoomLevel=19) -> Tuple[SmartImage, HomographyGeoData]:
        """
        This functions calls the map api to retrieve image and metadata from the surrounding area and
        returns a SmartImage object

        Returns
        -------
        Tuple[SmartImage, HomographyGeoData]
            The smart image and the homography geo data.
        """

        # Request input
        gpsInput = GpsInputSubWindow("Please enter WGS84 coordinates. \ne.g. (52.090695, 5.121314).",
                                     "Enter GPS coordinates for MapBox")
        MasterWindow.instance.AppendSubWindow(gpsInput, SubWindowPosition.Left)
        while not gpsInput.InputBeenGiven() and MasterWindow.instance.running:
            time.sleep(0.01)

        # Handle force close
        if not gpsInput.InputBeenGiven():
            return None

        # Extract data
        gps = gpsInput.GetGivenPosition()
        lon = gps.longitude
        lat = gps.latitude

        # Remove sub window and create smart image
        MasterWindow.instance.RemoveSubWindow(SubWindowPosition.Left)
        return MapBoxAPI.SmartImageFromLongLat(lon, lat, zoomLevel)

    @staticmethod
    def SmartImageFromLongLat(lon, lat, zoomLevel=19):
        """
        Helper function to actually perform API call and create smart image object, separated to ease testing

        Parameters
        ----------
        lon : double
            longitude value
        lat : double
            latitude value
        zoomLevel : int
            how far we want the returned image to be zoomed-in, default is 19

        Returns
        -------
        Tuple[SmartImage, HomographyGeoData]
            The smart image and the homography geo data.
        """
        imageSize = 1279  # the same width and height
        image = MapBoxAPI._MapBoxApiCall(lon, lat, zoomLevel, imageSize)

        if image is None:
            return None, None

        # scale in meters per pixel (from mapbox documentation)
        baseScale = EARTH_CIRCUMFERENCE * 1000 / imageSize
        scale = baseScale * np.cos(np.deg2rad(lat)) / (2 ** zoomLevel)

        return (
            SmartImage(image),
            HomographyGeoData(
                (639, 639),
                GeoPosition(longitude=lon, latitude=lat, altitude=0),
                scale
            )
        )

    @staticmethod
    def _MapBoxApiCall(lon=5.1659, lat=52.0881, zoomLevel=19, imageWidth=1279):
        """

        Parameters
        ----------
        lon : double
            longitude value
        lat : double
            latitude value
        zoomLevel : int
            how far we want the returned image to be zoomed-in
        imageWidth : int
            the width and height of the image (always square for simplicity, but is not necessary)

        Returns
        -------
        The received image from the mapbox api

        """
        service = Static(MAP_BOX_ACCESS_TOKEN)

        try:
            response = service.image(
                'mapbox.satellite',
                lon=lon, lat=lat, z=zoomLevel,
                width=imageWidth, height=imageWidth,
                image_format="jpg"
            )

            if response.status_code != 200:
                raise AssertionError("API call did not go through. Status code: " + response.status_code)
        except Exception as e:
            return None

        image = cv2.imdecode(np.frombuffer(response.content, np.uint8), cv2.IMREAD_COLOR)

        return image

# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software Project course.
# © Copyright Utrecht University (Department of Information and Computing Sciences)

"""
An implementation of the ICalibrationConfiguration, used by the homography converter.
"""

from collections import namedtuple
import numpy as np
from Calibrator.Configurations.ICalibrationConfiguration import ICalibrationConfiguration
from Calibrator.ImageReceiver.SmartImage import SmartImage


class GeoPosition:
    latitude = 0
    longitude = 0
    altitude = 0

    def __init__(self, latitude, longitude, altitude):
        self.latitude = latitude
        self.longitude = longitude
        self.altitude = altitude


class HomographyGeoData:
    """
    This class is used to store the geo data of a homography calibration.
    """
    anchorPixelPosition: (int, int)
    anchorGeoPosition: GeoPosition
    anchorRdPosition: (float, float) or None
    pixelScale: float

    def __init__(self, anchorPixelPosition, anchorGeoPosition, pixelScale, anchorRdPosition=None):
        """
        Initializes the class with the given parameters.

        Parameters
        ----------
        anchorPixelPosition : tuple
            The pixel position of the anchor point.
        anchorGeoPosition : GeoPosition
            The geo position of the anchor point.
        anchorRdPosition : (float, float)
            The position of the anchorpoint in 'Rijksdriehoek' coordinates
        pixelScale : float
            The pixel scale of the image.
        """
        self.anchorPixelPosition = anchorPixelPosition
        self.anchorGeoPosition = anchorGeoPosition
        self.anchorRdPosition = anchorRdPosition
        self.pixelScale = pixelScale


class HomographyCalibrationConfiguration(ICalibrationConfiguration):
    """
    This class is used to store the configuration for a homography calibration.
    """
    homographyMatrix: np.ndarray = None
    homographyGeoData: HomographyGeoData = None
    smartImage: SmartImage = None
    cameraResolution: (int, int) = None

    def __init__(self, homographyMatrix=None, cameraResolution=None, homographyGeoData=None, smartImage=None):
        """ Initialize the homography calibration configuration

        Parameters
        ----------
        homographyMatrix : np.ndarray
            The homography matrix of the calibration
        homographyGeoData : HomographyGeoData
            The homography geo data of the calibration
        smartImage : SmartImage
            The smart image of the calibration
        """

        self.homographyMatrix = homographyMatrix
        self.homographyGeoData = homographyGeoData
        self.smartImage = smartImage
        self.cameraResolution = cameraResolution

    def Save(self, cameraId: str):
        """ Save the homography calibration configuration

        Parameters
        ----------
        cameraId : str
            The camera id of the camera that is being calibrated
        """

        # Convert numpy array to list, as json can't handle numpy arrays
        self.homographyMatrix = self.homographyMatrix.tolist()

        # Save smart image and set to none
        self.smartImage.Save(cameraId)
        self.smartImage = None

        # Call super
        super(HomographyCalibrationConfiguration, self).Save(cameraId)

        # Convert list back to numpy array
        self.homographyMatrix = np.array(self.homographyMatrix)

        # Restore smart image
        self.smartImage = SmartImage.FromIdentifier(cameraId)

    def Load(self, cameraId, arguments=None):
        """ Load the homography calibration configuration

        Parameters
        ----------
        cameraId : string
            The camera id of the camera that is being calibrated
        arguments : Dict
            dictionary of program arguments
        """

        # Call super
        super(HomographyCalibrationConfiguration, self).Load(cameraId)

        # Convert list to numpy array
        self.homographyMatrix = np.array(self.homographyMatrix)

        if arguments is not None:
            scaling = np.zeros((3, 3))
            scaling[0][0] = self.cameraResolution[0] / arguments["analyzeWidth"]
            scaling[1][1] = self.cameraResolution[1] / arguments["analyzeHeight"]
            scaling[2][2] = 1
            self.homographyMatrix = np.matmul(self.homographyMatrix, scaling)

        # Convert nested homography geo data dictionary
        # back to class object instance
        self.homographyGeoData = HomographyGeoData(
            self.homographyGeoData["anchorPixelPosition"],
            GeoPosition(
                self.homographyGeoData["anchorGeoPosition"]["latitude"],
                self.homographyGeoData["anchorGeoPosition"]["longitude"],
                self.homographyGeoData["anchorGeoPosition"]["altitude"]
            ),
            self.homographyGeoData["pixelScale"],
            self.homographyGeoData["anchorRdPosition"]
        )

        # Restore smart image
        self.smartImage = SmartImage.FromIdentifier(cameraId)

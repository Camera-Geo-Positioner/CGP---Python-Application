# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software Project course.
# © Copyright Utrecht University (Department of Information and Computing Sciences)

import numpy as np
from unittest.mock import Mock
from Calibrator.ImageReceiver.SmartImage import SmartImage
from Calibrator.Configurations.HomographyCalibrationConfiguration import HomographyCalibrationConfiguration, \
    GeoPosition, HomographyGeoData


class TestHomographyCalibrationConfiguration:

    def test_Save(self):
        matrix = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        smartImage = SmartImage(matrix)
        homographyGeoData = HomographyGeoData(
            (100, 100), GeoPosition(longitude=5, latitude=50, altitude=0), 0.1
        )
        homographyCalibrationConfiguration = \
            HomographyCalibrationConfiguration(matrix, (3, 3), homographyGeoData, smartImage)
        homographyCalibrationConfiguration.ToJSON = Mock()
        smartImage.Save = Mock()
        SmartImage.FromIdentifier = Mock(return_value=smartImage)
        homographyCalibrationConfiguration.Save(1)

        assert \
            homographyCalibrationConfiguration.homographyMatrix.all() == matrix.all() and \
            np.array_equal(homographyCalibrationConfiguration.smartImage.image, matrix) and \
            homographyCalibrationConfiguration.homographyGeoData.anchorPixelPosition is \
            homographyGeoData.anchorPixelPosition and \
            homographyCalibrationConfiguration.homographyGeoData.anchorGeoPosition is \
            homographyGeoData.anchorGeoPosition and \
            homographyCalibrationConfiguration.homographyGeoData.pixelScale is homographyGeoData.pixelScale, \
            "Homography matrix has been modified!"

    def test_Load(self):
        matrix = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        smartImage = SmartImage(matrix)
        homographyGeoData = HomographyGeoData(
            (100, 100), GeoPosition(longitude=5, latitude=50, altitude=0), 1
        )
        homographyCalibrationConfiguration = HomographyCalibrationConfiguration(None, None, None)

        def setData(_):
            homographyCalibrationConfiguration.homographyMatrix = matrix
            homographyCalibrationConfiguration.smartImage = None
            homographyCalibrationConfiguration.homographyGeoData = {
                "anchorPixelPosition": (100, 100),
                "anchorGeoPosition": {
                    "longitude": 5,
                    "latitude": 50,
                    "altitude": 0
                },
                "anchorRdPosition": (100, 400),
                "pixelScale": 1
            }
            homographyCalibrationConfiguration.cameraResolution = (3, 3)

        arguments = {
            'analyzeWidth': 960,
            'analyzeHeight': 540,
        }

        homographyCalibrationConfiguration = HomographyCalibrationConfiguration(None, None)
        homographyCalibrationConfiguration.FromJSON = Mock(side_effect=setData)
        SmartImage.FromIdentifier = Mock(return_value=smartImage)
        homographyCalibrationConfiguration.Load(1, arguments)

        assert \
            homographyCalibrationConfiguration.homographyMatrix is not None and \
            homographyCalibrationConfiguration.smartImage is not None and \
            homographyCalibrationConfiguration.homographyGeoData is not None, \
            "Homography configuration data entry should not be None"
        assert \
            homographyCalibrationConfiguration.homographyMatrix.all() == matrix.all() and \
            np.array_equal(homographyCalibrationConfiguration.smartImage.image, matrix) and \
            homographyCalibrationConfiguration.homographyGeoData.anchorPixelPosition == \
            homographyGeoData.anchorPixelPosition and \
            homographyCalibrationConfiguration.homographyGeoData.anchorGeoPosition.latitude == \
            homographyGeoData.anchorGeoPosition.latitude and \
            homographyCalibrationConfiguration.homographyGeoData.anchorGeoPosition.longitude == \
            homographyGeoData.anchorGeoPosition.longitude and \
            homographyCalibrationConfiguration.homographyGeoData.anchorGeoPosition.altitude == \
            homographyGeoData.anchorGeoPosition.altitude and \
            homographyCalibrationConfiguration.homographyGeoData.pixelScale == homographyGeoData.pixelScale, \
            "Homography configuration has been modified wrongly!"

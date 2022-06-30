# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software Project course.
# © Copyright Utrecht University (Department of Information and Computing Sciences)

import pytest
from unittest.mock import Mock, patch, MagicMock
from Positioner.HomographyConverter import *
from Calibrator.Configurations.HomographyCalibrationConfiguration import HomographyCalibrationConfiguration, \
    HomographyGeoData
from IO import Pathing

detections = [DetectedObject(1, 1, 0, 0), DetectedObject(5, 5, 1, 0)]


@patch('Calibrator.ImageReceiver.SmartImage.SmartImage.FromIdentifier', Mock(return_value=Mock()))
def test_Normal():
    configuration = HomographyCalibrationConfiguration(None, None)
    configuration._GetJSONPath = Mock()
    configuration._GetJSONPath.return_value = \
        Pathing.AssureAbsolutePath('Testing/Assets/homographyTestConfiguration.json')

    def setData(_):
        configuration.homographyMatrix = [[0.5, 0.0, 0],
                                          [0.0, 0.5, 0],
                                          [0.0, 0.0, 1.0]]
        configuration.homographyGeoData = \
            {
                "anchorGeoPosition":
                    {
                        "latitude": 52.08850112867399,
                        "longitude": 5.165728014316017,
                        "altitude": 0
                    },
                "anchorPixelPosition": [725, 155],
                "anchorRdPosition": (100, 400),
                "pixelScale": 0
            }
        configuration.smartImage = MagicMock()

    configuration.FromJSON = Mock(side_effect=setData)

    configuration.Load(0, None)
    convertor = HomographyConverter(configuration, MagicMock())
    HomographyConverter._ShowConversions = Mock()

    detectedObjectGeoPositions = convertor.Convert2DTo3D(detections, 1)

    assert len(detectedObjectGeoPositions) == 2
    for i in range(len(detectedObjectGeoPositions)):
        assert detectedObjectGeoPositions[i].altitude == 0
        assert detectedObjectGeoPositions[i].type == 0
        assert detectedObjectGeoPositions[i].id == detections[i].id
        assert detectedObjectGeoPositions[i].rijksdriehoekX is not None
        assert detectedObjectGeoPositions[i].rijksdriehoekY is not None


def test_NoConverter():
    pytest.raises(TypeError, HomographyConverter, None)


def test_MoveGeoByBearing():
    movedLat1 = HomographyConverter.MoveGeoByBearing(50, 5, 0, 10)[0]
    movedLon1 = HomographyConverter.MoveGeoByBearing(50, 5, 90, 10)[1]

    movedLat2 = HomographyConverter.MoveGeoByBearing(50, 5, 0, 20)[0]
    movedLon2 = HomographyConverter.MoveGeoByBearing(50, 5, 90, 20)[1]

    movedLon3 = HomographyConverter.MoveGeoByBearing(80, 5, 90, 20)[1]

    assert movedLon1 < movedLon2 < movedLon3 and movedLat1 < movedLat2


def test_GeoConversionDistance():
    anchorGps = GeoPosition(5, 50, 0)
    anchorPixel = (500, 500)
    pixelScale = 0.1

    IConvertor._CalculateStaticError = Mock()
    convertor = HomographyConverter(
        HomographyCalibrationConfiguration(
            None,
            None,
            HomographyGeoData(
                anchorPixel, anchorGps, pixelScale
            ),
            None
        ),
        None
    )

    newX = 75
    newY = 150
    deltaX = newX - anchorPixel[0]
    deltaY = anchorPixel[1] - newY
    meters = convertor._VectorToMeters(deltaX, deltaY)
    assert np.abs(meters - 55) < pixelScale


def test_GeoConversionGPS():
    anchorGps = GeoPosition(49.999685586310726, 5, 0)
    anchorPixel = (500, 500)
    pixelScale = 0.1

    IConvertor._CalculateStaticError = Mock()
    convertor = HomographyConverter(
        HomographyCalibrationConfiguration(
            None,
            None,
            HomographyGeoData(
                anchorPixel, anchorGps, pixelScale
            ),
            None
        ),
        None
    )
    newX = 75
    newY = 150
    gps = convertor._Convert2DTopDownToGeo(newX, newY)
    expectedGPS = GeoPosition(50, 4.999406049979839, 0)
    assert np.abs(gps.longitude - expectedGPS.longitude) < 0.000001  # difference of 0.7 cm with accurate calcs
    assert np.abs(gps.latitude - expectedGPS.latitude) < 0.000001  # difference of 0.7 cm with accurate calcs

from Positioner.IConvertor import IConvertor, DetectedObject
from Positioner.Accuracy.StaticAccuracyDataset import StaticAccuracyError
import pytest
from unittest.mock import patch, MagicMock
import numpy as np

inputData = [(1, 1, 0, 0, 0), (21, 21, 99999, 2, -2), (0, 0, 0, 0, 0), (-89.9999, -89.9999, -9999999, -999999, -9999)]


@pytest.mark.parametrize("x, y, id, type, frame", inputData)
def test_similarity(x, y, id, type, frame):
    mockObject = IConvertor("this information is not used")
    mockObject.staticError = MagicMock()
    mockObject.staticError.GetMaxError = MagicMock(return_value=0)
    shouldBe = mockObject.Convert2DTo3D([DetectedObject(x, y, id, type)], frame)
    result = mockObject.ConversionSinglePixelError([DetectedObject(x, y, id, type)], frame)
    print(result)
    assert shouldBe[0].longitude == result[0].longitude


amountsToTest = [(10), (999), (0)]


@pytest.mark.parametrize("amount", amountsToTest)
def test_conservation(amount):
    detectedObjects = []
    mockObject = IConvertor("this information is not used")
    mockObject.staticError = MagicMock()
    mockObject.staticError.GetMaxError = MagicMock(return_value=0)
    for i in range(amount):
        detectedObjects.append(DetectedObject(2 * i % 90, -(1 * i % 90), i, 0))
    assert len(mockObject.ConversionSinglePixelError(detectedObjects, 0)) == amount


@pytest.mark.parametrize("metersToMove", [3, 10, 50, 0.3])
def test_conservation(metersToMove):
    [lat, lon] = IConvertor.MoveGeoByBearing(50, 5, 45, metersToMove)
    metersMoved = IConvertor.MetersBetweenGeoPositions((lat, lon), (50, 5))
    assert np.abs(metersToMove - metersMoved) < 0.03, 'difference was more than 3 cm'

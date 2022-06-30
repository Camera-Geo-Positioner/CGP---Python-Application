import pytest
from Calibrator.ImageReceiver.IImageReceiver import IImageReceiver


@pytest.mark.xfail(raises=NotImplementedError)
def test_create_smart_image():
    imageReceiver = IImageReceiver()
    imageReceiver.CreateGeoSmartImage()
    assert False

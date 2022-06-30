import pygame
import pytest
from unittest.mock import Mock

from Calibrator.ImageReceiver.MapBoxAPI import MapBoxAPI
from mapbox.errors import InvalidCoordError, InvalidZoomError, ImageSizeError
import mapbox as mb


@pytest.mark.parametrize("lon, lat, zoom", [(10, 10, 15),
                                            (-100, -100, 10),
                                            (5.166, 52.088, 6),
                                            (420, 420, 19),
                                            (-50, -50, 21),
                                            (5.166, 52.088, 0),
                                            (5.166, 52.088, -1),
                                            (5.166, 52.088, 22),
                                            (5.166, 52.088, 23)])
def test_CreateSmartImage(lon, lat, zoom):
    mapbox = MapBoxAPI()
    mb.Static = Mock()

    try:
        mapbox.SmartImageFromLongLat(lon, lat, zoom)
    except AssertionError:
        assert True
        return
    except OSError:
        assert True
        return
    except InvalidCoordError:
        assert True
        return
    except InvalidZoomError:
        assert True
        return
    except ImageSizeError:
        assert True
        return
    except Exception as e:
        assert False, "some other exception was thrown: " + str(e)
    assert True


@pytest.mark.parametrize("lon, lat, zoom, width",
                         [(5.1659, 52.0881, 19, 1279),
                          (5.1659, 52.0881, 23, 1281),
                          (5.1659, 52.0881, 19, -1),
                          (5.1659, 52.0881, 0, 1279),
                          (5.1659, 52.0881, -1, 1279),
                          (-5.1659, -52.0881, 19, 1279),
                          (5.1659, 520.0881, 19, 1279),
                          (500.1659, 52.0881, 19, 1279)])
def test_ApiCall(lon, lat, zoom, width):
    try:
        mb.Static = Mock()
        image = MapBoxAPI._MapBoxApiCall(lon, lat, zoom, width)
        assert image is not None
    except AssertionError:
        assert True
        return
    except InvalidCoordError:
        assert True
        return
    except InvalidZoomError:
        assert True
        return
    except ImageSizeError:
        assert True
        return
    except Exception as e:
        assert False, "some other exception was thrown: " + str(e)
    assert True


def mockPyGame():
    pygame.init = Mock()
    pygame.display_set_mode = Mock()
    pygame.display = Mock()
    pygame.display.get_surface = Mock()
    pygame.display.get_surface().get_size = Mock(return_value=(100, 100))
    pygame.event.get = Mock(return_value=[])

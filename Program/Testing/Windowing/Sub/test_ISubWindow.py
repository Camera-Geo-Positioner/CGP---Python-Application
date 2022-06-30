# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software Project course.
# © Copyright Utrecht University (Department of Information and Computing Sciences)

from types import SimpleNamespace
from unittest.mock import Mock
from pygame import MOUSEBUTTONDOWN
import pytest
from Windowing.Sub.ISubWindow import *
from Windowing.Sub.CameraSubWindow import *


def mockPyGame():
    pygame.init = Mock()
    pygame.display_set_mode = Mock()
    pygame.display = Mock()
    pygame.display.get_surface = Mock()
    pygame.display.get_surface().get_size = Mock(return_value=(100, 100))


@pytest.mark.parametrize("test_input", [1, 987543, -20, 'cat'])
def test_keyCallBack(test_input):
    # Create a Mock, then call the function that should be tested.
    x = Mock()
    ISubWindow.SetKeyCallback(x, test_input)

    assert x.keyCallback == test_input


@pytest.mark.parametrize("test_input", [1, 987543, -20, 'cat'])
def test_mouseCallBack(test_input):
    # Create a Mock, then call the function that should be tested.
    x = Mock()
    ISubWindow.SetMouseCallback(x, test_input)

    assert x.mouseCallback == test_input


def test_HandleInput():
    keyEventDownMock = Mock()
    keyEventDownMock.type = Mock(KEYDOWN)
    keyEventUpMock = Mock()
    keyEventUpMock.type = Mock(KEYUP)

    mouseEventDownMock = Mock()
    mouseEventDownMock.type = Mock(pygame.MOUSEBUTTONDOWN)
    mouseEventDownMock.pos = Mock(return_value=(10, 10))
    mouseEventUpMock = Mock()
    mouseEventUpMock.type = Mock(pygame.MOUSEBUTTONUP)
    mouseEventUpMock.pos = Mock(return_value=(10, 10))
    mouseEventMoveMock = Mock()
    mouseEventMoveMock.type = Mock(pygame.MOUSEMOTION)
    mouseEventMoveMock.pos = Mock(return_value=(10, 10))

    x = Mock()
    ISubWindow.SetKeyCallback(x, 1)
    ISubWindow.SetMouseCallback(x, 1)

    ISubWindow.HandleInput(x, [])
    ISubWindow.HandleInput(x, [keyEventDownMock, keyEventUpMock])
    ISubWindow.HandleInput(x, [mouseEventUpMock, mouseEventDownMock, mouseEventMoveMock])

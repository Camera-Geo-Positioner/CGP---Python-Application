# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software Project course.
# © Copyright Utrecht University (Department of Information and Computing Sciences)

from types import SimpleNamespace
from unittest.mock import Mock
from Windowing.Sub.GpsInputSubWindow import GpsInputSubWindow
import pygame
from Windowing.MasterWindow import MasterWindow
import Windowing.MasterWindow

result = False
newPosition = (0, 0)


def test_ResizeGUIManager():
    def setResult(_):
        global result
        result = True

    assert result is False

    x = Mock()
    x.previousWidth = 0
    x.previousHeight = 0
    x.guiManager = Mock()
    x.guiManager.set_window_resolution = Mock(side_effect=setResult)
    GpsInputSubWindow._ResizeGUIManager(x)

    assert result is True


def test_CenterPanel():
    def setResult(pos):
        global newPosition
        newPosition = pos

    x = Mock()
    x.guiManager = Mock()
    x.guiManager.window_resolution = [100, 100]
    x.panel = Mock()
    x.panel.get_abs_rect = Mock(return_value=SimpleNamespace(**{'width': 50, 'height': 50}))
    x.panel.set_position = Mock(side_effect=setResult)

    assert newPosition == (0, 0)

    GpsInputSubWindow._CenterPanel(x)

    assert newPosition == (25, 25)

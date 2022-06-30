# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software Project course.
# © Copyright Utrecht University (Department of Information and Computing Sciences)

from unittest.mock import Mock
import pygame

from IO import Pathing
import time
from Windowing.MasterWindow import *
import cv2


def mockPyGame():
    pygame.init = Mock()
    pygame.display_set_mode = Mock()
    pygame.display = Mock()
    pygame.display.get_init = Mock(return_value=False)
    pygame.display.get_surface = Mock()
    pygame.display.get_surface().get_size = Mock(return_value=(100, 100))
    pygame.event.get = Mock(return_value=[])


def CreateSubWindowMock():
    subWindow = Mock()
    subWindow.HandleInput = Mock()
    subWindow.invalidated = Mock(return_value=True)
    return subWindow


def test_UpdateAndRender():
    mockPyGame()

    MasterWindow.instance = None
    window = MasterWindow(800, 800, "frame")
    window.Render = Mock()

    window.Update(0)
    window.invalidated = True
    window.Update(0)
    assert window.invalidated is False, "Invalidated is not set to false after update"


def test_Startup():
    mockPyGame()

    MasterWindow.instance = None
    window = MasterWindow(800, 800, "frame")
    window.Render = Mock()

    window.leftSubWindow = CreateSubWindowMock()
    window.Open(True)

    assert window.running is 1
    assert window.runningThread is not None

    window.Close()


def test_SubWindows():
    mockPyGame()

    MasterWindow.instance = None
    window = MasterWindow(800, 800, "frame")
    window.Render = Mock()

    window.Update(0)

    window.AppendSubWindow(CreateSubWindowMock(), SubWindowPosition.Left)
    assert window.leftSubWindow is not None

    window.Update(0)

    window.AppendSubWindow(CreateSubWindowMock(), SubWindowPosition.Right)
    assert window.rightSubWindow is not None

    window.Update(0)

    window.RemoveSubWindow(SubWindowPosition.Left)
    assert window.leftSubWindow is None

    window.RemoveSubWindow(SubWindowPosition.Right)
    assert window.rightSubWindow is None


def test_SeperatorOffset():
    mockPyGame()

    MasterWindow.instance = None
    window = MasterWindow(800, 800, "frame")
    window.Render = Mock()

    window.rightSubWindow = CreateSubWindowMock()
    window.leftSubWindow = CreateSubWindowMock()

    assert window._CalculateSeperatorOffset() == 400

    window.leftSubWindow = None

    assert window._CalculateSeperatorOffset() == 0


def test_StripEvents():
    mockPyGame()

    MasterWindow.instance = None
    window = MasterWindow(800, 800, "frame")
    window.Render = Mock()
    ISubWindow._CalculateSeperatorOffset = Mock(return_value=20)

    window.events = [SimpleNamespace(**{
        "type": MOUSEBUTTONDOWN,
        "pos": (
            0, 0
        )
    })]
    (leftEvents, _) = window._GetStrippedEvents()
    assert len(leftEvents) is 1, "Events were not stripped correctly"

    window.events = [SimpleNamespace(**{
        "type": MOUSEBUTTONDOWN,
        "pos": (
            40, 0
        )
    })]
    (_, rightEvents) = window._GetStrippedEvents()
    assert len(rightEvents) is 1, "Events were not stripped correctly"

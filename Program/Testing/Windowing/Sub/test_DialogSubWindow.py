# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software Project course.
# © Copyright Utrecht University (Department of Information and Computing Sciences)

from types import SimpleNamespace
from unittest.mock import Mock
from Windowing.Sub.DialogSubWindow import DialogSubWindow

result = False
newPosition = (0, 0)


def test_GetSelectedOption():
    x = Mock()
    x.selectedOption = 1
    assert DialogSubWindow.GetSelectedOption(x) == 1


def test_InputBeenGiven():
    x = Mock()
    x.selectedOption = -1
    assert DialogSubWindow.InputBeenGiven(x) is False

    x.selectedOption = 0
    assert DialogSubWindow.InputBeenGiven(x) is True


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
    DialogSubWindow._ResizeGUIManager(x)

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

    DialogSubWindow._CenterPanel(x)

    assert newPosition == (25, 25)

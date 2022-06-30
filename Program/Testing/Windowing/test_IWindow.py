# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software Project course.
# © Copyright Utrecht University (Department of Information and Computing Sciences)
from unittest.mock import Mock, patch

import pytest
import pygame

from Windowing.IWindow import IWindow


class TestIWindow:
    @pytest.mark.parametrize("test_input", [1, 987543, -20, 'cat'])
    def test_keyCallBack(self, test_input):

        # Create a Mock, then call the function that should be tested.
        x = Mock()
        IWindow.SetKeyCallback(x, test_input)

        assert x.keyCallback == test_input

    @pytest.mark.parametrize("test_input", [1, 987543, -20, 'cat'])
    def test_mouseCallBack(self, test_input):

        # Create a Mock, then call the function that should be tested.
        x = Mock()
        IWindow.SetMouseCallback(x, test_input)

        assert x.mouseCallback == test_input

    @patch("pygame.display.get_surface", Mock(return_value=pygame.surface.Surface((800, 800))))
    def test_Screenshot(self):
        screenshot = IWindow.TakeScreenShot()
        assert screenshot.get_size() == (800, 800)

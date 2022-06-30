# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software Project course.
# © Copyright Utrecht University (Department of Information and Computing Sciences)

from unittest.mock import Mock, patch
import cv2
import pygame
import pytest

from Calibrator.Input.PrimitiveInput import PrimitiveInput, Primitives
from Calibrator.Input.Primitives.PlanePrimitive import PlanePrimitive
from Windowing.IWindow import IWindow

from IO import Pathing


class TestPrimitiveInput:
    def test_MouseCallback(self):
        primitiveInput = PrimitiveInput(None, None)
        primitiveInput.RequestPrimitives([Primitives.Plane])
        primitiveInput.MouseCallback(pygame.MOUSEBUTTONDOWN, 0, 0)

        assert primitiveInput.holdingMouse is True, "The mouse is not being held"

        primitiveInput.MouseCallback(pygame.MOUSEBUTTONUP, 0, 0)

        assert primitiveInput.holdingMouse is False, "The mouse is still being held"

    def test_KeyCallback(self):
        primitiveInput = PrimitiveInput(None, None)
        primitiveInput.RequestPrimitives([Primitives.Plane])
        primitiveInput._GetPrimitiveResult = Mock()
        primitiveInput.KeyCallback(pygame.KEYDOWN, pygame.K_n)
        assert primitiveInput.currentPrimitiveId == -1, "The current primitive id is not -1"

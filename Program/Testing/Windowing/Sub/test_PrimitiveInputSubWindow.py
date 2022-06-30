# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software Project course.
# © Copyright Utrecht University (Department of Information and Computing Sciences)

from unittest.mock import Mock
import cv2
import numpy
import pygame
import pytest
from pygame import KEYDOWN

from Calibrator.Input.PrimitiveInput import Primitives
from Calibrator.Input.Primitives.PlanePrimitive import PlanePrimitive
from IO import Pathing
from Windowing.IWindow import IWindow
from Windowing.Rendering import Rendering
from Windowing.Sub.ISubWindow import ISubWindow
from Windowing.Sub.PrimitiveInputSubWindow import PrimitiveInputSubWindow


class TestPrimitiveInputSubWindow:
    @pytest.mark.parametrize("path, title",
                             [
                                 ('Testing/Assets/testImage.png', "TITLE"),
                                 ('Testing/Assets/testImage.png', "Another title"),
                                 ('Testing/Assets/testImage.png', "Third title"),
                                 ('Testing/Assets/testImage.png', "TestingTitle")
                             ])
    def test_init(self, path, title):
        # First get the image path, then create a pygame image
        imagePath = Pathing.AssureAbsolutePath(path)
        image = cv2.imread(str(imagePath))

        # Mock these so the display doesn't open
        pygame.init = Mock()
        pygame.display = Mock()
        pygame.display.get_init = Mock(return_value=False)

        # Create an instance of PrimitiveInputSubWindow
        primitiveInputWindow = PrimitiveInputSubWindow(image, title)

        # Assert that the given parameters get saved correctly in the primitiveInputWindow
        assert primitiveInputWindow.image.get_width() ==\
            Rendering.ConvertOpenCVImageToPyGameImage(image).get_width()
        assert primitiveInputWindow.image.get_height() ==\
            Rendering.ConvertOpenCVImageToPyGameImage(image).get_height()

        # Assert that all variables are set to their correct values
        assert primitiveInputWindow.primitiveInput is not None

    def test_RequestPrimitives(self):
        # First get the image path, then create a pygame image
        imagePath = Pathing.AssureAbsolutePath('Testing/Assets/testImage.png')
        image = cv2.imread(str(imagePath))

        # Mock these so the display doesn't open
        pygame.init = Mock()
        pygame.display = Mock()
        pygame.display.get_init = Mock(return_value=False)

        # Create an instance of PrimitiveInputSubWindow
        primitiveInputWindow = PrimitiveInputSubWindow(image)

        # Check if the user input crashes if the list of primitives is empty
        pytest.raises(ValueError, primitiveInputWindow.RequestPrimitivesInput, [])

        # Check if a primitive plane can be passed through the primitive input
        primitiveInputWindow.RequestPrimitivesInput([Primitives.Plane])

        # Get results
        result = primitiveInputWindow.GetPrimitiveResults()

        # Check if not finished
        assert result[0] is False, "Primitive input should not have finished!"

        # Call next primitive
        primitiveInputWindow.primitiveInput.NextPrimitive()

        # Check if the list of primitives is correct
        assert len(result[1]) == 1, "The list of primitives is not correct."
        assert result[1][0].primitive is Primitives.Plane, "The primitive list is not correct."

        # Get the starting absolute points of a plane primitive
        plane = PlanePrimitive()
        absolutePoints = plane.GetAbsolutePoints(image.shape[1], image.shape[0])

        # Check if the points are correct
        assert len(result[1][0].points) == 4, "The number of points is not correct."
        allPointsCorrect = True
        for i in range(4):
            rp = result[1][0].points[i]
            ap = absolutePoints[i]
            if rp[0] != ap[0] or rp[1] != ap[1]:
                allPointsCorrect = False
                break

        assert allPointsCorrect, "Primitive input modified input plane primitive without any input!"


def test_GetScaledImageSize():
    # First get the image path, then create a pygame image
    imagePath = Pathing.AssureAbsolutePath('Testing/Assets/testImage.png')
    image = cv2.imread(str(imagePath))

    # Mock these so the display doesn't open
    pygame.init = Mock()
    pygame.display = Mock()
    pygame.display.get_init = Mock(return_value=False)

    # Create an instance of PrimitiveInputSubWindow
    primitiveInputWindow = PrimitiveInputSubWindow(image)
    primitiveInputWindow.previousWidth = primitiveInputWindow.image.get_width()
    primitiveInputWindow.previousHeight = primitiveInputWindow.image.get_height()

    # Get scaled image size
    scaledImageSize = primitiveInputWindow.GetScaledImageSize()
    assert \
        scaledImageSize[0] == primitiveInputWindow.image.get_width() and \
        scaledImageSize[1] == primitiveInputWindow.image.get_height(), \
        "Scaled image size should not have been scaled."


def test_GetScaledImageDrawingPoint():
    # First get the image path, then create a pygame image
    imagePath = Pathing.AssureAbsolutePath('Testing/Assets/testImage.png')
    image = cv2.imread(str(imagePath))

    # Mock these so the display doesn't open
    pygame.init = Mock()
    pygame.display = Mock()
    pygame.display.get_init = Mock(return_value=False)

    # Create an instance of PrimitiveInputSubWindow
    primitiveInputWindow = PrimitiveInputSubWindow(image)
    primitiveInputWindow.previousWidth = primitiveInputWindow.image.get_width()
    primitiveInputWindow.previousHeight = primitiveInputWindow.image.get_height()

    # Get scaled image drawing point
    scaledImageDrawingPoint = primitiveInputWindow.GetScaledImageDrawingPoint()
    assert \
        scaledImageDrawingPoint[0] == 0 and scaledImageDrawingPoint[1] == 0, \
        "Scaled image drawing point should default to zero"


def test_InputHandlers():
    # First get the image path, then create a pygame image
    imagePath = Pathing.AssureAbsolutePath('Testing/Assets/testImage.png')
    image = cv2.imread(str(imagePath))

    # Mock these so the display doesn't open
    pygame.init = Mock()
    pygame.display = Mock()
    pygame.display.get_init = Mock(return_value=False)

    # Create an instance of PrimitiveInputSubWindow
    primitiveInputWindow = PrimitiveInputSubWindow(image)

    mouseEventDownMock = Mock()
    mouseEventDownMock.type = Mock(pygame.MOUSEBUTTONDOWN)
    mouseEventDownMock.pos = Mock(return_value=(10, 10))

    primitiveInputWindow.primitiveInput.invalidated = True
    primitiveInputWindow.HandleInput([mouseEventDownMock])
    assert primitiveInputWindow.invalidated, "Primitive input sub window should have invalidated set to True."

    keyEventDownMock = Mock()
    keyEventDownMock.type = Mock(KEYDOWN)
    primitiveInputWindow.primitiveInput.invalidated = True

    primitiveInputWindow.HandleInput([keyEventDownMock])
    assert primitiveInputWindow.invalidated, "Primitive input sub window should have invalidated set to True."

# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software Project course.
# © Copyright Utrecht University (Department of Information and Computing Sciences)

"""
Handles the primitive input for the calibration.
"""

from enum import Enum

import numpy as np
import pygame
from pygame import MOUSEBUTTONDOWN, MOUSEBUTTONUP, KEYDOWN, K_n, KEYUP
from Calibrator.Input.Primitives.PlanePrimitive import PlanePrimitive
from Calibrator.Input.Primitives.PointsPrimitive import PointsPrimitive
from Calibrator.Input.Primitives.SquarePrimitive import SquarePrimitive
from Windowing.Rendering import Rendering


class Primitives(Enum):
    """ The possible primitives that can be used in the PrimitiveInput. """
    Plane = PlanePrimitive
    Points = PointsPrimitive
    Square = SquarePrimitive


class PrimitiveInputResult:
    def __init__(self, primitive, points):
        """ Initialize the PrimitiveInputResult class.

            Parameters
            ----------
            primitive : Primitives
                The primitive that was used.
            points : list
                The points that were used.
        """

        self.primitive = primitive
        self.points = points

        # Check if primitive is a type
        if not isinstance(primitive, Enum):
            raise ValueError("The primitive is not a type")


class PrimitiveInput:
    image: pygame.surface = None
    parent = None
    sibling = None

    primitives = None
    results = []
    currentPrimitiveId = -1
    currentPrimitive = None
    renderScaled = False
    holdingMouse = False

    invalidated = False
    finished = False

    def __init__(self, image: pygame.surface, parent: 'PrimitiveInputSubWindow', sibling=None):
        """ Initializes the primitive input class. Make
            sure to handle the input callback before requesting
            the primitives.

            Parameters
            ----------
            image : pygame.Surface or cv2.Image
                The image that is used to draw the primitive.
            parent: PrimitiveInputSubWindow
                The parent window of the primitive input.
            sibling: PrimitiveInput
                The sibling primitive input, only used if the
                requested primitives will be linked.
        """
        self.image = image
        if isinstance(image, np.ndarray):
            self.image = Rendering.ConvertOpenCVImageToPyGameImage(image)
        self.parent = parent
        self.sibling = sibling

        # Always self link
        if self.sibling is not None:
            self.sibling.sibling = self

    def RequestPrimitives(
            self, primitives
    ):
        """ Fills the primitives list with the specified primitives.

            Parameters
            ----------
            primitives : list
                The primitives that are used in the input loop.
        """

        # Set primitives and reset other variables
        self.primitives = primitives
        self.currentPrimitiveId = 0
        self.finished = False
        self.results = []

        # Make sure that the list of primitives is not empty
        # and contains primitive enums
        if len(self.primitives) == 0:
            raise ValueError("The list of primitives is empty")
        for primitive in self.primitives:
            if not isinstance(primitive, Enum):
                raise ValueError("The list of primitives contains an invalid primitive")

        # Create first primitive
        self._CreatePrimitive()

        # Set invalidated
        self.invalidated = True

    def KeyCallback(self, event, key):
        """ Handles key events

        Parameters
        ----------
        event : int
            The event type.
        key : int
            The key that was pressed.
        """

        # Check if key down event
        if event == KEYDOWN:
            # Check if key is 'n'
            if key == K_n:
                # Next primitive
                self.NextPrimitive()
            # Check if key is control
            elif key == pygame.K_LCTRL:
                # Set render scaled to True
                self.renderScaled = True
                # Set invalidated flag
                self.invalidated = True
        # Check if key up event
        elif event == KEYUP:
            # Check if key is control
            if key == pygame.K_LCTRL:
                # Set render scaled to False
                self.renderScaled = False
                # Set invalidated flag
                self.invalidated = True

    def MouseCallback(self, event, relativeMouseX, relativeMouseY):
        """ Handles mouse events

        Parameters
        ----------
        event : int
            The event type.
        relativeMouseX : int
            The relative x position of the mouse.
        relativeMouseY : int
            The relative y position of the mouse.
        """

        # Make sure that the current primitive is valid
        if self.currentPrimitiveId == -1 or self.currentPrimitive is None:
            return

        # Handle mouse events
        if event == MOUSEBUTTONDOWN:
            self.holdingMouse = True
        elif event == MOUSEBUTTONUP:
            self.currentPrimitive.ResetMouseMovement()
            self.holdingMouse = False
            self.invalidated = True

        # Handle mouse movement during events
        if self.holdingMouse:
            # Handle current primitive movement and check if there was any movement
            movedPrimitive = self.currentPrimitive.HandleMouseMovement(relativeMouseX, relativeMouseY)

            # If there was any movement, render and set window zoomed held to false
            if movedPrimitive:
                self.invalidated = True

    def NextPrimitive(self):
        """ Moves to the next primitive """

        # Get the current primitive result
        self.results.append(self._GetPrimitiveResult())

        # Increment primitive id and create new primitive
        self.currentPrimitiveId += 1
        if self.currentPrimitiveId >= len(self.primitives):
            # Set current primitive ID to -1
            self.currentPrimitiveId = -1

            # Set finished
            self.finished = True
        else:
            # Create new primitive
            self._CreatePrimitive()

            # Set invalidated
            self.invalidated = True

    def _CreatePrimitive(self):
        """ Creates the current primitive """

        self.currentPrimitive = self.primitives[self.currentPrimitiveId].value()

    def _GetPrimitiveResult(self):
        """ Returns the result of the current primitive

            Returns
            -------
            PrimitiveInputResult
                The result of the current primitive.
        """

        return PrimitiveInputResult(
            self.primitives[self.currentPrimitiveId],
            self.currentPrimitive.GetAbsolutePoints(
                self.image.get_width(),
                self.image.get_height()
            )
        )

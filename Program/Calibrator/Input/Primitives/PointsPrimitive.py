# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software Project course.
# © Copyright Utrecht University (Department of Information and Computing Sciences)

import cv2
import numpy as np
from Calibrator.Input.Primitives.IPrimitive import IPrimitive, IPrimitivePoint
from Windowing.Rendering import Rendering


class PointsPrimitive(IPrimitive):

    def __init__(self, relativeX=0.5, relativeY=0.5, relativeWidth=0.5, relativeHeight=0.5):
        """
        initialize a new point cloud
        """
        # Create points
        points = [
            IPrimitivePoint(-relativeWidth / 2, -relativeHeight / 2, (255, 0, 0, 255)),
            IPrimitivePoint(relativeWidth / 2, -relativeHeight / 2, (0, 255, 0, 255)),
            IPrimitivePoint(relativeWidth / 2, relativeHeight / 2, (0, 0, 255, 255)),
            IPrimitivePoint(-relativeWidth / 2, relativeHeight / 2, (255, 255, 0, 255)),
            IPrimitivePoint(0, -relativeHeight / 2, (127, 0, 255, 255)),
            IPrimitivePoint(relativeWidth / 2, 0, (0, 255, 255, 255)),
            IPrimitivePoint(0, relativeHeight / 2, (255, 127, 0, 255)),
            IPrimitivePoint(-relativeWidth / 2, 0, (255, 0, 255, 255))
        ]

        # Call super constructor
        super(PointsPrimitive, self).__init__(relativeX, relativeY, points)

    def IsMouseOver(self, relativeMouseX, relativeMouseY) -> bool:
        """ Check if the mouse is over the primitive.
            but we never want this with point cloud
        Parameters
        ----------
        relativeMouseX : int
            The relative x screen position of the mouse.
        relativeMouseY : int
            The relative y screen position of the mouse.

        Returns
        -------
        bool
            False
        """

        return False

    def Render(self, surface, xOffset, yOffset, absoluteWidth, absoluteHeight, scaled=False):  # pragma: no cover
        """ Render the primitive.

        Parameters
        ----------
        surface : pygame.Surface
            The surface to render on.
        xOffset : int
            The x offset to render the primitive at.
        yOffset : int
            The y offset to render the primitive at.
        absoluteWidth : int
            The absolute width of the respective image.
        absoluteHeight : int
            The absolute height of the respective image
        scaled : bool
            Determines if the points should be shown scaled. Default is False.
        """
        super(PointsPrimitive, self).Render(surface, xOffset, yOffset, absoluteWidth, absoluteHeight, scaled)

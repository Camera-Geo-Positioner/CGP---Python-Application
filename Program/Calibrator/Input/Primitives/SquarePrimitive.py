# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software Project course.
# © Copyright Utrecht University (Department of Information and Computing Sciences)

"""
Implementation of the IPrimitive.
Create a plane on screen for calibration.
"""

import cv2
import numpy as np
from Calibrator.Input.Primitives.IPrimitive import IPrimitive, IPrimitivePoint
from Windowing.Rendering import Rendering


class SquarePrimitive(IPrimitive):
    def __init__(self, relativeX=0.5, relativeY=0.5, relativeWidth=0.5, relativeHeight=0.5):
        """ Initialize a new plane primitive.

        Parameters
        ----------
        relativeX : float
            The relative center x position of the plane.
        relativeY : float
            The relative center y position of the plane.
        relativeWidth : float
            The relative width of the plane.
        relativeHeight : float
            The relative height of the plane.
        """

        # Create points
        points = [
            IPrimitivePoint(-relativeWidth * 0.9, -relativeHeight * 0.9),
            IPrimitivePoint(relativeWidth * 0.9, relativeHeight * 0.9)
        ]

        # Call super constructor
        super(SquarePrimitive, self).__init__(relativeX, relativeY, points)

    def IsMouseOver(self, relativeMouseX, relativeMouseY) -> bool:
        """ Check if the mouse is over the primitive.

        Parameters
        ----------
        relativeMouseX : float
            The relative x screen position of the mouse.
        relativeMouseY : float
            The relative y screen position of the mouse.

        Returns
        -------
        bool
            True if the mouse is over the primitive, false otherwise.
        """

        # Check if mouse is over the quadrilateral plane - we require
        # an arbitrary scale to go from float space to int space
        arbitraryScale = 100

        points = self.GetRelativePoints()
        for i in range(len(points)):
            points[i] = (int(points[i][0] * arbitraryScale), int(points[i][1] * arbitraryScale))

        # Because it's a square consisting of two points, compensate for the missing
        # two points
        points.append(
            (points[0][0], points[1][1])
        )
        points.append(
            (points[1][0], points[0][1])
        )

        mouseX = int(relativeMouseX * arbitraryScale)
        mouseY = int(relativeMouseY * arbitraryScale)

        return cv2.pointPolygonTest(np.array(points), (mouseX, mouseY), False) >= 0

    def Render(self, surface, xOffset, yOffset, absoluteWidth, absoluteHeight, scaled=False):
        """ Render the primitive.

        Parameters
        ----------
        surface : pygame.Surface
            The surface to render on.
        xOffset : int
            The x offset of the primitive.
        yOffset : int
            The y offset of the primitive.
        absoluteWidth : int
            The absolute width of the respective image.
        absoluteHeight : int
            The absolute height of the respective image.
        scaled : bool
            Determines if the points should be shown scaled. Default is False.
        """

        # Get the absolute points, with the offset applied
        points = self.GetAbsolutePoints(absoluteWidth, absoluteHeight)
        for i in range(len(points)):
            points[i] = (int(points[i][0]) + xOffset, int(points[i][1]) + yOffset)

        # Setup alpha and colors for the lines between points
        alpha = 255
        green = (0, 255, 0, alpha)

        (x1, y1) = points[0]
        (x2, y2) = points[1]

        # create the four lines to complete the square
        Rendering.RenderLine(surface, x1, y1, x2, y1, green)
        Rendering.RenderLine(surface, x1, y2, x2, y2, green)
        Rendering.RenderLine(surface, x2, y1, x2, y2, green)
        Rendering.RenderLine(surface, x1, y1, x1, y2, green)

        super(SquarePrimitive, self).Render(surface, xOffset, yOffset, absoluteWidth, absoluteHeight, scaled)

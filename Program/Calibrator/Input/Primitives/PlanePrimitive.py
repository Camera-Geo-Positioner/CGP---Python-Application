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


class PlanePrimitive(IPrimitive):
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
            IPrimitivePoint(-relativeWidth / 2, -relativeHeight / 2),
            IPrimitivePoint(relativeWidth / 2, -relativeHeight / 2),
            IPrimitivePoint(relativeWidth / 2, relativeHeight / 2),
            IPrimitivePoint(-relativeWidth / 2, relativeHeight / 2)
        ]

        # Call super constructor
        super(PlanePrimitive, self).__init__(relativeX, relativeY, points)

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

        mouseX = int(relativeMouseX * arbitraryScale)
        mouseY = int(relativeMouseY * arbitraryScale)

        return cv2.pointPolygonTest(np.array(points), (mouseX, mouseY), False) >= 0

    def Render(self, surface, xOffset, yOffset, absoluteWidth, absoluteHeight, scaled=False):  # pragma: no cover
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
        colors = [
            (255, 0, 0, alpha),  # Red
            (0, 0, 255, alpha),  # Blue
            (255, 0, 0, alpha),  # Red
            (0, 0, 255, alpha)   # Blue
        ]

        # Draw a perspective grid on the plane between the four points,
        # we do this by setting up a number of points on the lines between
        # the points, and then drawing a line between each of these points

        # Get the lines between the points
        subPoints = 7
        lines = []
        for i in range(len(points)):
            lines.append(np.linspace(points[i][0], points[(i + 1) % len(points)][0], subPoints))
            lines.append(np.linspace(points[i][1], points[(i + 1) % len(points)][1], subPoints))

        # Draw the lines from one line to it's opposite line to create a grid
        for i in range(subPoints):
            # Skip the first and last point
            if i == 0 or i == subPoints - 1:
                continue

            # Render the lines
            Rendering.RenderLine(
                surface,
                int(lines[0][i]), int(lines[1][i]),
                int(lines[4][(subPoints - 1) - i]), int(lines[5][(subPoints - 1) - i]),
                (255, 255, 255, alpha)
            )
            Rendering.RenderLine(
                surface,
                int(lines[2][i]), int(lines[3][i]),
                int(lines[6][(subPoints - 1) - i]), int(lines[7][(subPoints - 1) - i]),
                (255, 255, 255, alpha)
            )

        # Draw the lines and direction texts between the points
        direction = ["Verweg", "Rechts", "Dichtbij", "Links"]
        # Magic numbers to get the boxes and text to fit and be centered
        directionOffset = [(-10, -12), (10, 0), (-12, 14), (-40, 0)]
        boxOffset = (-4, -8)
        boxesSizes = [(53, 16), (50, 16), (55, 16), (40, 16)]
        for i in range(len(points)):
            x1, y1 = points[i]
            x2, y2 = points[(i + 1) % len(points)]

            # Render line
            Rendering.RenderLine(surface, x1, y1, x2, y2, colors[i], 2)

            # Render box with text
            Rendering.RenderBox(
                surface,
                (x1 + x2) / 2 + directionOffset[i][0] + boxOffset[0],
                (y1 + y2) / 2 + directionOffset[i][1] + boxOffset[1],
                boxesSizes[i][0],
                boxesSizes[i][1],
                (25, 25, 25, 125)
            )
            Rendering.RenderText(
                surface,
                direction[i],
                (x1 + x2) / 2 + directionOffset[i][0],
                (y1 + y2) / 2 + directionOffset[i][1],
                Rendering.FontSize.Small,
                Rendering.TextAlignment.MiddleLeft,
                (255, 255, 255, alpha),
                1
            )

        super(PlanePrimitive, self).Render(surface, xOffset, yOffset, absoluteWidth, absoluteHeight, scaled)

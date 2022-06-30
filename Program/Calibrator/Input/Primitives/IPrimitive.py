# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software Project course.
# © Copyright Utrecht University (Department of Information and Computing Sciences)

"""
Interface for primitive inputs for the calibration.
"""

from abc import ABC, abstractmethod
from Windowing.Rendering import Rendering


class IPrimitive(ABC):
    # Movement variables
    prevMousePositionX = 0
    prevMousePositionY = 0
    moveAsWhole = False
    movePoint = False
    movePointIndex = None
    prevMovePointIndex = None

    # This class is an abstract class that defines the interface for all primitives.
    def __init__(self, relativeX, relativeY, points):
        """ Initializes a primitive.

        Parameters
        ----------
        relativeX : int
            The relative center x position of the primitive.
        relativeY : int
            The relative center y position of the primitive.
        points : list
            The points of the primitive.
        """

        self.x = relativeX
        self.y = relativeY
        self.points = points

        # Check if the points are IPrimitivePoints
        for point in self.points:
            if not isinstance(point, IPrimitivePoint):
                raise TypeError("The points must be of type IPrimitivePoint.")

    # Moves the shape as a whole
    def MoveTo(self, relativeX, relativeY):
        """ Moves the shape as a whole.

        Parameters
        ----------
        relativeX : int
            The relative center x position of the primitive.
        relativeY : int
            The relative center y position of the primitive.
        """

        # For all points in the primitive, check if the offset
        # would put them out-of-bounds
        dx = relativeX - self.prevMousePositionX
        dy = relativeY - self.prevMousePositionY
        for point in self.GetRelativePoints():
            nx = point[0] + dx
            ny = point[1] + dy

            if nx < 0 or nx > 1:
                dx = 0
            if ny < 0 or ny > 1:
                dy = 0

        # Move as whole
        self.x += dx
        self.y += dy

    # Converts relative primitive points to absolute screen points
    def GetAbsolutePoints(self, absoluteWidth, absoluteHeight) -> [(int, int)]:
        """ Converts relative primitive points to absolute screen points.

        Parameters
        ----------
        absoluteWidth : int
            The absolute width of the respective image.
        absoluteHeight : int
            The absolute height of the respective image.

        Returns
        -------
        [(int, int)]
            The absolute screen points of the primitive.
        """

        return list(
            map(
                lambda point: self.GetAbsolutePoint(point, absoluteWidth, absoluteHeight),
                range(len(self.points))
            )
        )

    # Converts specific relative primitive point to absolute screen point
    def GetAbsolutePoint(self, index, absoluteWidth, absoluteHeight) -> (int, int):
        """ Converts specific relative primitive point with index to absolute screen point.

         Parameters
         ----------
         index : int
             The index of the point to be converted.
         absoluteWidth : int
             The absolute width of the respective image.
         absoluteHeight : int
             The absolute height of the respective image.

         Returns
         -------
         (int, int)
             The absolute screen point of the primitive.
         """

        width = (self.x + self.points[index].relativeX) * absoluteWidth
        height = (self.y + self.points[index].relativeY) * absoluteHeight
        return int(width), int(height)

    # Converts relative primitive points to relative screen points
    def GetRelativePoints(self) -> [(float, float)]:
        """ Lists relative primitive points.

        Returns
        -------
        [(float, float)]
            The relative screen points of the primitive.
        """

        return list(
            map(
                self.GetRelativePoint,
                range(len(self.points))
            )
        )

    # Converts specific relative primitive point to relative screen point
    def GetRelativePoint(self, index) -> (float, float):
        """ Get a specific relative primitive point.

        Parameters
        ----------
        index : int
            The index of the point.

        Returns
        -------
        (float, float)
            The relative screen point of the primitive at the specified index.
        """

        return self.x + self.points[index].relativeX, self.y + self.points[index].relativeY

    # Checks if the relative mouse position is over any primitive point
    def IsMouseOverPoint(self, relativeMouseX, relativeMouseY) -> (bool, int):
        """ Checks if the relative mouse position is over any primitive point.

        Parameters
        ----------
        relativeMouseX : float
            The relative x screen position of the mouse.
        relativeMouseY : float
            The relative y screen position of the mouse.

        Returns
        -------
        (bool, int)
            A tuple containing the following:
                - True if the mouse is over a point, False otherwise.
                - The index of the point if the mouse is over a point, None otherwise.
        """

        # Get all valid points
        valid = [False] * len(self.points)
        for i in range(len(self.points)):
            if self.points[i].IsMouseOver(self.x, self.y, relativeMouseX, relativeMouseY):
                valid[i] = True

        # Be biased for the previous move point index
        if self.prevMovePointIndex is not None and valid[self.prevMovePointIndex]:
            return True, self.prevMovePointIndex

        # Otherwise, take the first valid point
        for i in range(len(valid)):
            if valid[i]:
                return True, i
        return False, None

    def HandleMouseMovement(self, relativeMouseX, relativeMouseY) -> bool:
        """ Handles mouse movement.

        Parameters
        ----------
        relativeMouseX : float
            The relative x screen position of the mouse.
        relativeMouseY : float
            The relative y screen position of the mouse.

        Returns
        -------
        bool
            True if the primitive was moved, False otherwise.
        """

        movedPrimitive = False

        # Handle movement from previous frame
        if self.moveAsWhole:
            self.MoveTo(relativeMouseX, relativeMouseY)
            movedPrimitive = True
        elif self.movePoint:
            self.points[self.movePointIndex].MoveTo(relativeMouseX - self.x, relativeMouseY - self.y)
            self.prevMovePointIndex = self.movePointIndex
            movedPrimitive = True

        # Reset movement
        self.ResetMouseMovement()

        # Check if the mouse is over any of the primitive points
        mouseOverPoint, pointIndex = self.IsMouseOverPoint(relativeMouseX, relativeMouseY)
        if mouseOverPoint:
            # If the mouse is over a primitive point, move that point
            self.movePoint = True
            self.movePointIndex = pointIndex

        # Check if the mouse is over the primitive as a whole
        elif self.IsMouseOver(relativeMouseX, relativeMouseY):
            # If the mouse is not over a primitive point, move the whole primitive
            self.moveAsWhole = True
            movedPrimitive = True

        # Set previous mouse position
        self.prevMousePositionX = relativeMouseX
        self.prevMousePositionY = relativeMouseY

        return movedPrimitive

    def ResetMouseMovement(self):
        """ Resets mouse movement. """

        self.moveAsWhole = False
        self.movePoint = False
        self.movePointIndex = None

    @abstractmethod
    # Check if the relative mouse position is over the primitive as a whole
    def IsMouseOver(self, relativeMouseX, relativeMouseY) -> bool:
        """ Checks if the relative mouse position is over the primitive as a whole.

        Parameters
        ----------
        relativeMouseX : float
            The relative x screen position of the mouse.
        relativeMouseY : float
            The relative y screen position of the mouse.

        Returns
        -------
        bool
            True if the mouse is over the primitive as a whole, False otherwise.
        """

        raise NotImplementedError("The method isMouseOver is not implemented.")
        pass

    @abstractmethod
    # Render the primitive to a surface
    def Render(self, surface, xOffset, yOffset, absoluteWidth, absoluteHeight, scaled=False):  # pragma: no cover
        """ Renders the primitive to a surface.

        Parameters
        ----------
        surface : pygame.Surface
            The surface to render the primitive to.
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

        for i in range(len(self.points)):
            self.points[i].Render(
                surface,
                self.x, self.y,
                xOffset, yOffset,
                absoluteWidth, absoluteHeight,
                i,
                scaled
            )


class IPrimitivePoint:
    collisionRadius = 3
    borderRadius = 1
    innerBorderColor = (255, 255, 255, 255)
    outerBorderColor = (0, 0, 0, 64)

    def __init__(self, relativeX, relativeY, color=(255, 255, 255, 255)):
        """ Initializes the primitive point.

        Parameters
        ----------
        relativeX : float
            The relative x position of the point.
        relativeY : float
            The relative y position of the point.
        """

        self.relativeX = relativeX
        self.relativeY = relativeY
        self.color = color

    def MoveTo(self, relativeX, relativeY):
        """ Moves the primitive point to the relative position.

        Parameters
        ----------
        relativeX : float
            The relative x position of the point.
        relativeY : float
            The relative y position of the point.
        """

        self.relativeX = relativeX
        self.relativeY = relativeY

    def IsMouseOver(self, x, y, relativeMouseX, relativeMouseY) -> bool:
        """ Moves the primitive point to the relative position.

        Parameters
        ----------
        x : int
            The relative x position of the parent.
        y : int
            The relative y position of the parent.
        relativeMouseX : float
            The relative x position of the mouse.
        relativeMouseY : float
            The relative y position of the mouse.
        """

        ax = x + self.relativeX
        ay = y + self.relativeY
        dx = abs(relativeMouseX - ax)
        dy = abs(relativeMouseY - ay)
        relativeRadius = self.collisionRadius / 128.0
        return dx * dx + dy * dy <= relativeRadius * relativeRadius

    def Render(
            self,
            surface,
            x, y,
            xOffset, yOffset,
            absoluteWidth, absoluteHeight,
            identifier,
            scaled=False
    ):  # pragma: no cover
        """ Renders the primitive point to a surface.

        Parameters
        ----------
        surface : pygame.Surface
            The surface to render to.
        x : float
            The relative x position of the primitive (parent).
        y : float
            The relative y position of the primitive (parent).
        xOffset : int
            The x offset to render the primitive at.
        yOffset : int
            The y offset to render the primitive at.
        absoluteWidth : int
            The absolute width of the respective image.
        absoluteHeight : int
            The absolute height of the respective image
        identifier : int
            The identifier of the primitive point.
        scaled : bool
            Determines if the point should be shown scaled. Default is False.
        """
        # Calculate scale
        scale = 3.5 if scaled else 1

        # Calculate point center
        px = int((x + self.relativeX) * absoluteWidth) + xOffset
        py = int((y + self.relativeY) * absoluteHeight) + yOffset

        # Render outer border
        Rendering.RenderPoint(
            surface,
            px, py,
            self.outerBorderColor,
            (self.collisionRadius * scale + self.borderRadius * 2)
        )

        # Render inner border
        Rendering.RenderPoint(
            surface,
            px, py,
            self.innerBorderColor,
            (self.collisionRadius * scale + self.borderRadius)
        )

        # Render inner fill
        Rendering.RenderPoint(
            surface,
            px, py,
            self.color,
            self.collisionRadius * scale
        )

        # If scaled: render the ID inside the point
        if scaled:
            Rendering.RenderText(
                surface=surface,
                text=str(identifier),
                x=px, y=py,
                shadowOffset=1,
                textAlignment=Rendering.TextAlignment.MiddleCenter,
                fontSize=Rendering.FontSize.Mini
            )

# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software Project course.
# © Copyright Utrecht University (Department of Information and Computing Sciences)

"""
Implementation of the ISubWindow
Takes a frame and shows it in a sub window with additional user input.
"""

import pygame
from Windowing.Rendering import Rendering
from Windowing.Sub.ISubWindow import ISubWindow


class CameraSubWindow(ISubWindow):
    """ This class represents a camera sub window. """
    frame = None

    pressed = False
    showPressed = False
    mouseX = 0
    mouseY = 0
    aMouseX = 0
    aMouseY = 0
    scale: float = 1

    def __init__(self):
        """
        Constructor a new camera window instance.
        """

        # Call super
        super(CameraSubWindow, self).__init__("Camera Venster", "Windowing/Assets/Icons/camera.png")

        # Set mouse callback
        self.SetMouseCallback(self.MouseClick)

    def Update(self, deltaTime):  # pragma: no cover
        """ Update the camera sub window.

        Parameters
        ----------
        deltaTime : float
            The time between the last frame and the current frame.
        """
        pass

    def Render(self, width: int, height: int) -> pygame.Surface:  # pragma: no cover
        """ Renders the camera window.

        Parameters
        ----------
        width : int
            The rendering width of the sub window.
        height : int
            The rendering height of the sub window.
        """

        # Create surface
        surface = super(CameraSubWindow, self).Render(width, height)

        # If there is currently no frame, return the blank surface
        if self.frame is None:
            return surface

        # Calculate aspect ratio of image
        aspectRatio = self.frame.get_width() / self.frame.get_height()

        # Draw scaled image
        if width / height <= aspectRatio:
            # Calculate adjusted height
            adjustedHeight = width / aspectRatio
            self.imageOffsetY = (height - adjustedHeight) / 2
            self.imageOffsetX = 0
            self.scale = adjustedHeight / self.frame.get_height()

            # Render the image to the surface at the center of the screen,
            # with the adjusted height
            surface.blit(
                pygame.transform.scale(self.frame, (width, adjustedHeight)),
                (0, height / 2 - adjustedHeight / 2)
            )
        else:
            # Calculate adjusted width
            adjustedWidth = height * aspectRatio
            self.imageOffsetX = (width - adjustedWidth) / 2
            self.imageOffsetY = 0
            self.scale = adjustedWidth / self.frame.get_width()

            # Render the image to the surface at the center of the screen,
            # with the adjusted width
            surface.blit(
                pygame.transform.scale(self.frame, (adjustedWidth, height)),
                (width / 2 - adjustedWidth / 2, 0)
            )

        # Draw cross, if mouse was clicked
        if self.pressed and self.showPressed:
            mouseX, mouseY = self.ImageToScreenPosition(self.aMouseX, self.aMouseY)
            Rendering.RenderLine(surface, mouseX - 4, mouseY, mouseX + 4, mouseY, (255, 0, 0))
            Rendering.RenderLine(surface, mouseX, mouseY - 4, mouseX, mouseY + 4, (255, 0, 0))

        return surface

    def MousePosition(self):
        """ Get the last mouse position

        Returns
        -------
        (int, int)
            The last mouse position.
        """

        return self.mouseX, self.mouseY

    def ImageMousePosition(self):
        """ Get the absolute mouse position

        Returns
        -------
        (int, int)
            The absolute mouse position.
        """

        # If there is no current frame or the
        # window size is invalid, return the
        # regular mouse position
        if self.frame is None or self.previousWidth <= 0 or self.previousHeight <= 0:
            return self.MousePosition()

        return (self.mouseX - self.imageOffsetX) / self.scale, \
               (self.mouseY - self.imageOffsetY) / self.scale

    def ImageToScreenPosition(self, x, y):
        """
        Convert an absolute image position to a screen position

        Parameters
        ----------
        x : int
            The x position
        y : int
            The y position

        Returns
        -------
        int, int
            The screen position
        """
        return (x * self.scale) + self.imageOffsetX, \
               (y * self.scale) + self.imageOffsetY

    def MouseClick(self, event, x, y):
        """ Handle a mouse click.

        Parameters
        ----------
        event : int
            The event type.
        x : int
            The x position of the mouse.
        y : int
            The y position of the mouse.
        """

        if event == pygame.MOUSEBUTTONDOWN:
            self.pressed = True
            self.mouseX, self.mouseY = x, y
            self.aMouseX, self.aMouseY = self.ImageMousePosition()

    def ShowFrame(self, frame):
        """ Show a frame in the window.

        Parameters
        ----------
        frame : pygame.Surface or np.ndarray
            The frame to show.
        """

        # Set image property;
        # Check if the image is an OpenCV image
        if isinstance(frame, pygame.Surface):
            self.frame = frame
        else:
            self.frame = Rendering.ConvertOpenCVImageToPyGameImage(frame)

        # Set invalidated
        self.invalidated = True

    def SetShowPressed(self, showPressed: bool):
        self.showPressed = showPressed

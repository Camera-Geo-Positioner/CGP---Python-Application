# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software Project course.
# © Copyright Utrecht University (Department of Information and Computing Sciences)

"""
Implementation of the ISubWindow.
Handles the window used by the calibration for the primitive input.
"""
from typing import Tuple, Any

import numpy as np
import pygame
import pygame_gui
from Calibrator.Input.PrimitiveInput import PrimitiveInput
from IO import Pathing
from Windowing.MasterWindow import MasterWindow
from Windowing.Rendering import Rendering
from Windowing.Sub.ISubWindow import ISubWindow


class PrimitiveInputSubWindow(ISubWindow):
    primitiveInput: PrimitiveInput = None

    guiManager: pygame_gui.UIManager = None
    confirmButton: pygame_gui.elements.ui_button.UIButton = None

    zoomScale = 7
    zoomRectangleSize = (200, 200)

    invalidatedPartially = True
    resized = False
    previousSurface: pygame.Surface = None
    holdingMouse = False
    hideMenu = False

    def __init__(self, image, title="Primitive Invoer Venster"):
        """ Initializes a primitive input window, based on the given image.

        Parameters
        ----------
        image : pygame.Surface or np.ndarray
            The image that will be displayed in the window, preferably a pygame.Surface
        title : str
            The title of the window.
        """

        # Make sure we are dealing with a pygame surface
        if not isinstance(image, pygame.Surface):
            self.image = Rendering.ConvertOpenCVImageToPyGameImage(image)
        else:
            self.image = image

        # Create new primitive input
        self.primitiveInput = PrimitiveInput(self.image, self)

        # Set properties
        def handleMouseCallback(event, mouseX, mouseY):
            if self.previousWidth == 0 or self.previousHeight == 0:
                return

            # Calculate relative mouse position
            scaledImageDrawingPoint = self.GetScaledImageDrawingPoint()
            scaledImageSize = self.GetScaledImageSize()

            # Calculate relative mouse position
            relativeMouseX = (mouseX - scaledImageDrawingPoint[0]) / scaledImageSize[0]
            relativeMouseY = (mouseY - scaledImageDrawingPoint[1]) / scaledImageSize[1]

            # Clamp relative mouse position to not exceed image boundaries
            relativeMouseX = np.clip(relativeMouseX, 0.0, 1.0)
            relativeMouseY = np.clip(relativeMouseY, 0.0, 1.0)

            # Let primitive input handle mouse input
            self.primitiveInput.MouseCallback(event, relativeMouseX, relativeMouseY)
            if self.primitiveInput.invalidated:
                self.invalidated = True
                self.invalidatedPartially = False
                self.primitiveInput.invalidated = False

        def handleKeyCallback(event, key):
            self.primitiveInput.KeyCallback(event, key)
            if self.primitiveInput.invalidated:
                self.invalidated = True
                self.invalidatedPartially = False
                self.primitiveInput.invalidated = False

        self.SetMouseCallback(handleMouseCallback)
        self.SetKeyCallback(handleKeyCallback)

        # Call super constructor
        super(PrimitiveInputSubWindow, self).__init__(title, "Windowing/Assets/Icons/primitive-input.png")

    def RequestPrimitivesInput(self, primitives):
        """ Requests the primitive input.

        Parameters
        ----------
        primitives : list
            The list of primitives that should be handled
        """

        # Set properties
        self.primitiveInput.RequestPrimitives(primitives)

        # Invalidate
        self.invalidated = True
        self.invalidatedPartially = False

    def GetPrimitiveResults(self) -> Tuple[Any, Any]:
        """ Returns the primitive results.

        Returns
        -------
        bool
            True if the primitive input has finished, False otherwise.
        [PrimitiveInputResult]
            The primitive results.
        """

        # Return primitive results
        return self.primitiveInput.finished, self.primitiveInput.results

    def HandleInput(self, events: [pygame.event]):  # pragma: no cover
        """ Handles the input of the window.

        Parameters
        ----------
        events : [pygame.event]
            The events that are being handled.
        """

        for event in events:
            # If the window was resized, invalidate fully
            if event.type == pygame.WINDOWRESIZED:
                self.resized = True
                self.invalidated = True
                self.invalidatedPartially = False

            # If the mouse button is being held down, set holding mouse to true
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.holdingMouse = True

            # If the mouse is being moved and the mouse is being held down,
            # hide the menu
            if event.type == pygame.MOUSEMOTION and self.holdingMouse:
                self.hideMenu = True

            # If the mouse button was released, show menu
            if event.type == pygame.MOUSEBUTTONUP:
                self.holdingMouse = False
                self.hideMenu = False

        if self.guiManager is not None:
            # For all events, handle GUI events
            for event in events:
                # If a button was clicked, check which option was pressed
                if event.type == pygame_gui.UI_BUTTON_PRESSED:
                    # Confirm button
                    if event.ui_element == self.confirmButton:
                        # Advance to the next primitive
                        self.primitiveInput.NextPrimitive()

                        # If possible, make sure to do the same for the sibling
                        if self.primitiveInput.sibling is not None:
                            self.primitiveInput.sibling.NextPrimitive()

                # Let the GUI manager handle the event
                self.guiManager.process_events(event)

        super(PrimitiveInputSubWindow, self).HandleInput(events)

    def Update(self, deltaTime):  # pragma: no cover
        """ Update the camera sub window.

        Parameters
        ----------
        deltaTime : float
            The time between the last frame and the current frame.
        """
        # Update GUI manager if possible
        if self.guiManager is not None:
            # Update GUI manager
            self.guiManager.update(deltaTime)

            # Always invalidate
            self.invalidated = True

        # Failsafe, make sure at least one primitive input has menu GUI
        if self.guiManager is None:
            if self.primitiveInput.sibling is None:
                raise Exception("Primitive input has no sibling, but no GUI manager was provided.")

        # TODO: If primitive input has sibling, check if the sibling has menu GUI - but there
        #       is no direct access to the sibling's window.

        # If primitive input was invalidated, invalidate fully
        if self.primitiveInput.invalidated:
            self.invalidated = True
            self.invalidatedPartially = False
            self.primitiveInput.invalidated = False

        super(PrimitiveInputSubWindow, self).Update(deltaTime)

    def Render(self, width: int, height: int) -> pygame.Surface:  # pragma: no cover
        """ Renders the primitive input window.

        Parameters
        ----------
        width : int
            The width of the window.
        height : int
            The height of the window.

        Returns
        -------
        pygame.Surface
            The rendered surface.
        """

        # Check if invalidated partially or fully
        if not self.invalidatedPartially or self.previousSurface is None:
            # Restore invalidated partially
            self.invalidatedPartially = True

            # Create surface
            surface = super(PrimitiveInputSubWindow, self).Render(width, height)

            # Get scaled image size and drawing position
            scaledImageSize = self.GetScaledImageSize()
            scaledImageDrawingPoint = self.GetScaledImageDrawingPoint()

            # Draw scaled image
            surface.blit(
                pygame.transform.scale(self.image, scaledImageSize),
                scaledImageDrawingPoint
            )

            # Draw current primitive
            if self.primitiveInput.currentPrimitive is not None:
                self.primitiveInput.currentPrimitive.Render(
                    surface,
                    scaledImageDrawingPoint[0], scaledImageDrawingPoint[1],
                    scaledImageSize[0], scaledImageSize[1],
                    self.primitiveInput.renderScaled
                )

            # Primitive movement specific render calls
            if self.primitiveInput.currentPrimitive.movePointIndex is not None:
                # Draw lines between primitive points, if necessary
                if self.primitiveInput.sibling is not None:
                    self._RenderPointConnection(surface, self.primitiveInput.currentPrimitive.movePointIndex)

                # Draw zoom box/pixel peeper
                self._RenderZoomRectangle(surface)

            elif self.primitiveInput.sibling is not None and \
                    self.primitiveInput.sibling.currentPrimitive.movePointIndex is not None:
                # Draw lines between primitive points, if necessary
                self._RenderPointConnection(surface, self.primitiveInput.sibling.currentPrimitive.movePointIndex)

            # Return surface result
            self.previousSurface = surface

        return self._RenderGUI()

    def GetScaledImageSize(self):
        """ Returns the scaled image size.

        Returns
        -------
        tuple
            The scaled image size.
        """

        # Calculate aspect ratio of image
        aspectRatio = self.image.get_width() / self.image.get_height()

        # Adjust image size to fit in window
        if self.previousWidth / self.previousHeight <= aspectRatio:
            # Calculate adjusted height
            adjustedHeight = self.previousWidth / aspectRatio

            return int(self.previousWidth), int(adjustedHeight)
        else:
            # Calculate adjusted width
            adjustedWidth = self.previousHeight * aspectRatio

            return int(adjustedWidth), int(self.previousHeight)

    def GetScaledImageDrawingPoint(self):
        """ Returns the scaled image drawing point.

        Returns
        -------
        tuple
            The scaled image drawing point.
        """

        # Calculate aspect ratio of image
        aspectRatio = self.image.get_width() / self.image.get_height()

        # Adjust image size to fit in window
        if self.previousWidth != 0 and \
                self.previousWidth / self.previousHeight <= aspectRatio:
            # Calculate adjusted height
            adjustedHeight = self.previousWidth / aspectRatio

            return 0, int(self.previousHeight / 2 - adjustedHeight / 2)
        else:
            # Calculate adjusted width
            adjustedWidth = self.previousHeight * aspectRatio

            return int(self.previousWidth / 2 - adjustedWidth / 2), 0

    def CreateMenuGUI(self):  # pragma: no cover
        """ Creates the menu GUI, necessary for closing or finishing the primitive input. """
        # Create the GUI manager
        if self.guiManager is None:
            self.guiManager = pygame_gui.ui_manager.UIManager(
                window_resolution=(MasterWindow.instance.width, MasterWindow.instance.height),
                theme_path=str(Pathing.AssureAbsolutePath("Windowing/Assets/Themes/default_theme.json"))
            )
        else:
            self.guiManager.set_window_resolution((self.previousWidth, self.previousHeight))

        # If the previous sizes are invalid, set resized flag to True
        # and ignore creating the menu GUI
        if self.previousWidth == -1 and self.previousHeight == -1:
            self.resized = True
            return

        # Constants
        buttonHeight = 40
        buttonWidth = 120

        # Confirm button
        if self.confirmButton is not None:
            self.confirmButton.kill()
        self.confirmButton = pygame_gui.elements.ui_button.UIButton(
            relative_rect=pygame.Rect(
                (self.previousWidth / 2 - buttonWidth / 2, self.previousHeight - buttonHeight),
                (buttonWidth, buttonHeight)
            ),
            text="Doorgaan",
            manager=self.guiManager
        )

        # Overwrite GUI manager scaled mouse position
        # to make it relative to the sub window
        self.guiManager.calculate_scaled_mouse_position = lambda pos: (
            int(self.guiManager.mouse_pos_scale_factor[0] * self.previousMouseX),
            int(self.guiManager.mouse_pos_scale_factor[1] * self.previousMouseY)
        )

        # Set invalidated
        self.invalidated = True
        self.invalidatedPartially = False

    def _RenderGUI(self) -> pygame.Surface:
        """
        Renders the GUI to the previously rendered whole.
        """
        surface = self.previousSurface.copy()
        if self.guiManager is not None and not self.hideMenu:
            # Recreate the menu GUI if dimensions have changed
            if self.resized:
                self.resized = False
                self.CreateMenuGUI()

            # Render the GUI
            self.guiManager.draw_ui(surface)
        return surface

    def _RenderPointConnection(self, surface, movePointIndex):  # pragma: no cover
        """
        Renders a line from the current primitive point to the sibling primitive point.
        This assumes that the sibling primitive is not None.

        Parameters
        ----------
        surface : pygame.Surface
            The surface to draw on.
        """

        # Make sure the sibling primitive is not None
        if self.primitiveInput.sibling is not None:
            # Get the current primitive point
            currentSize = self.GetScaledImageSize()
            currentOffset = self.GetScaledImageDrawingPoint()
            currentPoint = self.primitiveInput.currentPrimitive.GetAbsolutePoint(
                movePointIndex,
                currentSize[0],
                currentSize[1]
            )

            # Get the sibling primitive point
            siblingSize = self.primitiveInput.sibling.parent.GetScaledImageSize()
            siblingOffset = self.primitiveInput.sibling.parent.GetScaledImageDrawingPoint()
            siblingPoint = self.primitiveInput.sibling.currentPrimitive.GetAbsolutePoint(
                movePointIndex,
                siblingSize[0],
                siblingSize[1]
            )

            # We need to know if we are on the left or right side of the sibling primitive
            left = MasterWindow.instance.leftSubWindow is self
            offset = currentSize[0] if left else -siblingSize[0]

            # Render the line
            Rendering.RenderLine(
                surface,
                currentOffset[0] + currentPoint[0], currentOffset[1] + currentPoint[1],
                offset + siblingOffset[0] + siblingPoint[0], siblingOffset[1] + siblingPoint[1],
                (255, 255, 255, 185),
                3
            )

            # Call invalidate
            self.primitiveInput.sibling.invalidated = True

    def _RenderZoomRectangle(self, surface):  # pragma: no cover
        """
        Renders the zoom rectangle, also the sibling
        zoom rectangle if the primitive input has a sibling.

        Parameters
        ----------
        surface : pygame.Surface
            The surface to render to.
        """

        def render(image, center, position, text=None):
            # Create clipped and zoomed rectangle of the image
            zoomRectangleSurface = PrimitiveInputSubWindow._ClipZoomRectangle(
                image,
                center,
                self.zoomRectangleSize,
                self.zoomScale
            )

            # Render crosshair in the middle of the clipped zoom rectangle
            rectangleCenter = (
                self.zoomRectangleSize[0] // 2 + self.zoomRectangleSize[0] % self.zoomScale,
                self.zoomRectangleSize[1] // 2 + self.zoomRectangleSize[1] % self.zoomScale
            )
            Rendering.RenderCrosshair(zoomRectangleSurface, rectangleCenter[0], rectangleCenter[1])

            # Render coordinate
            Rendering.RenderText(
                zoomRectangleSurface,
                "({0}, {1})".format(center[0], center[1]),
                10,
                rectangleCenter[1] + self.zoomRectangleSize[1] / 2 - 24,
                Rendering.FontSize.Small
            )

            # Render point index and possible text
            if text is None:
                text = "#{0}".format(self.primitiveInput.currentPrimitive.movePointIndex)
            else:
                text += ": #{0}".format(self.primitiveInput.currentPrimitive.movePointIndex)
            Rendering.RenderText(
                zoomRectangleSurface,
                text,
                12,
                rectangleCenter[1] - self.zoomRectangleSize[1] / 2 + 2,
                Rendering.FontSize.Medium
            )

            # Render to the top right of the screen
            surface.blit(
                zoomRectangleSurface,
                position
            )

        # Get the scaled image size
        scaledImageSize = self.GetScaledImageSize()

        # set the y pos based on mouse, so that the zoom rectangle is not in the way

        if self.previousMouseY > self.previousHeight / 2:
            yPos = 0
        else:
            yPos = self.previousHeight - self.zoomRectangleSize[1]

        # If the primitive input has no sibling, only draw
        # the zoom rectangle for this primitive input
        if self.primitiveInput.sibling is None:
            p1 = self.primitiveInput.currentPrimitive.GetAbsolutePoint(
                self.primitiveInput.currentPrimitive.movePointIndex,
                self.image.get_width(),
                self.image.get_height()
            )
            render(self.image, p1, (0, yPos))

        # Render the primitive input zoom rectangle, and
        # the zoom rectangle of the sibling's same primitive
        else:

            p1 = self.primitiveInput.currentPrimitive.GetAbsolutePoint(
                self.primitiveInput.currentPrimitive.movePointIndex,
                self.image.get_width(),
                self.image.get_height()
            )
            p2 = self.primitiveInput.sibling.currentPrimitive.GetAbsolutePoint(
                self.primitiveInput.currentPrimitive.movePointIndex,
                self.primitiveInput.sibling.image.get_width(),
                self.primitiveInput.sibling.image.get_height()
            )
            if MasterWindow.instance.leftSubWindow is self:
                render(
                    self.primitiveInput.sibling.image,
                    p2,
                    (self.zoomRectangleSize[0], yPos),
                    "Ander venster"
                )
                render(
                    self.image,
                    p1,
                    (0, yPos),
                    self.title
                )
            else:
                render(
                    self.image,
                    p1,
                    (self.zoomRectangleSize[0], yPos),
                    self.title
                )
                render(
                    self.primitiveInput.sibling.image,
                    p2,
                    (0, yPos),
                    "Ander venster"
                )

    @staticmethod
    def _ClipZoomRectangle(
            image: any, center: (int, int), size: (int, int), scale: int
    ) -> pygame.Surface:  # pragma: no cover
        """ Clips the zoom rectangle from the image to a new surface.

        Parameters
        ----------
        image : any
            The image to clip and zoom.
        center : (int, int)
            The center of the zoom rectangle.
        size : (int, int)
            The size of the zoom rectangle.
        scale : int
            The scale of the zoom rectangle.

        Returns
        -------
        pygame.Surface
            The clipped zoom rectangle surface.
        """

        # Scale down the size
        actualSize = (
            size[0] // scale,
            size[1] // scale
        )

        # Create new surface
        zoomRectangleSurface = pygame.Surface(actualSize)

        # Copy zoom rectangle from image to new surface
        zoomRectangleSurface.blit(
            image,
            (0, 0),
            (
                (center[0] - actualSize[0] // 2),
                (center[1] - actualSize[1] // 2),
                actualSize[0],
                actualSize[1]
            )
        )

        # Scale up the surface to the intended size
        zoomRectangleSurface = pygame.transform.scale(
            zoomRectangleSurface,
            size,
        )

        # Return surface result
        return zoomRectangleSurface

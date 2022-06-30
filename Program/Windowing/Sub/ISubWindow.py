# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software Project course.
# © Copyright Utrecht University (Department of Information and Computing Sciences)

from abc import ABC, abstractmethod
import pygame
from pygame import KEYDOWN, KEYUP
from IO import Pathing


SUB_WINDOW_CLEAR_COLOR = (22, 22, 22)


class ISubWindow(ABC):
    """
    This class is an interface for the SubWindow class.
    """
    title: str = "Sub Window"
    icon: pygame.Surface = None
    invalidated: bool = True   # Always invalidate the sub window when it is created.
    keyCallback: any = None
    mouseCallback: any = None
    previousMouseX: int = -1   # The previous mouse X position.
    previousMouseY: int = -1   # The previous mouse Y position.
    previousWidth: int = -1    # The previous width is necessary for some implementations.
    previousHeight: int = -1   # The previous height is necessary for some implementations.
    imageOffsetX: float = 0    # The previous offset in x of the actual image by a black border.
    imageOffsetY: float = 0    # The previous offset in y of the actual image by a black border.

    def __init__(self, title, iconPath=""):
        """
        Initializes the sub window.

        Parameters
        ----------
        title : str
            The title of the sub window.
        iconPath: str
            The optional path to an icon image file.
        """
        self.title = title

        # Attempt to load icon
        try:
            # Defer to default if no icon path was specified
            if iconPath == "":
                iconPath = "Windowing/Assets/Icons/default.png"

            # Load icon
            self.icon = pygame.image.load(str(Pathing.AssureAbsolutePath(iconPath)))

            # Convert if possible
            if pygame.get_init() and pygame.display.get_init():
                self.icon = self.icon.convert_alpha()
        except:
            print("Could not load icon from \"" + iconPath + "\"!")

    def SetKeyCallback(self, callback):
        """ Sets the key callback.

        Parameters
        ----------
        callback : function
            The callback function.
        """

        self.keyCallback = callback

    def SetMouseCallback(self, callback):
        """ Sets the mouse callback.

        Parameters
        ----------
        callback : function
            The callback function.
        """

        self.mouseCallback = callback

    @abstractmethod
    def Update(self, deltaTime):  # pragma: no cover
        """
        Updates the sub window.

        Parameters
        ----------
        deltaTime : float
            The time since the last frame.
        """

        pass

    @abstractmethod
    def Render(self, width, height) -> pygame.Surface:  # pragma: no cover
        """
        Renders the sub window.

        Parameters
        ----------
        width : int
            The width of the sub window.
        height : int
            The height of the sub window.

        Returns
        -------
        pygame.Surface
            The rendered sub window.
        """

        # Set previous width and height.
        self.previousWidth = width
        self.previousHeight = height

        # Create an empty surface and return it.
        surface = pygame.Surface((width, height))
        surface.fill(SUB_WINDOW_CLEAR_COLOR)
        return surface

    def HandleInput(self, events: [pygame.event]):  # pragma: no cover
        """
        Handles the input of the sub window.

        Parameters
        ----------
        events : [pygame.event]
            The events that are currently being handled.
        """

        for event in events:
            # Did the user hit a key?
            if event.type == KEYDOWN:
                # Call key callback, if it exists
                if self.keyCallback is not None:
                    self.keyCallback(KEYDOWN, event.key)
            # Did the user release a key?
            elif event.type == KEYUP:
                # Call key callback, if it exists
                if self.keyCallback is not None:
                    self.keyCallback(KEYUP, event.key)

            # Did the user use the mouse? If so, call mouse callback if it exists.
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                self.previousMouseX, self.previousMouseY = x, y
                if self.mouseCallback is not None:
                    self.mouseCallback(pygame.MOUSEBUTTONDOWN, x, y)
            elif event.type == pygame.MOUSEBUTTONUP:
                x, y = event.pos
                self.previousMouseX, self.previousMouseY = x, y
                if self.mouseCallback is not None:
                    self.mouseCallback(pygame.MOUSEBUTTONUP, x, y)
            elif event.type == pygame.MOUSEMOTION:
                x, y = event.pos
                self.previousMouseX, self.previousMouseY = x, y
                if self.mouseCallback is not None:
                    self.mouseCallback(pygame.MOUSEMOTION, x, y)

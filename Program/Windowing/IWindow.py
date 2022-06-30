# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software Project course.
# © Copyright Utrecht University (Department of Information and Computing Sciences)

"""
Interface for different windowing objects.
"""

import threading
from abc import ABC, abstractmethod
import pygame
from pygame import K_ESCAPE, QUIT, KEYDOWN, KEYUP, DOUBLEBUF, RESIZABLE, MOUSEBUTTONDOWN, MOUSEMOTION, MOUSEBUTTONUP, \
    WINDOWRESIZED, VIDEORESIZE
from IO import Pathing
from Windowing.Rendering import Rendering


class IWindow(ABC):     # pragma: no cover
    """ This class is used to create a window, using PyGame. """
    width: int = 0
    height: int = 0
    title: str = ""
    clock: pygame.time.Clock = None
    targetFrameRate: int = 60

    invalidated: bool = False
    running: bool = False

    runningThread: threading.Thread = None

    window = None
    backgroundImageSmall = None
    backgroundImageFull = None

    def __init__(self, width, height, title):
        """ Create a window.

        Parameters
        ----------
        width : int
            The width of the window.
        height : int
            The height of the window.
        title : str
            The title of the window.
        """

        self.window = None

        # Set properties
        self.width = width
        self.height = height
        self.title = title

        self.mouseCallback = None
        self.keyCallback = None

        self.events = []
        self.clock = pygame.time.Clock()

        self.invalidated = False
        self.running = 0  # Integer instead of boolean, faster performance in while loop
        self.runningThread = None

    def Open(self, inThread: bool = False, onCloseEvent: threading.Event = None):
        """
        Opens a pygame window.

        Parameters
        ----------
        inThread : bool
            If `True`, opens the window in a separate thread.
        onCloseEvent : threading.Event
            Threading event that is triggerd when the window is closed.
        """
        if self.running:
            return

        # Variable to keep the main loop running
        self.invalidated = True
        self.running = 1

        if inThread:
            self.runningThread = threading.Thread(target=self._RunWindow, args=[onCloseEvent])
            self.runningThread.daemon = True
            self.runningThread.start()
        else:
            self._RunWindow(onCloseEvent)

    def Close(self):
        """ Closes the window. """

        self.running = 0
        if self.runningThread is not None:
            self.runningThread.join()
            self.runningThread = None

    def _RunWindow(self, onCloseEvent: threading.Event):
        """
        Function that creates and runs the actual window, can be started as thread.

        Parameters
        ----------
        onCloseEvent : threading.Event
            Threading event that is triggered when the window is closed.
        """

        # Create pygame window
        pygame.init()
        self.window = pygame.display.set_mode(
            (self.width, self.height),
            RESIZABLE | DOUBLEBUF,
            16
        )
        pygame.display.set_caption(self.title)

        # Limit pygame events
        pygame.event.set_allowed([
            QUIT,
            KEYDOWN, KEYUP,
            MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION,
            WINDOWRESIZED, VIDEORESIZE
        ])

        # Load images
        try:
            self.backgroundImageSmall = pygame.image.load(
                str(Pathing.AssureAbsolutePath('Windowing/Assets/WatchfulEye_Small.png'))
            ).convert_alpha()
            self.backgroundImageFull = pygame.image.load(
                str(Pathing.AssureAbsolutePath('Windowing/Assets/WatchfulEye_Full.png'))
            ).convert_alpha()
        except:
            raise Exception('Could not load background image(s).')

        # Set icon (we assume the small background image)
        pygame.display.set_icon(self.backgroundImageSmall)

        # Run window
        while self.running:
            deltaTime = self.clock.tick(self.targetFrameRate) / 1000.0  # Sleeps and gets delta time
            self.Update(deltaTime)

        # Cleanup
        pygame.display.quit()
        pygame.quit()
        if onCloseEvent is not None:
            onCloseEvent.set()

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
    def Update(self, deltaTime: float):
        """ Update the window. """

        # Look at every event in the queue
        self.events = pygame.event.get()
        for event in self.events:
            # Did the user hit a key?
            if event.type == KEYDOWN:
                # Was it the Escape key? If so, stop running.
                if event.key == K_ESCAPE:
                    self.running = False
                # Otherwise, call key callback, if it exists
                elif self.keyCallback is not None:
                    self.keyCallback(KEYDOWN, event.key)
            # Did the user release a key?
            elif event.type == KEYUP:
                # Call key callback, if it exists
                if self.keyCallback is not None:
                    self.keyCallback(KEYUP, event.key)

            # Did the user use the mouse? If so, call mouse callback if it exists.
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.mouseCallback is not None:
                    x, y = event.pos
                    self.mouseCallback(pygame.MOUSEBUTTONDOWN, x, y)
            elif event.type == pygame.MOUSEBUTTONUP:
                if self.mouseCallback is not None:
                    x, y = event.pos
                    self.mouseCallback(pygame.MOUSEBUTTONUP, x, y)
            elif event.type == pygame.MOUSEMOTION:
                if self.mouseCallback is not None:
                    x, y = event.pos
                    self.mouseCallback(pygame.MOUSEMOTION, x, y)

            # Did the user click the window close button? If so, stop the loop.
            if event.type == QUIT:
                self.running = False

            # Did the user resize the window?
            if event.type == pygame.VIDEORESIZE:
                self.width = event.w
                self.height = event.h
                self.invalidated = True

        # If invalidated, clear and render the window
        if self.invalidated:
            # Get the window size
            width, height = pygame.display.get_surface().get_size()

            # Create surface
            surface = pygame.Surface((width, height))

            # Draw background image, scaled to the window
            if self.backgroundImageSmall is not None and self.backgroundImageFull is not None:
                backgroundFullSize = (700, 105)
                backgroundSmallSize = (165, 105)
                cutoffFactor = .75
                if width * cutoffFactor >= backgroundFullSize[0] and height * cutoffFactor >= backgroundFullSize[1]:
                    surface.blit(
                        pygame.transform.smoothscale(self.backgroundImageFull, backgroundFullSize),
                        (width / 2 - backgroundFullSize[0] / 2, height / 2 - backgroundFullSize[1] / 2)
                    )
                else:
                    surface.blit(
                        pygame.transform.smoothscale(self.backgroundImageSmall, backgroundSmallSize),
                        (width / 2 - backgroundSmallSize[0] / 2, height / 2 - backgroundSmallSize[1] / 2)
                    )

            # Render the surface and flip surface to the window
            self.Render(surface)

            # Reset invalidated flag
            self.invalidated = False

    @abstractmethod
    def Render(self, surface):  # pragma: no cover
        """ Renders the surface to the window.

        Parameters
        ----------
        surface : pygame.Surface
            The surface to render.
        """

        # If not invalidated, ignore
        if not self.invalidated:
            return

        # Draw copyright notice
        Rendering.RenderText(
            surface=surface,
            text="© Utrecht University (ICS)",
            x=surface.get_width() - 8, y=5,
            fontSize=Rendering.FontSize.Mini,
            textAlignment=Rendering.TextAlignment.TopRight,
            shadowOffset=0  # No shadow
        )

        # Blit the surface to the window
        self.window.blit(surface, (0, 0))

        # Flip the window
        pygame.display.update()

    @staticmethod
    def TakeScreenShot():
        return pygame.display.get_surface()

# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software Project course.
# © Copyright Utrecht University (Department of Information and Computing Sciences)

from enum import Enum
from types import SimpleNamespace

import pygame.mouse
import pygame_gui
from pygame import MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION
from pygame.event import Event
from Windowing.IWindow import IWindow
from Windowing.Rendering import Rendering
from Windowing.Sub import ISubWindow

# Constants

# The height/size of headers of sub-windows in the master window
MASTER_WINDOW_HEADER_SIZE = 24

# The coloring of the header of sub-windows in the master window
MASTER_WINDOW_HEADER_FOREGROUND_COLOR = (255, 255, 255, 255)
MASTER_WINDOW_HEADER_BACKGROUND_COLOR = (50, 50, 50, 255)
MASTER_WINDOW_HEADER_BORDER_COLOR = (75, 75, 75, 255)


class SubWindowPosition(Enum):
    """
    This class is used to determine the position of a sub window.
    """
    Left = 0,
    Right = 1,


class MasterWindow(IWindow):
    """
    This class is the master window. It is the window that contains two possible sub windows.
    """
    instance: 'MasterWindow' = None
    previousWidth: int = -1
    previousHeight: int = -1

    leftSubWindow: ISubWindow = None
    rightSubWindow: ISubWindow = None

    leftSubWindowFocussed: bool = False
    rightSubWindowFocussed: bool = False

    leftSubWindowHeaderSurface: pygame.Surface = None
    rightSubWindowHeaderSurface: pygame.Surface = None

    def __init__(self, width, height, title):
        """
        Initialize the master window.

        Parameters
        ----------
        width : int
            The width of the master window.
        height : int
            The height of the master window.
        title : str
            The title of the master window.
        """

        # Call super
        super(MasterWindow, self).__init__(width, height, title)

        # Check if singleton
        if MasterWindow.instance is not None:
            raise Exception("Master window already exists")

        # Set previous width and height
        self.previousWidth = width
        self.previousHeight = height

        # Set instance
        MasterWindow.instance = self
        MasterWindow.invalidated = True

    def AppendSubWindow(self, subWindow: ISubWindow, position: SubWindowPosition):
        """
        Append a sub window to the master window.

        Parameters
        ----------
        subWindow : ISubWindow
            The sub window to append.
        position : SubWindowPosition
            The position of the sub window.
        """

        if position == SubWindowPosition.Left:
            self.leftSubWindow = subWindow
            self.leftSubWindowHeaderSurface = None
            self.leftSubWindow.invalidated = True
        elif position == SubWindowPosition.Right:
            self.rightSubWindow = subWindow
            self.rightSubWindowHeaderSurface = None
            self.rightSubWindow.invalidated = True

        self.invalidated = True
        self.leftSubWindowFocussed = False
        self.rightSubWindowFocussed = False

    def RemoveSubWindow(self, position: SubWindowPosition):
        """
        Remove a sub window from the master window, if it exists

        Parameters
        ----------
        position : SubWindowPosition
            The position of the sub window to remove.
        """
        if position == SubWindowPosition.Left:
            self.leftSubWindow = None
            self.leftSubWindowHeaderSurface = None
        elif position == SubWindowPosition.Right:
            self.rightSubWindow = None
            self.rightSubWindowHeaderSurface = None

        if self.leftSubWindow is None and self.rightSubWindow is None:
            self.invalidated = False
        else:
            self.invalidated = True

        self.leftSubWindowFocussed = False
        self.rightSubWindowFocussed = False

    def Close(self):
        """
        Close the master window.
        """

        # Call super
        super(MasterWindow, self).Close()

        # Set instance to None
        MasterWindow.instance = None

    def Update(self, deltaTime: float):
        """
        Update the sub windows.
        """

        # Check if the width or height of the master window has changed
        if (self.previousWidth != -1 and self.previousWidth != self.width) or \
           (self.previousHeight != -1 and self.previousHeight != self.height):
            self.previousWidth = self.width
            self.previousHeight = self.height

            # Reset rendered header surfaces
            self.leftSubWindowHeaderSurface = None
            self.rightSubWindowHeaderSurface = None
            self.invalidated = True

        # Call super, needs to be done after possible invalidation for immediate rendering
        # but also to grab the list of current events
        super(MasterWindow, self).Update(deltaTime)

        # If no sub-windows are present, we do not have to handle
        # any events further
        if self.leftSubWindow is None and self.rightSubWindow is None:
            return

        # Get the stripped events
        leftSubWindowEvents, rightSubWindowEvents = self._GetStrippedEvents()

        # Check sub window focus, this is used to make sure that
        # resetting events are compensated for when switching focus
        # between sub-windows

        # Check if left sub-window currently has the focus (present events)
        if len(leftSubWindowEvents) > 0 and len(rightSubWindowEvents) is 0:
            # If the right sub-window was previously focussed, send mouse up event
            # for resetting purposes
            if self.rightSubWindowFocussed:
                x, y = pygame.mouse.get_pos()
                self.rightSubWindowFocussed = False
                rightSubWindowEvents.append(SimpleNamespace(**{
                    "type": MOUSEBUTTONUP,
                    "pos": (
                        x - self._CalculateSeperatorOffset(),
                        y
                    ),
                    "button": None
                }))

            # Focus left sub-window
            self.leftSubWindowFocussed = True

        # Check if right sub-window currently has the focus (present events)
        elif len(rightSubWindowEvents) > 0 and len(leftSubWindowEvents) is 0:
            # If the left sub-window was previously focussed, send mouse up event
            # for resetting purposes
            if self.leftSubWindowFocussed:
                x, y = pygame.mouse.get_pos()
                self.leftSubWindowFocussed = False
                leftSubWindowEvents.append(SimpleNamespace(**{
                    "type": MOUSEBUTTONUP,
                    "pos": (
                        x,
                        y
                    ),
                    "button": None
                }))

            # Focus right sub-window
            self.rightSubWindowFocussed = True

        # If the left sub window is not None, update it
        # and handle events
        if self.leftSubWindow is not None:
            self.leftSubWindow.Update(deltaTime)
            self.leftSubWindow.HandleInput(leftSubWindowEvents)

            # Check if the left sub window is invalidated.
            if self.leftSubWindow.invalidated:
                # Set master window to invalidated, this
                # will ask for a render pass
                self.invalidated = True

        # If the right sub window is not None, update it
        # and handle events
        if self.rightSubWindow is not None:
            self.rightSubWindow.Update(deltaTime)
            self.rightSubWindow.HandleInput(rightSubWindowEvents)

            # Check if the right sub window is invalidated.
            if self.rightSubWindow.invalidated:
                # Set master window to invalidated, this
                # will ask for a render pass
                self.invalidated = True

    def Render(self, surface):  # pragma: no cover
        """
        Render the Master Window.

        Parameters
        ----------
        surface : pygame.Surface
            The surface to render on.
        """

        # Calculate seperator offset
        seperatorOffset = self._CalculateSeperatorOffset()

        # Setup inline rendering method, for rendering
        # onto surfaces with a header
        def renderSubWindow(subWindowPosition, subWindow):
            # Check if the header surface has already been rendered once
            headerSurface = None
            if subWindowPosition == SubWindowPosition.Left:
                # Render the left sub-window header surface if necessary
                if self.leftSubWindowHeaderSurface is None:
                    self.leftSubWindowHeaderSurface = MasterWindow.CreateSurfaceWithHeader(
                        subWindow.title,
                        subWindow.icon,
                        MASTER_WINDOW_HEADER_SIZE,
                        self.width - seperatorOffset,
                        self.height
                    )
                headerSurface = self.leftSubWindowHeaderSurface
            elif subWindowPosition == SubWindowPosition.Right:
                # Render the right sub-window header surface if necessary
                if self.rightSubWindowHeaderSurface is None:
                    self.rightSubWindowHeaderSurface = MasterWindow.CreateSurfaceWithHeader(
                        subWindow.title,
                        subWindow.icon,
                        MASTER_WINDOW_HEADER_SIZE,
                        self.width - seperatorOffset,
                        self.height
                    )
                headerSurface = self.rightSubWindowHeaderSurface

            # Render the sub window
            subWindowSurface = subWindow.Render(
                self.width - seperatorOffset,
                self.height - MASTER_WINDOW_HEADER_SIZE
            )

            # Blit the left sub window surface to the header surface
            headerSurface.blit(
                subWindowSurface,
                (0, MASTER_WINDOW_HEADER_SIZE)
            )

            # Blit the header surface to the master window
            surface.blit(
                headerSurface,
                (
                    0 if subWindowPosition is SubWindowPosition.Left else seperatorOffset,
                    0
                )
            )

            # Set the left sub window to not invalidated
            subWindow.invalidated = False

        # If the left sub window is not None and has been
        # invalidated, render it.
        if self.leftSubWindow is not None:
            renderSubWindow(SubWindowPosition.Left, self.leftSubWindow)

        # If the right sub window is not None and has been
        # invalidated, render it.
        if self.rightSubWindow is not None:
            renderSubWindow(SubWindowPosition.Right, self.rightSubWindow)

        # If both windows are present, render seperator line
        if self.leftSubWindow is not None and self.rightSubWindow is not None:
            Rendering.RenderLine(
                surface,
                seperatorOffset, 0,  # Point 1
                seperatorOffset, self.height,  # Point 2
                MASTER_WINDOW_HEADER_BORDER_COLOR,
                1
            )

        # Call the super class render method, this resets the invalidated flag
        super(MasterWindow, self).Render(surface)

    def _CalculateSeperatorOffset(self) -> int:
        """
        Calculates the offset of the seperator.

        Returns
        -------
        int
            The offset of the seperator.
        """

        # Calculate the offset of the seperator, this is only done
        # if both of the sub windows are not None.
        if self.leftSubWindow is not None and self.rightSubWindow is not None:
            return self.width // 2

        # No offset, as there is only one or no sub windows present
        return 0

    def _GetStrippedEvents(self) -> ([Event], [Event]):
        """
        Strips the total window events over the left and right sub-windows respectively.

        Returns
        -------
        ([Event], [Event])
            Tuple containing the left sub-window events and the right sub-windows respectively.
        """

        # Calculate seperator offset
        seperatorOffset = self._CalculateSeperatorOffset()

        # Strip events, if necessary (seperator offset more than zero)
        leftSubWindowEvents = []
        rightSubWindowEvents = []
        if seperatorOffset is not 0:
            # Strip all mouse events
            for event in self.events:
                # Only mouse events need to be stripped
                # according to the seperator offset
                if event.type == MOUSEBUTTONDOWN or \
                   event.type == MOUSEBUTTONUP or \
                   event.type == MOUSEMOTION:
                    # Get the event mouse position
                    x, _ = event.pos

                    # Check if mouse event is for the left
                    # or the right sub-window, based on the
                    # seperator offset
                    if x >= seperatorOffset:
                        # Add event with modified offset to the right sub-window
                        rightSubWindowEvents.append(
                            SimpleNamespace(**{
                                "type": event.type,
                                "pos": (
                                    event.pos[0] - seperatorOffset,
                                    event.pos[1] - MASTER_WINDOW_HEADER_SIZE
                                ),
                                "button": event.button if hasattr(event, "button") else None
                            })
                        )
                    else:
                        # Add event to the left sub-window
                        leftSubWindowEvents.append(
                            SimpleNamespace(**{
                                "type": event.type,
                                "pos": (
                                    event.pos[0],
                                    event.pos[1] - MASTER_WINDOW_HEADER_SIZE
                                ),
                                "button": event.button if hasattr(event, "button") else None
                            })
                        )

                # Other events can be passed through directly
                else:
                    leftSubWindowEvents.append(event)
                    rightSubWindowEvents.append(event)

        # No sub-window separation present, pipe all events directly but
        # make sure to subtract the header size from mouse events
        else:
            for event in self.events:
                # Mouse events need position modification to account
                # for the header offset
                if event.type == MOUSEBUTTONDOWN or \
                   event.type == MOUSEBUTTONUP or \
                   event.type == MOUSEMOTION:
                    # Create modified event
                    modifiedEvent = SimpleNamespace(**{
                        "type": event.type,
                        "pos": (
                            event.pos[0],
                            event.pos[1] - MASTER_WINDOW_HEADER_SIZE
                        ),
                        "button": event.button if hasattr(event, "button") else None
                    })

                    # Pipe modified events
                    leftSubWindowEvents.append(modifiedEvent)
                    rightSubWindowEvents.append(modifiedEvent)

                # Other events can be piped directly
                else:
                    leftSubWindowEvents.append(event)
                    rightSubWindowEvents.append(event)

        return leftSubWindowEvents, rightSubWindowEvents

    @staticmethod
    def CreateSurfaceWithHeader(title, icon, headerSize, width, height) -> pygame.Surface:
        """
        Creates a surface that has a graphical header at the top.

        Parameters
        ---------
        title : string
            The title that should be displayed in the header on the left.
        icon : pygame.Surface
            The icon that should be displayed in the header on the left.
        headerSize : int
            The height/size of the header.
        width : int
            The width of the surface to be created.
        height : int
            The height of the surface to be created.

        Returns
        -------
        pygame.Surface
            The surface which has a graphical header at the top.
        """

        # Create a new surface
        surface = pygame.Surface((width, height))

        # Render a graphical header at the top
        borderSize = 1

        # Border/outer box
        Rendering.RenderBox(
            surface,
            0, 0,
            width, headerSize,
            MASTER_WINDOW_HEADER_BORDER_COLOR,
            0
        )

        # Inner box
        Rendering.RenderBox(
            surface,
            borderSize, borderSize,
            width - borderSize * 2, headerSize - borderSize * 2,
            MASTER_WINDOW_HEADER_BACKGROUND_COLOR,
            1
        )

        # Render the icon
        iconScale = .875
        iconSize = headerSize * iconScale
        iconOffset = (1 - iconScale) / 2 * headerSize
        surface.blit(
            pygame.transform.smoothscale(icon, (iconSize, iconSize)),
            (iconOffset * 4, iconOffset)
        )

        # Render the title
        Rendering.RenderText(
            surface,
            title,
            iconOffset * 8 + iconSize,
            headerSize / 2 + 1,
            Rendering.FontSize.Small,
            Rendering.TextAlignment.MiddleLeft,
            MASTER_WINDOW_HEADER_FOREGROUND_COLOR,
            0
        )

        # Return the result
        return surface

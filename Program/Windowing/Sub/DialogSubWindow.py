# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software Project course.
# © Copyright Utrecht University (Department of Information and Computing Sciences)

"""
Implementation of the ISubWindow.
Prompts the user to select a possible option concerning a given description.
"""

import pygame
import pygame_gui

from IO import Pathing
from Windowing.MasterWindow import MasterWindow
from Windowing.Sub.ISubWindow import ISubWindow


class DialogSubWindowOption:
    """
    Class for a single option in a dialog sub window.
    """

    def __init__(self, text: str, tooltip: str = None):
        """
        Initialize the DialogSubWindowOption class.

        Parameters
        ----------
        text : str
            The text of the option.
        tooltip : str
            The tooltip of the option, default is None.
        """
        self.text = text
        self.tooltip = tooltip


class DialogSubWindow(ISubWindow):
    selectedOption = -1

    def __init__(self, prompt: str, options: [DialogSubWindowOption], title="Dialog Window"):   # pragma: no cover
        """ Initializes a dialog sub window.

        Parameters
        ----------
        prompt : str
            The prompt to display.
        options : [DialogSubWindowOption]
            The options to display.
        title : str
            The optional title of the window, by default "Dialog Window".
        """

        # Check if the master window exists
        if MasterWindow.instance is None:
            raise Exception("Master window does not exist")

        # Setup GUI manager
        self.guiManager = pygame_gui.UIManager(
            window_resolution=(MasterWindow.instance.width, MasterWindow.instance.height),
            theme_path=str(Pathing.AssureAbsolutePath("Windowing/Assets/Themes/default_theme.json"))
        )

        # Cut the prompt into sentences
        sentences = prompt.split("\n")
        largestSentenceLength = 0
        for sentence in sentences:
            if len(sentence) > largestSentenceLength:
                largestSentenceLength = len(sentence)

        # Calculate base width, based on the length of the prompt string
        baseWidth = 200
        promptWidth = largestSentenceLength * 9
        totalWidth = promptWidth if promptWidth > baseWidth else baseWidth

        # Calculate base height, based on the number of options
        lineHeight = 16
        baseHeight = lineHeight * 2 + len(sentences) * lineHeight
        buttonMargin = 10
        buttonHeight = 40
        totalHeight = baseHeight + (len(options) * (buttonHeight + buttonMargin)) + buttonMargin

        # Create base panel
        self.panel = pygame_gui.elements.ui_panel.UIPanel(
            relative_rect=pygame.Rect(0, 0, totalWidth, totalHeight),
            manager=self.guiManager,
            starting_layer_height=0,
        )

        # Create the prompt labels
        for i in range(len(sentences)):
            height = baseHeight - (len(sentences) - i) * lineHeight
            pygame_gui.elements.ui_label.UILabel(
                relative_rect=pygame.Rect((0, lineHeight / 4 + i * lineHeight), (totalWidth, height)),
                text=sentences[i],
                manager=self.guiManager,
                container=self.panel,
            )

        # Create the options
        self.options = []
        for i in range(len(options)):
            possibleMargin = 0 if i == 0 else buttonMargin
            self.options.append(pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(
                    (totalWidth * .125, baseHeight + i * (buttonHeight + possibleMargin)),
                    (totalWidth * .75, buttonHeight)
                ),
                text=options[i].text,
                tool_tip_text=options[i].tooltip,
                manager=self.guiManager,
                container=self.panel
            ))

        # Overwrite GUI manager scaled mouse position
        # to make it relative to the sub window
        self.guiManager.calculate_scaled_mouse_position = lambda pos: (
            int(self.guiManager.mouse_pos_scale_factor[0] * self.previousMouseX),
            int(self.guiManager.mouse_pos_scale_factor[1] * self.previousMouseY)
        )

        # Call super constructor
        super(DialogSubWindow, self).__init__(title, "Windowing/Assets/Icons/dialog.png")

        # Center the container
        self._CenterPanel()

        # Invalidate by default
        self.invalidated = True

    def HandleInput(self, events: [pygame.event]):  # pragma: no cover
        """
        Handle the input of the user.

        Parameters
        ----------
        events : [pygame.event]
            The events that are currently being handled.
        """
        # For all events, handle GUI events
        for event in events:
            # If the window was resized, update the container to be centered
            # and resize the GUI manager
            if event.type == pygame.WINDOWRESIZED:
                self._ResizeGUIManager()
                self._CenterPanel()

            # If a button was clicked, check which option was pressed
            elif event.type == pygame_gui.UI_BUTTON_PRESSED:
                for i in range(len(self.options)):
                    if event.ui_element == self.options[i]:
                        self.selectedOption = i
                        break

            # Let the GUI manager handle the event
            self.guiManager.process_events(event)

        # Call super
        super(DialogSubWindow, self).HandleInput(events)

    def Update(self, deltaTime):  # pragma: no cover
        """
        Update the window.

        Parameters
        ----------
        deltaTime : float
            The time since the last update.
        """
        self.invalidated = True

        # Call update
        self.guiManager.update(deltaTime)

        # Call super
        super(DialogSubWindow, self).Update(deltaTime)

    def Render(self, width, height) -> pygame.Surface:  # pragma: no cover
        """
        Render the window.

        Parameters
        ----------
        width : int
            The width of the window.
        height : int
            The height of the window.

        Returns
        -------
        pygame.Surface
            The surface that is being rendered.
        """
        # Create surface

        surface = super(DialogSubWindow, self).Render(width, height)
        self.guiManager.draw_ui(surface)
        return surface

    def GetSelectedOption(self) -> int:
        """
        Get the selected option.

        Returns
        -------
        int
            The index of the selected option.
        """
        return self.selectedOption

    def InputBeenGiven(self) -> bool:
        """
        Check if the user has given input.

        Returns
        -------
        bool
            True if the user has given input, False otherwise.
        """
        return self.selectedOption != -1

    def _ResizeGUIManager(self):
        """
        Resize the GUI manager.
        """
        self.guiManager.set_window_resolution(
            (self.previousWidth, self.previousHeight)
        )

    def _CenterPanel(self):
        """
        Centers the container, should be called after initialization and window resizing.
        """
        # Offset the container to be centered
        nx = (self.guiManager.window_resolution[0] - self.panel.get_abs_rect().width) / 2
        ny = (self.guiManager.window_resolution[1] - self.panel.get_abs_rect().height) / 2
        self.panel.set_position((nx, ny))

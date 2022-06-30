# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software Project course.
# © Copyright Utrecht University (Department of Information and Computing Sciences)

"""
Implementation of the ISubWindow
Allows user to input (alpha) numeric characters in response to a prompt.
"""

from enum import Enum
import pygame
import pygame_gui

from IO import Pathing
from Windowing.Sub.ISubWindow import ISubWindow
from Windowing.MasterWindow import MasterWindow, MASTER_WINDOW_HEADER_SIZE


class InputType(Enum):
    """
    Enum for the different input types.
    """
    ALPHA_NUMERIC = 0,
    NUMERIC = 1


class InputSubWindow(ISubWindow):
    input: str = ""
    inputType: InputType

    def __init__(self, prompt: str, inputType: InputType, title="Input Window"):  # pragma: no cover
        """
        Initialize the InputSubWindow class, corresponding to a
        specific input type and a given title.

        Parameters
        ----------
        prompt : str
            The prompt to be displayed.
        inputType : InputType
            The type of input that is expected.
        title : str
            The (optional) title of the window, default is "Input Window".
        """

        # Set the input type
        self.inputType = inputType

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

        # Set total height
        lineHeight = 16
        baseHeight = lineHeight * 2 + len(sentences) * lineHeight
        inputHeight = 36
        buttonHeight = 40
        generalMargin = 10
        totalHeight = baseHeight + inputHeight + buttonHeight + generalMargin * 4

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

        # Create the input text box
        self.inputEntry = pygame_gui.elements.ui_text_entry_line.UITextEntryLine(
            relative_rect=pygame.Rect(
                (totalWidth * .125, baseHeight + generalMargin),
                (totalWidth * .75, inputHeight)
            ),
            manager=self.guiManager,
            container=self.panel,
        )

        # Create the confirm button
        self.confirmButton = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(
                (totalWidth / 4, baseHeight + inputHeight + generalMargin * 2),
                (totalWidth / 2, buttonHeight)
            ),
            text='Confirm',
            manager=self.guiManager,
            container=self.panel,
        )

        # Call super constructor
        super(InputSubWindow, self).__init__(title, "Windowing/Assets/Icons/input.png")

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

        # Restore GUI manager scaled mouse position
        # to make it non-relative to the sub window.
        # The events are already relative to the window
        # and thus should not be scaled.
        self.guiManager.calculate_scaled_mouse_position = lambda pos: (
            int(self.guiManager.mouse_pos_scale_factor[0] * pos[0]),
            int(self.guiManager.mouse_pos_scale_factor[1] * pos[1])
        )

        # For all events, handle GUI events
        for event in events:
            # If the window was resized, update the container to be centered
            # and resize the GUI manager
            if event.type == pygame.WINDOWRESIZED:
                self._ResizeGUIManager()
                self._CenterPanel()

            # If a button was clicked, check if it was the confirm button
            elif event.type == pygame_gui.UI_BUTTON_PRESSED:
                # If the confirm button was pressed, check if the input is valid
                if event.ui_element == self.confirmButton:
                    # Check if the input is valid

                    # Alpha numeric input
                    if self.inputType == InputType.ALPHA_NUMERIC:
                        # Check if the input is alphanumeric
                        if self.inputEntry.get_text().isalnum():
                            # Set the input
                            self.input = self.inputEntry.text

                    # Numeric input
                    elif self.inputType == InputType.NUMERIC:
                        dottedInput = self.inputEntry.get_text().replace(",", ".")
                        partialInput = self.inputEntry.get_text().replace(".", "").replace("-", "")

                        # Check if the input is numeric
                        if partialInput.isnumeric():
                            # Set the input
                            self.input = dottedInput

            # Let the GUI manager handle the event
            self.guiManager.process_events(event)

        # Call super
        super(InputSubWindow, self).HandleInput(events)

    def Update(self, deltaTime):  # pragma: no cover
        """
        Update the window.

        Parameters
        ----------
        deltaTime : float
            The time since the last update.
        """
        self.invalidated = True

        # Overwrite GUI manager scaled mouse position
        # to make it relative to the sub window
        self.guiManager.calculate_scaled_mouse_position = lambda pos: (
            int(self.guiManager.mouse_pos_scale_factor[0] * pos[0]),
            int(self.guiManager.mouse_pos_scale_factor[1] * pos[1] - MASTER_WINDOW_HEADER_SIZE)
        )

        # Call update
        self.guiManager.update(deltaTime)

        # Call super
        super(InputSubWindow, self).Update(deltaTime)

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

        surface = super(InputSubWindow, self).Render(width, height)
        self.guiManager.draw_ui(surface)
        return surface

    def GetInput(self) -> int:
        """
        Get the selected option.

        Returns
        -------
        int
            The index of the selected option.
        """
        return self.input

    def InputBeenGiven(self) -> bool:
        """
        Check if the user has given input.

        Returns
        -------
        bool
            True if the user has given input, False otherwise.
        """
        return len(self.input) > 0

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

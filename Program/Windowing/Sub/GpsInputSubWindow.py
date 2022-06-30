# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software Project course.
# © Copyright Utrecht University (Department of Information and Computing Sciences)

"""
Implementation of the ISubWindow
Allows user to input coordinates in the main window for a mapbox image to use for homography conversion
"""

import pygame
import pygame_gui

from Calibrator.Configurations.HomographyCalibrationConfiguration import GeoPosition
from IO import Pathing
from Windowing.Sub.ISubWindow import ISubWindow
from Windowing.MasterWindow import MasterWindow


class GpsInputSubWindow(ISubWindow):
    gps: GeoPosition = None

    def __init__(self, prompt: str, title="GPS Input Window"):  # pragma: no cover
        """
        Initialize the GpsInputSubWindow class, with a given title.

        Parameters
        ----------
        prompt : str
            The prompt to be displayed.
        title : str
            The title of the window.
        """

        # Check if the master window exists
        if MasterWindow.instance is None:
            raise Exception("Master window does not exist")

        # Cut the prompt into sentences
        sentences = prompt.split("\n")
        largestSentenceLength = 0
        for sentence in sentences:
            if len(sentence) > largestSentenceLength:
                largestSentenceLength = len(sentence)

        # Calculate base width, based on the length of the prompt string
        baseWidth = 435
        promptWidth = largestSentenceLength * 9
        totalWidth = promptWidth if promptWidth > baseWidth else baseWidth

        # Set total height
        lineHeight = 16
        baseHeight = lineHeight * 2 + len(sentences) * lineHeight
        inputHeight = 36
        inputFieldHeight = 40
        generalMargin = 10
        totalHeight = baseHeight + inputHeight + 2 * inputFieldHeight + generalMargin * 4

        # Setup GUI manager
        self.guiManager = pygame_gui.UIManager(
            window_resolution=(MasterWindow.instance.width, MasterWindow.instance.height),
            theme_path=str(Pathing.AssureAbsolutePath("Windowing/Assets/Themes/default_theme.json"))
        )

        # Create panel
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

        # Create latitude label and text entry
        self.latLabel = pygame_gui.elements.ui_label.UILabel(
            relative_rect=pygame.Rect((10, baseHeight + generalMargin), (200, 40)),
            text="Latitude",
            manager=self.guiManager,
            container=self.panel,
        )

        self.latEntry = pygame_gui.elements.ui_text_entry_line.UITextEntryLine(
            relative_rect=pygame.Rect((10, baseHeight + generalMargin + inputFieldHeight), (200, 36)),
            manager=self.guiManager,
            container=self.panel,
        )
        self.latEntry.focus()  # Focus by default

        # Create longitude label and text entry
        self.lonLabel = pygame_gui.elements.ui_label.UILabel(
            relative_rect=pygame.Rect((220, baseHeight + generalMargin), (200, 40)),
            text="Longitude",
            manager=self.guiManager,
            container=self.panel,
        )

        self.lonEntry = pygame_gui.elements.ui_text_entry_line.UITextEntryLine(
            relative_rect=pygame.Rect((220, baseHeight + generalMargin + inputFieldHeight), (200, 36)),
            manager=self.guiManager,
            container=self.panel,
        )

        # Create the error labels
        self.errorLabel = pygame_gui.elements.ui_label.UILabel(
            relative_rect=pygame.Rect((10, 85), (400, 35)),
            object_id="#error",
            text="Één of meer waardes zijn niet numeriek.",
            manager=self.guiManager,
            container=self.panel,
            visible=False
        )

        # Create the confirm button
        self.confirmButton = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((totalWidth / 2 - 100, totalHeight - 40 - generalMargin), (200, 40)),
            text='Opsturen',
            manager=self.guiManager,
            container=self.panel,
        )

        # Overwrite GUI manager scaled mouse position
        # to make it relative to the sub window
        self.guiManager.calculate_scaled_mouse_position = lambda pos: (
            int(self.guiManager.mouse_pos_scale_factor[0] * self.previousMouseX),
            int(self.guiManager.mouse_pos_scale_factor[1] * self.previousMouseY)
        )

        # Call super constructor
        super(GpsInputSubWindow, self).__init__(title, "Windowing/Assets/Icons/map.png")

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

            # If a button was clicked, check if it was the confirm button
            elif event.type == pygame_gui.UI_BUTTON_PRESSED:
                # If the confirm button was pressed, check if the input is valid
                if event.ui_element == self.confirmButton:
                    try:
                        latDottedInput = self.latEntry.get_text().replace(",", ".")
                        latPartialInput = self.latEntry.get_text().replace(".", "").replace("-", "")

                        lonDottedInput = self.lonEntry.get_text().replace(",", ".")
                        lonPartialInput = self.lonEntry.get_text().replace(".", "").replace("-", "")

                        # Check if the input is numeric
                        if latPartialInput.isnumeric() and lonPartialInput.isnumeric():
                            # Parse latitude and longitude as float values
                            lat = float(latDottedInput)
                            lon = float(lonDottedInput)

                            # Check if the longitude and latitude are valid
                            if lat < -90 or lat > 90 or lon < -180 or lon > 180:
                                raise ValueError

                            # Create GeoPosition and set it as given
                            self.gps = GeoPosition(latitude=lat, longitude=lon, altitude=-1)
                        else:
                            # Throw exception if the input is not numeric
                            raise ValueError
                    except ValueError:
                        # Show error labels
                        self.errorLabel.visible = True

                        # Fade in
                        self.errorLabel.set_active_effect(
                            pygame_gui.TEXT_EFFECT_FADE_IN,
                            params={'time_per_alpha_change': 0.00125}
                        )

            # Let the GUI manager handle the event
            self.guiManager.process_events(event)

        # Call super
        super(GpsInputSubWindow, self).HandleInput(events)

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
        super(GpsInputSubWindow, self).Update(deltaTime)

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

        surface = super(GpsInputSubWindow, self).Render(width, height)
        self.guiManager.draw_ui(surface)
        return surface

    def GetGivenPosition(self):  # pragma: no cover
        """
        Get the given GeoPosition.

        Returns
        -------
        GeoPosition
            The GeoPosition that is given.
        """
        return self.gps

    def InputBeenGiven(self):  # pragma: no cover
        """
        Check if the input has been given.

        Returns
        -------
        bool
            True if the input has been given, False otherwise.
        """
        return self.gps is not None

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

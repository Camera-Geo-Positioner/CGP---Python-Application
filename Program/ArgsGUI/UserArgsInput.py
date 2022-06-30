# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software Project course.
# © Copyright Utrecht University (Department of Information and Computing Sciences)

"""
The window for inputting the args. Uses tkinter as input window.
"""

import os
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd

import Main
from ArgsGUI.IArgsWindow import IArgsWindow
from typing import Dict
import argparse


class UserArgsInput(IArgsWindow):
    argumentsToPass: Dict[str, any] = None
    currentArguments: Dict[str, any]
    frame: tk.Tk
    errorLabel: tk.Label
    copyrightLabel: tk.Label
    closed: bool
    continueButton: ttk.Button
    isStream: tk.BooleanVar
    videoStreamLocation: str
    detectionMethod: str
    detectionThreshold: tk.DoubleVar
    calibrationMethod: str
    forceCalibration: tk.BooleanVar
    showDetection: tk.BooleanVar
    apiPort: int

    VideoStreamFrame: ttk.LabelFrame
    DetectionFrame: ttk.LabelFrame
    TwoD3DFrame: ttk.LabelFrame
    DebugFrame: ttk.LabelFrame
    APIFrame: ttk.LabelFrame
    PipelineFrame: ttk.LabelFrame
    VideoStreamCombobox: ttk.Combobox
    VideoStreamLocationEntry: ttk.Entry
    VideoStreamExplorerButton: ttk.Button
    DetectionMethodCombobox: ttk.Combobox
    DetectionThresholdLabel: ttk.Label
    DetectionThresholdScale: ttk.Scale
    DetectionThresholdScaleLabel: ttk.Label
    ResolutionLabel: ttk.Label
    ResolutionWidth: ttk.Entry
    ResolutionHeight: ttk.Entry
    TwoD3DMethodeCombobox: ttk.Combobox
    APIPortLabel: ttk.Label
    APIPortEntry: ttk.Entry
    TwoD3DForceCalibrationSwitch: ttk.Checkbutton
    DebugShowDetectionCheckbutton: ttk.Checkbutton

    testing = False

    @staticmethod
    def AddArgsGUIArguments(parser: argparse.ArgumentParser):  # pragma: no cover
        """
        Add the arguments of the ArgsGUI. This is only the argument that makes the GUI pop up.

        Parameters
        ----------
        parser : argparse.ArgumentParser
            The parser that parses the arguments
        """

        if parser is None:
            raise TypeError("Parser is none.")

        parser.add_argument('--argsGUI', dest='displayArgsGUI', action='store_true',
                            help='Show the launcher where a user can input the parameters of the program in a graphical'
                                 'user interface.')

    def GetArgsFromUser(self, currentArguments: Dict[str, any]):  # pragma: no cover
        """
        This function creates a gui window for the user to input
        the arguments that specify how the program will execute.
        For example, a user can define what camera to connect to
        or if a calibration will be forced.

        Returns
        -------
        an updated arguments object
        """
        self.currentArguments = currentArguments

        self.closed = False
        self.frame = tk.Tk()
        self.frame.title("CGP - Python Applicatie Launcher")
        self.frame.resizable(False, False)

        style = ttk.Style(self.frame)
        self.frame.tk.call('source', 'ArgsGUI/azure.tcl')
        style.theme_use('azure')
        style.map('azure.TCombobox', fieldbackground=[('readonly', 'green')])
        style.map('azure.TCombobox', foreground=[('readonly', 'red')])

        # The frames
        self.VideoStreamFrame = ttk.LabelFrame(
            self.frame,
            text='Video input'
        )

        self.DetectionFrame = ttk.LabelFrame(
            self.frame,
            text='Detectie'
        )

        self.TwoD3DFrame = ttk.LabelFrame(
            self.frame,
            text='2D3D Positioner'
        )

        self.DebugFrame = ttk.LabelFrame(
            self.frame,
            text='Debug'
        )

        self.APIFrame = ttk.LabelFrame(
            self.frame,
            text='API'
        )

        self.PipelineFrame = ttk.LabelFrame(
            self.frame,
            text='Pipeline resolutie'
        )

        # Video stream

        self.isStream = tk.BooleanVar()
        self.isStream.set(currentArguments['isStream'])

        self.VideoStreamCombobox = ttk.Combobox(
            self.VideoStreamFrame,
            state='readonly',
            value=['Live camerabeelden', 'Video bestand']
        )
        self.VideoStreamCombobox.configure(background='white')

        self.VideoStreamExplorerButton = ttk.Button(
            self.VideoStreamFrame,
            state='disabled',
            text='Bladeren...',
            command=self._VideoStreamExplorerButtonCommand
        )

        self.VideoStreamLocationEntry = ttk.Entry(
            self.VideoStreamFrame
        )

        if self.currentArguments['isStream']:
            self.VideoStreamCombobox.current(0)
        else:
            self.VideoStreamCombobox.current(1)

        def _SwitchVideoStream(event):
            value = self.VideoStreamCombobox.get()
            if (value == "Live camerabeelden"):
                self.VideoStreamExplorerButton['state'] = tk.DISABLED
                self.VideoStreamLocationEntry.delete(0, tk.END)
                self.VideoStreamLocationEntry.insert(0, 'rtsp://')
                self.isStream = True
            else:
                self.VideoStreamExplorerButton['state'] = tk.NORMAL
                self.VideoStreamLocationEntry.delete(0, tk.END)
                self.VideoStreamLocationEntry.insert(0, self.currentArguments['fileOrStreamLocation'])
                self.isStream = False

        self.VideoStreamCombobox.bind("<<ComboboxSelected>>", _SwitchVideoStream)

        _SwitchVideoStream("")

        # Detectie

        self.DetectionMethodCombobox = ttk.Combobox(
            self.DetectionFrame,
            state='readonly',
            value=['Manual', 'DeepSocial']
        )

        if currentArguments['detector'] == 'Manual':
            self.DetectionMethodCombobox.current(0)
        elif currentArguments['detector'] == 'DeepSocial':
            self.DetectionMethodCombobox.current(1)
        else:
            raise Exception("Invalid argument, validation has failed apparently")

        self.DetectionThresholdLabel = ttk.Label(
            self.DetectionFrame,
            text='Minimale detectie zekerheid'
        )

        self.detectionThreshold = tk.DoubleVar()
        self.detectionThreshold.set(currentArguments['detectionThreshold'])
        self.DetectionThresholdScale = ttk.Scale(
            self.DetectionFrame,
            from_=0,
            to=1,
            variable=self.detectionThreshold,
            command=self._DetectionTresholdScaleCommand
        )

        self.DetectionThresholdScaleLabel = tk.Label(
            self.DetectionFrame,
            text=self.currentArguments["detectionThreshold"]
        )

        def _SwitchDetectionThreshold(event):
            value = self.DetectionMethodCombobox.get()
            if (value == "DeepSocial"):
                self.DetectionThresholdLabel['state'] = tk.NORMAL
                self.DetectionThresholdScale['state'] = tk.NORMAL
                self.DetectionThresholdScaleLabel['state'] = tk.NORMAL
            else:
                self.DetectionThresholdLabel['state'] = tk.DISABLED
                self.DetectionThresholdScale['state'] = tk.DISABLED
                self.DetectionThresholdScaleLabel['state'] = tk.DISABLED

        self.DetectionMethodCombobox.bind("<<ComboboxSelected>>", _SwitchDetectionThreshold)

        _SwitchDetectionThreshold("")

        # Pipeline-Resolution
        self.ResolutionLabel = ttk.Label(
            self.PipelineFrame,
            text='Resolutie'
        )

        resolutionWidthValidateCommand = (self.frame.register(self._ValidateResolutionWidth), '%P')
        self.resolutionXLabel = ttk.Label(
            self.PipelineFrame,
            text='Breedte:'
        )
        self.ResolutionWidth = ttk.Entry(
            self.PipelineFrame,
            width=9,
            name='resolutie breedte')
        self.ResolutionWidth.config(validate='focusout', validatecommand=resolutionWidthValidateCommand)
        self.ResolutionWidth.insert(0, currentArguments['analyzeWidth'])

        resolutionHeightValidateCommand = (self.frame.register(self._ValidateResolutionHeight), '%P')
        self.resolutionYLabel = ttk.Label(
            self.PipelineFrame,
            text='Hoogte:'
        )
        self.ResolutionHeight = ttk.Entry(
            self.PipelineFrame,
            width=9,
            name='resolutie hoogte')
        self.ResolutionHeight.config(validate='focusout', validatecommand=resolutionHeightValidateCommand)
        self.ResolutionHeight.insert(0, currentArguments['analyzeHeight'])

        # 2D3D

        self.TwoD3DMethodeCombobox = ttk.Combobox(
            self.TwoD3DFrame,
            state='readonly',
            value=['Homography']
        )
        self.TwoD3DMethodeCombobox.current(0)

        self.forceCalibration = tk.BooleanVar()
        self.forceCalibration.set(currentArguments['forceRecalibrate'])
        self.TwoD3DForceCalibrationSwitch = ttk.Checkbutton(
            self.TwoD3DFrame,
            text='Forceer kalibratie',
            style='Switch',
            variable=self.forceCalibration
        )

        # Debug

        self.showDetection = tk.BooleanVar()
        self.showDetection.set(currentArguments['showDetections'])
        self.DebugShowDetectionCheckbutton = ttk.Checkbutton(
            self.DebugFrame,
            text='Laat detectie\nresultaat zien',
            variable=self.showDetection,
            offvalue=False,
            onvalue=True
        )

        # API

        self.APIPortLabel = ttk.Label(
            self.APIFrame,
            text='Poort Nummer:'
        )

        apiValidateCommand = (self.frame.register(self._ValidateAPIPoort), '%P')

        self.APIPortEntry = ttk.Entry(
            self.APIFrame,
            width=9,
            name='api poort')
        self.APIPortEntry.config(validate='focusout', validatecommand=apiValidateCommand)
        self.APIPortEntry.insert(0, currentArguments['port'])

        # Copyright message

        self.copyrightLabel = tk.Label(self.frame, text="© Utrecht University (ICS)")

        # Error label

        self.errorLabel = tk.Label(self.frame, text="", fg="#FF0000")

        # Continue button

        self.continueButton = ttk.Button(
            self.frame,
            text="Doorgaan",
            style="Accentbutton",
            command=self.Confirm
        )

        # Layout
        # Padding
        paddx = 10
        paddy = 10
        ipaddx = 10
        ipaddy = 10

        # Video input
        self.VideoStreamFrame.grid(row=0, column=0, padx=paddx, pady=paddy, sticky="NSWE")
        self.VideoStreamCombobox.grid(row=0, column=0, padx=ipaddx, pady=ipaddy, sticky="NSWE")
        self.VideoStreamLocationEntry.grid(row=1, column=0, padx=ipaddx, pady=ipaddy, sticky="NSWE")
        self.VideoStreamExplorerButton.grid(row=2, column=0, padx=ipaddx, pady=ipaddy, sticky="NSWE")

        # Detectie
        self.DetectionFrame.grid(row=0, column=1, padx=paddx, pady=paddy, sticky="NSWE")
        self.DetectionMethodCombobox.grid(row=0, column=0, padx=ipaddx, pady=ipaddy, columnspan=2, sticky="NSWE")
        self.DetectionThresholdLabel.grid(row=1, column=0, padx=ipaddx, pady=ipaddy, columnspan=2, sticky="NSWE")
        self.DetectionThresholdScale.grid(row=2, column=0, padx=ipaddx, pady=ipaddy, sticky="NSWE")
        self.DetectionThresholdScaleLabel.grid(row=2, column=1, padx=ipaddx, pady=ipaddy, sticky="NSWE")

        # 2D3D Positioner
        self.TwoD3DFrame.grid(row=0, column=2, padx=paddx, pady=paddy, sticky="NSWE")
        self.TwoD3DMethodeCombobox.grid(row=0, column=0, padx=ipaddx, pady=ipaddy, sticky="NSWE")
        self.TwoD3DForceCalibrationSwitch.grid(row=1, column=0, padx=ipaddx, pady=ipaddy, sticky="NSWE")

        # Pipeline
        self.PipelineFrame.grid(row=1, column=0, padx=paddx, pady=paddy, sticky="NSWE")
        self.resolutionXLabel.grid(row=1, column=0, padx=ipaddx, pady=ipaddy, sticky="NSWE")
        self.ResolutionWidth.grid(row=1, column=1, padx=ipaddx, pady=ipaddy, sticky="NSWE")
        self.resolutionYLabel.grid(row=2, column=0, padx=ipaddx, pady=ipaddy, sticky="NSWE")
        self.ResolutionHeight.grid(row=2, column=1, padx=ipaddx, pady=ipaddy, sticky="NSWE")

        # API
        self.APIFrame.grid(row=1, column=1, padx=paddx, pady=paddy, sticky="NSWE")
        self.APIPortLabel.grid(row=0, column=0, padx=ipaddx, pady=ipaddy, sticky="NSWE")
        self.APIPortEntry.grid(row=1, column=0, padx=ipaddx, pady=ipaddy, sticky="NSWE")

        # Debug
        self.DebugFrame.grid(row=1, column=2, padx=paddx, pady=paddy, sticky="NSWE")
        self.DebugShowDetectionCheckbutton.grid(row=0, column=0, padx=ipaddx, pady=ipaddy, sticky="NSWE")

        # Copyright message
        self.copyrightLabel.grid(row=2, column=0, padx=ipaddx, pady=ipaddy, sticky="SW")

        # Continue button
        self.continueButton.grid(row=2, column=1, padx=ipaddx, pady=ipaddy, sticky="S")

        # Error label
        self.errorLabel.grid(row=2, column=2, padx=ipaddx, pady=ipaddy, sticky="SE")

        self.frame.mainloop()

        if self.closed or not Main.Program.ValidateAllArguments(self.argumentsToPass):
            return None
        return self.argumentsToPass

    def _DetectionTresholdScaleCommand(self, i):  # pragma: no cover
        self.detectionThreshold.set(float(self.DetectionThresholdScale.get()))
        self.DetectionThresholdScaleLabel.configure(text=round(self.detectionThreshold.get(), 2))
        # TODO: make sure this slider still works

    def _VideoStreamExplorerButtonCommand(self):  # pragma: no cover
        fileLocation = self._SelectImageFile()
        self.VideoStreamLocationEntry.delete(0, tk.END)
        self.VideoStreamLocationEntry.insert(0, fileLocation)

    @staticmethod
    def _SelectImageFile():  # pragma: no cover
        """
        This function shows a dialogue box to user where they can select an image file
        Returns
        -------
        the file path of the selected image as a string
        """
        # define filetypes
        filetypes = (
            ('Videobestanden', '.mp4 .mov .avi'),
            ('Afbeeldingen', '.png .jpg .jpeg .gif .tiff'),
            ('Alle bestanden', '*.*')
        )

        # creates dialogue box for selecting an image
        filename = fd.askopenfilename(
            title='Kies het videobestand dat je wilt gebruiken',
            initialdir='./',
            filetypes=filetypes)

        return filename

    def OnClosing(self):
        """
        Window closing event, ensures that the window is closed correctly.
        """
        self.closed = True
        self.frame.destroy()

    @staticmethod
    def PrintError(text: str, errorLabel: ttk.Label):  # pragma: no cover
        """
        Print an error to a label

        Parameters
        ----------
        text : str
            The error to be printed to the label
        errorLabel : ttk.Label
            Label to print the error to
        """
        errorLabel.config(text=text)

    def _ValidateAPIPoort(self, value):  # pragma: no cover
        self.ValidateIntegerValues()
        return self.ValidateInteger(self.APIPortEntry, 1024, 65536)

    def _ValidateResolutionWidth(self, value):  # pragma: no cover
        self.ValidateIntegerValues()
        return self.ValidateInteger(self.ResolutionWidth, 0, 10000)

    def _ValidateResolutionHeight(self, value):  # pragma: no cover
        self.ValidateIntegerValues()
        return self.ValidateInteger(self.ResolutionHeight, 0, 10000)

    def ValidateIntegerValues(self):  # pragma: no cover
        """
        Validate all integer values

        Returns
        -------
        bool
            True if all integer values are correct.
        """
        errorStatus = True
        errorStatus = errorStatus and self.ValidateInteger(self.APIPortEntry, 1024, 65536)
        errorStatus = errorStatus and self.ValidateInteger(self.ResolutionWidth, 0, 10000)
        errorStatus = errorStatus and self.ValidateInteger(self.ResolutionHeight, 0, 10000)
        if errorStatus:
            self.PrintError('', self.errorLabel)
        return errorStatus

    def ValidateInteger(self, entry: ttk.Entry, minValue: int, maxValue: int):
        """
        Validate an Integer

        Parameters
        ----------
        entry : ttk.Entry
            The entry containing the integer
        minValue : int
            The minimum value the integer needs to be greater than
        maxValue : int
            The maximum value the integer needs to be smaller then

        Returns
        -------
        bool
            True if the entry contains an integer between minValue and maxValue
        """

        # Check if entry is empty
        if not bool(entry.get()):
            if not self.testing:  # pragma: no cover
                entry['foreground'] = 'red'
                self.PrintError(entry.winfo_name() + ' is leeg.', self.errorLabel)
            return False

        # Check if entry is an int.
        try:
            int(entry.get())
        except:
            if not self.testing:  # pragma: no cover
                entry['foreground'] = 'red'
                self.PrintError(
                    entry.winfo_name() + ' is geen geheel getal. Vermijd letters, punten, komma\'s, en tekens.',
                    self.errorLabel)
            return False

        # Check if entry between minValue and maxValue
        if minValue < int(entry.get()) < maxValue:
            if not self.testing:  # pragma: no cover
                entry['foreground'] = 'black'
            return True

        if not self.testing:  # pragma: no cover
            entry['foreground'] = 'red'
            self.PrintError(entry.winfo_name() + ' ligt niet tussen ' + str(minValue) + ' en ' + str(maxValue) + '.',
                            self.errorLabel)
        return False

    def Confirm(self):  # pragma: no cover
        """
        Confirm all the arguments, store them in a dictionary and close the window.
        """

        # Check that the API port value is valid
        if not (self.ValidateIntegerValues()):
            return False

        self.videoStreamLocation = self.VideoStreamLocationEntry.get()

        self.detectionMethod = self.DetectionMethodCombobox.get()
        self.calibrationMethod = self.TwoD3DMethodeCombobox.get()

        self.argumentsToPass = dict()
        self.argumentsToPass['isStream'] = self.isStream
        self.argumentsToPass['fileOrStreamLocation'] = self.videoStreamLocation
        self.argumentsToPass['detector'] = self.detectionMethod
        self.argumentsToPass['detectionThreshold'] = self.detectionThreshold.get()
        self.argumentsToPass['analyzeWidth'] = int(self.ResolutionWidth.get())
        self.argumentsToPass['analyzeHeight'] = int(self.ResolutionHeight.get())
        self.argumentsToPass['calibrator'] = self.calibrationMethod
        self.argumentsToPass['forceRecalibrate'] = self.forceCalibration.get()
        self.argumentsToPass['showDetections'] = self.showDetection.get()
        self.argumentsToPass['port'] = int(self.APIPortEntry.get())

        # Not implemented in the GUI
        self.argumentsToPass['keepID'] = self.currentArguments['keepID']
        self.argumentsToPass['calibrateDataSet'] = self.currentArguments['calibrateDataSet']
        self.argumentsToPass['calibrateDataSetMethod'] = self.currentArguments['calibrateDataSetMethod']
        self.argumentsToPass['noEncryption'] = self.currentArguments['noEncryption']
        self.frame.destroy()
        return "break"

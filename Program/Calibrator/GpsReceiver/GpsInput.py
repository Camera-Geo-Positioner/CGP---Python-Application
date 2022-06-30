# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software Project course.
# © Copyright Utrecht University (Department of Information and Computing Sciences)

"""
Implementation of the IGpsReceiver.
The window for inputting the camera gps position. Uses tkinter as input window.
"""

from Calibrator.GpsReceiver.IGpsReceiver import IGpsReceiver
import tkinter as tk
from Calibrator.Configurations.HomographyCalibrationConfiguration import GeoPosition


class GpsInput(IGpsReceiver):

    Gps: GeoPosition
    frame: tk.Tk
    latitudeTxt: tk.Text
    longitudeTxt: tk.Text
    altitudeTxt: tk.Text
    confirmButton: tk.Button
    errorLabel: tk.Label
    closed: bool

    def GetGpsPosition(self):
        """
        This function creates a gui window for the user to input
        the gps coordinates of the surrounding area.

        Returns
        -------
        A GpsPosition from user input
        """
        self.closed = False
        self.frame = tk.Tk()
        self.frame.title("Gps position input")
        self.frame.geometry('250x205')

        # example input label
        tk.Label(self.frame, text="Please enter WGS84 coordinates. \ne.g. (52.090695, 5.121314, 3).").pack()

        # TextBox Creation
        tk.Label(self.frame, text="Latitude:").pack()
        self.latitudeTxt = tk.Text(self.frame,
                                   height=1,
                                   width=20)
        self.latitudeTxt.pack()
        self.latitudeTxt.bind("<Tab>", GpsInput.FocusNextWidget)
        self.latitudeTxt.bind("<Return>", self.Confirm)

        tk.Label(self.frame, text="Longitude:").pack()
        self.longitudeTxt = tk.Text(self.frame,
                                    height=1,
                                    width=20)
        self.longitudeTxt.pack()
        self.longitudeTxt.bind("<Tab>", GpsInput.FocusNextWidget)
        self.longitudeTxt.bind("<Return>", self.Confirm)

        tk.Label(self.frame, text="Altitude:").pack()
        self.altitudeTxt = tk.Text(self.frame,
                                   height=1,
                                   width=20)
        self.altitudeTxt.pack()
        self.altitudeTxt.bind("<Tab>", GpsInput.FocusNextWidget)
        self.altitudeTxt.bind("<Return>", self.Confirm)

        # Button creation
        self.confirmButton = tk.Button(self.frame,
                                       text="Confirm",
                                       command=self.Confirm)
        self.confirmButton.pack()

        # Label Creation
        self.errorLabel = tk.Label(self.frame, text="")
        self.errorLabel.pack()

        self.frame.protocol("WM_DELETE_WINDOW", self.OnClosing)
        self.frame.mainloop()

        if self.closed:
            return None
        return self.Gps

    def OnClosing(self):
        self.closed = True
        self.frame.destroy()

    def PrintError(self):
        self.errorLabel.config(text="Error: input not in correct format.")

    def Confirm(self, event=None):
        lon = self.longitudeTxt.get(1.0, "end-1c")
        lat = self.latitudeTxt.get(1.0, "end-1c")
        alt = self.altitudeTxt.get(1.0, "end-1c")
        try:
            self.Gps = GeoPosition(longitude=float(lon), latitude=float(lat), altitude=float(alt))
            self.frame.destroy()
        except ValueError:
            self.PrintError()
        return "break"

    @staticmethod
    def FocusNextWidget(event):
        event.widget.tk_focusNext().focus()
        return "break"

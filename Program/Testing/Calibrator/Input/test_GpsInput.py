from unittest.mock import Mock

from Calibrator.Configurations.HomographyCalibrationConfiguration import GeoPosition
from Calibrator.GpsReceiver.GpsInput import GpsInput
import tkinter as tk
import pytest


class TestGpsInput:

    @pytest.mark.parametrize("lon, lat, alt", [("5.984534", "50.3568", "0"),
                                               ("5.", "50.", "0."),
                                               (".56516", "50.", "1351"),
                                               ("-.56516", "50.", "-.1465136e-5")])
    def test_GetGps(self, lon, lat, alt):
        gpsInput = GpsInput()

        def setFalse(_, __):
            gpsInput.closed = False

        def setMocks():
            gpsInput.frame = Mock()
            gpsInput.frame.title = Mock()
            gpsInput.frame.geometry = Mock()
            gpsInput.frame.protocol = Mock(side_effect=setFalse)
            gpsInput.frame.mainloop = Mock(side_effect=gpsInput.Confirm)
            return gpsInput.frame

        def setTxtMocks(_, height, width):

            if not hasattr(gpsInput, "latitudeTxt"):
                gpsInput.latitudeTxt = Mock()
                gpsInput.latitudeTxt.pack = Mock()
                gpsInput.latitudeTxt.get.return_value = lat
                return gpsInput.latitudeTxt
            elif not hasattr(gpsInput, "longitudeTxt"):
                gpsInput.longitudeTxt = Mock()
                gpsInput.longitudeTxt.pack = Mock()
                gpsInput.longitudeTxt.get.return_value = lon
                return gpsInput.longitudeTxt
            else:
                gpsInput.altitudeTxt = Mock()
                gpsInput.altitudeTxt.pack = Mock()
                gpsInput.altitudeTxt.get.return_value = alt
                return gpsInput.altitudeTxt

        tk.Tk = Mock(side_effect=setMocks)
        tk.Text = Mock(side_effect=setTxtMocks)
        tk.Button = Mock()
        tk.Label = Mock()

        gps = gpsInput.GetGpsPosition()

        assert gps.latitude == float(lat)
        assert gps.longitude == float(lon)
        assert gps.altitude == float(alt)

    def test_Confirm(self):
        gpsInput = GpsInput()

        gpsInput.frame = Mock()
        gpsInput.latitudeTxt = Mock()
        gpsInput.longitudeTxt = Mock()
        gpsInput.altitudeTxt = Mock()

        gpsInput.latitudeTxt.get = Mock(return_value="50")
        gpsInput.longitudeTxt.get = Mock(return_value="5")
        gpsInput.altitudeTxt.get = Mock(return_value="0")

        gpsInput.Confirm()

        gps = gpsInput.Gps
        assert gps.latitude == 50
        assert gps.longitude == 5
        assert gps.altitude == 0

    @pytest.mark.parametrize("lon, lat, alt", [("5,984534", "50,3568", "0"),
                                               ("5,arg", "sg/-*rg-", "dgr"),
                                               ("hello", "world", "!")])
    def test_InputError(self, lon, lat, alt):
        gpsInput = GpsInput()

        def setMocks():
            gpsInput.frame = Mock()
            gpsInput.frame.mainloop = Mock(side_effect=gpsInput.Confirm)
            return gpsInput.frame

        def setTxtMocks(_, height, width):

            if not hasattr(gpsInput, "latitudeTxt"):
                gpsInput.latitudeTxt = Mock()
                gpsInput.latitudeTxt.get.return_value = lat
                return gpsInput.latitudeTxt
            elif not hasattr(gpsInput, "longitudeTxt"):
                gpsInput.longitudeTxt = Mock()
                gpsInput.longitudeTxt.get.return_value = lon
                return gpsInput.longitudeTxt
            else:
                gpsInput.altitudeTxt = Mock()
                gpsInput.altitudeTxt.get.return_value = alt
                return gpsInput.altitudeTxt

        def SetErrorMock(_, text):
            if text != "":
                return Mock()
            gpsInput.errorLabel = Mock()
            gpsInput.errorLabel.config = Mock(side_effect=SetBool)
            return gpsInput.errorLabel

        tk.Tk = Mock(side_effect=setMocks)
        tk.Text = Mock(side_effect=setTxtMocks)
        tk.Button = Mock()
        tk.Label = Mock(side_effect=SetErrorMock)

        self.errorOccurred = False

        def SetBool(text):
            self.errorOccurred = True
            gpsInput.Gps = None

        gpsInput.GetGpsPosition()

        assert self.errorOccurred

    def test_FocusNextWidget(self):
        result = GpsInput.FocusNextWidget(Mock())
        assert result == "break"

    def test_Closing(self):
        gpsInput = GpsInput()

        def Close(_, __):
            gpsInput.OnClosing()

        def setMocks():
            gpsInput.frame = Mock()
            gpsInput.frame.title = Mock()
            gpsInput.frame.geometry = Mock()
            gpsInput.frame.protocol = Mock(side_effect=Close)
            gpsInput.frame.mainloop = Mock(side_effect=gpsInput.Confirm)
            return gpsInput.frame

        def setTxtMocks(_, height, width):

            if not hasattr(gpsInput, "latitudeTxt"):
                gpsInput.latitudeTxt = Mock()
                gpsInput.latitudeTxt.pack = Mock()
                gpsInput.latitudeTxt.get.return_value = 0
                return gpsInput.latitudeTxt
            elif not hasattr(gpsInput, "longitudeTxt"):
                gpsInput.longitudeTxt = Mock()
                gpsInput.longitudeTxt.pack = Mock()
                gpsInput.longitudeTxt.get.return_value = 0
                return gpsInput.longitudeTxt
            else:
                gpsInput.altitudeTxt = Mock()
                gpsInput.altitudeTxt.pack = Mock()
                gpsInput.altitudeTxt.get.return_value = 0
                return gpsInput.altitudeTxt

        tk.Tk = Mock(side_effect=setMocks)
        tk.Text = Mock(side_effect=setTxtMocks)
        tk.Button = Mock()
        tk.Label = Mock()

        gps = gpsInput.GetGpsPosition()

        assert gps is None

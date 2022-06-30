# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software Project course.
# © Copyright Utrecht University (Department of Information and Computing Sciences)

"""
Implementation of the IImageReceiver.
This class is used to upload top-down view images and
retrieve the image along with its metadata.
It retrieves the filepath using the lib tkinter
than it asks for a zoom-in in the GUI of pygame, implemented by MasterWindow
"""
import numpy as np

from Calibrator.ImageReceiver.IImageReceiver import IImageReceiver
from tkinter import filedialog as fd
import tkinter as tk
from typing import Tuple
from Calibrator.ImageReceiver.SmartImage import SmartImage
from Calibrator.Configurations.HomographyCalibrationConfiguration import GeoPosition, HomographyGeoData
import cv2
import os.path
from rijksdriehoek import rijksdriehoek
import pygame
from Windowing.MasterWindow import MasterWindow, SubWindowPosition
from Calibrator.Input.PrimitiveInput import PrimitiveInput, Primitives
from Windowing.Sub.PrimitiveInputSubWindow import PrimitiveInputSubWindow
from Windowing.Rendering import *
import time


class CycloMedia(IImageReceiver):
    """
    This class is used to upload top-down view images
    and retrieve the image along with its metadata.
    """

    def CreateGeoSmartImage(self, masterWindow=None) -> Tuple[SmartImage, HomographyGeoData] or None:
        """
        This function reads an image and its metadata selected by the user to create a smart image.

        Returns
        -------
        A SmartImage object
        """

        if masterWindow is None:
            return None

        # get filepath: IO
        fileName = CycloMedia._SelectImageFile()

        # No file selected
        if fileName is None or fileName == '':
            return None

        # get file containing meta info about image
        metaFileName = os.path.splitext(fileName)[0] + '.tfw'

        # There is no meta file
        if not os.path.exists(metaFileName):
            return None

        # parse metadata: IO
        (scale, x, y) = CycloMedia._GetMetaFileLines(metaFileName)

        result = self.GetZoomedInImage(fileName, (scale, x, y), masterWindow)
        if result is None:
            return None
        (image, (x2, y2)) = result

        # create rd converter
        rd = rijksdriehoek.Rijksdriehoek(x2, y2)

        # convert rd to gps
        (lat, lon) = rd.to_wgs()

        return (
            SmartImage(image),
            HomographyGeoData(
                (0, 0),
                GeoPosition(longitude=lon, latitude=lat, altitude=0),
                scale,
                (x2, y2)
            )
        )

    @staticmethod
    def GetZoomedInImage(fileName: str, metaData: (float, float, float), masterWindow: MasterWindow):
        image = cv2.imread(fileName)
        Rect = CycloMedia.GetZoomSquareFromUser(masterWindow, image.copy())

        if Rect is None:
            return None

        # normalize to be top left bottom right
        Rect = ((np.maximum(np.min([Rect[0][0], Rect[1][0], image.shape[0]]), 0),
                 (np.maximum(np.min([Rect[0][1], Rect[1][1], image.shape[1]]), 0))),  # point1 (smallest x and y)
                ((np.minimum(np.max([Rect[0][0], Rect[1][0], 0]), image.shape[0])),
                 (np.minimum(np.max([Rect[0][1], Rect[1][1], 0]), image.shape[1]))))  # point2 (biggest x and y)

        image = Rendering.ConvertOpenCVImageToPyGameImage(image)
        zoomedImage = image.subsurface(Rect[0], (Rect[1][0] - Rect[0][0], Rect[1][1] - Rect[0][1]))

        (scale, x, y) = metaData

        newAnchorPoint = (x + scale * Rect[0][0], y - scale * Rect[0][1])  # anchor point is now the top left of Rect

        bgrImage = Rendering.ConvertSurfaceToOpenCV(zoomedImage)

        return bgrImage, newAnchorPoint

    @staticmethod
    def GetZoomSquareFromUser(masterWindow, image):  # pragma: no cover
        message = "Boven Aanzicht: Selecteer het inzoomen met behulp van de rechthoek."
        userInput = PrimitiveInputSubWindow(image, message)

        # Request primitives input
        userInput.RequestPrimitivesInput([Primitives.Square])

        # Set the master window's sub windows
        masterWindow.AppendSubWindow(userInput, SubWindowPosition.Left)
        masterWindow.RemoveSubWindow(SubWindowPosition.Right)

        # Create the menu GUI
        userInput.CreateMenuGUI()

        # Setup get result method
        results = (False, [])

        def getResults():
            sqr = userInput.GetPrimitiveResults()
            return sqr

        while results[0] is False:
            # If the master window has been closed, return None
            if not masterWindow.running:
                return None

            # Get results again, sleep and continue
            results = getResults()
            time.sleep(0.01)
            continue

        # Remove the two sub windows from the master window
        masterWindow.RemoveSubWindow(SubWindowPosition.Left)
        masterWindow.RemoveSubWindow(SubWindowPosition.Right)

        # Get results
        if results[1] is None:  # Result list is empty
            return None

        return results[1][0].points  # We only request one primitive

    @staticmethod
    def _GetMetaFileLines(metaFileName: str):
        """
        This function retrieves some metadata from a file through IO

        Parameters
        ----------
        metaFileName: str
            The file path to a metadata file (*.tfw)

        Returns
        -------
        (scale: float, x: float, y: float)
        """
        with open(metaFileName, 'r') as tfw:
            lines = tfw.readlines()
        return float(lines[0]), float(lines[4]), float(lines[5])

    @staticmethod
    def _SelectImageFile():
        """
        This function shows a dialogue box to user where they can select an image file
        Returns
        -------
        the file path of the selected image as a string
        """

        # to hide root window
        root = tk.Tk()
        root.withdraw()

        # Define filetypes
        filetypes = (
            ('tif files', '*.tif'),
            ('png files', '*.png'),
            ('jpg files', '*.jpg'),
            ('jpeg files', '*.jpeg'),
            ('jp2 files', '*.jp2'),
            ('jpe files', '*.jpe')
        )

        # Creates dialogue box for selecting an image
        filename = fd.askopenfilename(
            title='Open een bovenaanzicht afbeelding waar de camera op kijkt.',
            initialdir='/',
            filetypes=filetypes)

        # Linux specific failsafe: prevent tuple returnable when quitting the dialog
        if isinstance(filename, tuple):
            return None

        return filename

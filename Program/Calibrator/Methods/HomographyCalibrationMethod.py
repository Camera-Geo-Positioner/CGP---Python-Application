# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software Project course.
# © Copyright Utrecht University (Department of Information and Computing Sciences)

import queue
import time

from Windowing.Sub.DialogSubWindow import DialogSubWindow, DialogSubWindowOption
from Windowing.Sub.InputSubWindow import InputSubWindow, InputType
from Windowing.Sub.PrimitiveInputSubWindow import PrimitiveInputSubWindow

"""
An implementation of the ICalibrationMethod.
The Homography Calibration Method is used for the Homography calibration.
"""

import cv2
import numpy as np

from Windowing.MasterWindow import MasterWindow

from Calibrator.Configurations.HomographyCalibrationConfiguration import HomographyCalibrationConfiguration
from Calibrator.Methods.ICalibrationMethod import ICalibrationMethod
from Calibrator.Input.PrimitiveInput import PrimitiveInput, Primitives
from Calibrator.ImageReceiver.MapBoxAPI import MapBoxAPI
from Calibrator.ImageReceiver.CycloMedia import CycloMedia
from Calibrator.ImageReceiver.MapBoxAPI import MapBoxAPI
from Windowing.MasterWindow import SubWindowPosition


# Implementation of a calibrator specifically for using homography to
# obtain a linear transformation matrix going from camera view to top-down view
class HomographyCalibrationMethod(ICalibrationMethod):
    def MakeWorldRepresentation(self, srcImage, masterWindow: MasterWindow) \
            -> HomographyCalibrationConfiguration or None:  # pragma: nocover
        """
        Creates a configuration object currently from user input by matching squares between the
        camera image and the topdown image.

        Parameters
        ----------
        srcImage : cv2.Image
            the image retrieved from the camera.
        masterWindow : MasterWindow
            the master window of the program

        Returns
        -------
        HomographyCalibrationConfiguration
            A configuration object (in this case: homography).
        """

        # Check if valid
        if srcImage is None or masterWindow is None:
            return None

        # Request the user to select the top-down image retrieval method
        topDownDialogSubWindow = DialogSubWindow(
            "Selecteer de oplevering methode voor het\nplaatje van de scene van bovenaf",
            [
                # Option #0 - MapBox
                DialogSubWindowOption(
                    "MapBoxAPI (Online)",
                    "Laad een plaatje onlin in aan de hand van geocoordinaten."
                ),
                # Option #1 - CycloMedia
                DialogSubWindowOption(
                    "CycloMedia (Offline)",
                    "Laad een plaatje offlin in aan de hand van een CycloMedia plaatje en een bijbehornd\
                     geocoordinaten bestand."
                )
            ],
            "Maak een keuze",
        )
        masterWindow.AppendSubWindow(topDownDialogSubWindow, SubWindowPosition.Left)

        # Wait for the user to select a method
        while not topDownDialogSubWindow.InputBeenGiven() and masterWindow.running:
            time.sleep(0.01)

        # Handle force close
        if not topDownDialogSubWindow.InputBeenGiven():
            return None

        # Remove sub window and get the selected method
        masterWindow.RemoveSubWindow(SubWindowPosition.Left)
        topDownMethod = topDownDialogSubWindow.GetSelectedOption()

        # Call the top-down image receiver to get the top-down image
        result = None
        if topDownMethod == 0:  # MapBoxAPI
            result = MapBoxAPI().CreateGeoSmartImage()
        elif topDownMethod == 1:  # CycloMedia
            result = CycloMedia().CreateGeoSmartImage(masterWindow)

        # Check if valid
        if result is None:
            return None

        # Extract the top-down image and the homography geo data
        (smartImage, homographyGeoData) = result
        if smartImage is None or homographyGeoData is None:
            return None
        dstImage = smartImage.GetImage()

        # Request the primitive the user wants to use to match features
        primitiveDialogSubWindow = DialogSubWindow(
            "Selecteer de gewenste primitieve(n)\nvoor kalibratie.",
            [
                # Option #0 - Plane
                DialogSubWindowOption(
                    "Vlakte",
                    "Een vlakte met vier punten."
                ),
                # Option #1 - Points
                DialogSubWindowOption(
                    "Losse Punten",
                    "Een set van acht losse punten."
                )
            ],
            "Maak een keuze",
        )
        masterWindow.AppendSubWindow(primitiveDialogSubWindow, SubWindowPosition.Left)

        # Wait for the user to select a method
        while not primitiveDialogSubWindow.InputBeenGiven() and masterWindow.running:
            time.sleep(0.01)

        # Handle force close
        if not primitiveDialogSubWindow.InputBeenGiven():
            return None

        # Remove sub window and get the selected method
        masterWindow.RemoveSubWindow(SubWindowPosition.Left)
        primitive = primitiveDialogSubWindow.GetSelectedOption()

        # Create two primitive input sub windows
        srcPrimitiveInput = PrimitiveInputSubWindow(srcImage, "Camera Aanzicht")
        dstPrimitiveInput = PrimitiveInputSubWindow(dstImage, "Bovenaanzicht")

        # Set primitive input sub windows as siblings
        srcPrimitiveInput.primitiveInput.sibling = dstPrimitiveInput.primitiveInput
        dstPrimitiveInput.primitiveInput.sibling = srcPrimitiveInput.primitiveInput

        # Request primitives input based on the specified primitive
        if primitive == 0:  # Primitives.Plane
            srcPrimitiveInput.RequestPrimitivesInput([Primitives.Plane])
            dstPrimitiveInput.RequestPrimitivesInput([Primitives.Plane])
        elif primitive == 1:  # Primitives.Points
            srcPrimitiveInput.RequestPrimitivesInput([Primitives.Points])
            dstPrimitiveInput.RequestPrimitivesInput([Primitives.Points])

        # Have the right primitive input make menu GUI
        dstPrimitiveInput.CreateMenuGUI()

        # Set the master window's sub windows
        masterWindow.AppendSubWindow(srcPrimitiveInput, SubWindowPosition.Left)
        masterWindow.AppendSubWindow(dstPrimitiveInput, SubWindowPosition.Right)

        # Setup get result method
        srcResults = (False, [])
        dstResults = (False, [])

        def getResults():
            src = srcPrimitiveInput.GetPrimitiveResults()
            dst = dstPrimitiveInput.GetPrimitiveResults()
            return src, dst

        while srcResults[0] is False or dstResults[0] is False:
            # If the master window has been closed, return None
            if not masterWindow.running:
                return None

            # Get results again, sleep and continue
            srcResults, dstResults = getResults()
            time.sleep(0.01)
            continue

        # Remove the two sub windows from the master window
        masterWindow.RemoveSubWindow(SubWindowPosition.Left)
        masterWindow.RemoveSubWindow(SubWindowPosition.Right)

        # Get source results
        if srcResults[1] is None:  # Result list is empty
            return None
        srcPlane = srcResults[1][0].points  # We only request one primitive

        # Get destination results
        if len(dstResults) == 0 or dstResults[1] is None:  # Result list is empty
            return None
        dstPlane = dstResults[1][0].points  # We only request one primitive

        # Then get the homography matrix
        homographyMatrix = HomographyCalibrationMethod.GetTransformationMatrix(srcPlane, dstPlane)

        # Ask for the height offset
        heightInputSubWindow = InputSubWindow(
            "Geef de hoogte van de scene met respect\ntot de NAP (in meters)",
            InputType.NUMERIC,
            "Voer een getal in"
        )
        masterWindow.AppendSubWindow(heightInputSubWindow, SubWindowPosition.Left)

        # Wait for the user to input a height
        while not heightInputSubWindow.InputBeenGiven() and masterWindow.running:
            time.sleep(0.01)

        # Handle force close
        if not heightInputSubWindow.InputBeenGiven():
            return None

        # Remove sub window and get the height
        masterWindow.RemoveSubWindow(SubWindowPosition.Left)
        napHeightOffset = float(heightInputSubWindow.GetInput())
        homographyGeoData.anchorGeoPosition.altitude = napHeightOffset

        # Now create the configuration
        return HomographyCalibrationConfiguration(homographyMatrix,
                                                  (srcImage.shape[1], srcImage.shape[0]),
                                                  homographyGeoData,
                                                  smartImage)

    # finds the transformation matrix to go from shape1 to shape2, to be used to convert points as well
    @staticmethod
    def GetTransformationMatrix(src_shape, dst_shape, src_img=None, dst_img=None) -> np.array:
        """ Finds the transformation matrix to go from shape1 to shape2, to be used to convert points as well.

        Parameters
        ----------
        src_shape : np.array
            The source shape.
        dst_shape : np.array
            The destination shape.
        src_img : cv2.Image
            The optional source image.
        dst_img : cv2.Image
            The optional destination image.

        Returns
        -------
        np.array
            The transformation matrix.
        """

        # error handling
        HomographyCalibrationMethod._CheckIfCorrectShape(src_shape)
        HomographyCalibrationMethod._CheckIfCorrectShape(dst_shape)

        # Four corners of the book in source image
        pts_src = np.array(src_shape)

        # Four corners of the book in destination image.
        pts_dst = np.array(dst_shape)

        # Calculate Homography
        h, status = cv2.findHomography(pts_src, pts_dst)
        # print("homography:" + str(h))
        # print("inv of H:" + str(inv(h)))

        if src_img is not None and dst_img is not None:
            # Deal with images ---------------------------------
            # Warp source image to destination based on homography
            im_out = cv2.warpPerspective(src_img, h, (dst_img.shape[1], dst_img.shape[0]))

            # Display images for testing
            cv2.imshow("Source Image", src_img)
            cv2.imshow("Destination Image", dst_img)
            cv2.imshow("Warped Source Image", im_out)
            cv2.imwrite("Testing/Assets/im_out.jpg", im_out)

            while True:
                if cv2.waitKey(0) & 0xFF == ord('q'):
                    break

        return h

    @staticmethod
    def _CheckIfCorrectShape(shape):
        """
        This function checks the shape and makes sure nothing's weird about it
        Parameters
        ----------
        shape : Any
            a list of pixel coordinates
        """
        print(shape)
        for i, point1 in enumerate(shape):
            for j, point2 in enumerate(shape):
                if i != j and point1 is point2:
                    raise Exception("shape not correct")
                if point1[0] < 0 or point1[1] < 0:
                    raise Exception("shape out of bounds")

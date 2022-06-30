# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software Project course.
# © Copyright Utrecht University (Department of Information and Computing Sciences)

"""
The actual encoding of the image used by the calibration.
"""

import numpy as np
import cv2

from IO import Pathing


class SmartImage:
    """
    This class represents a smart image, which at runtime is a presentable
    image but which can also be stored and loaded using a unique identifier.
    """

    image = None

    def __init__(self, image: np.ndarray = None):
        """ Constructor for the SmartImage class

        Parameters
        ----------
        image : numpy.ndarray
            The image, can be None.
        """

        self.image = image

    def GetImage(self):
        """ Returns the image.

        Returns
        -------
        numpy.ndarray
            The image.
        """

        if self.image is None:
            raise ValueError("No image set, load an image first!")

        return self.image.copy()

    def Save(self, identifier):
        """
        Saves the image to the file system
        """

        # Get the path to the image
        path = Pathing.GetDataPath() / "SmartImages"

        # Check if the directory exists
        if not path.exists():
            path.mkdir()

        # Save the image
        cv2.imwrite(str(path / f"{identifier}.jpg"), self.image)

    def Load(self, identifier):
        """
        Loads the image from the file system
        """

        # Check if identifier is valid
        if identifier is None:
            raise ValueError("No identifier set!")

        # Get the path to the image
        path = Pathing.GetDataPath() / "SmartImages" / f"{identifier}.jpg"

        # Check if the directory exists
        if not path.exists():
            raise ValueError(f"No smart image with identifier {identifier} found!")

        # Load the image
        self.image = cv2.imread(str(path))

    @staticmethod
    def FromIdentifier(identifier: str):
        """
        Creates a smart image from an identifier
        """

        # Create a new smart image
        smartImage = SmartImage()

        # Load the image
        smartImage.Load(identifier)

        # Return the smart image
        return smartImage

# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software Project course.
# © Copyright Utrecht University (Department of Information and Computing Sciences)

"""
Interface for receiving images used for calibration.
These images are converted to SmartImages
"""

from typing import Tuple
from Calibrator.Configurations.HomographyCalibrationConfiguration import HomographyGeoData
from Calibrator.ImageReceiver.SmartImage import SmartImage


class IImageReceiver:
    def CreateGeoSmartImage(self) -> Tuple[SmartImage, HomographyGeoData] or None:
        """
        Is meant to be overridden by some implementation (e.g. some api call or database lookup)

        Returns
        -------
        Tuple[SmartImage, HomographyGeoData]
            The smart image and the homography geo data.
        """
        raise NotImplementedError("Method not implemented")

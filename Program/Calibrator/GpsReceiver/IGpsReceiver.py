# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software Project course.
# © Copyright Utrecht University (Department of Information and Computing Sciences)

"""
Interface for getting the camera gps position.
"""

import abc
from Calibrator.Configurations.HomographyCalibrationConfiguration import GeoPosition


class IGpsReceiver:

    @abc.abstractmethod
    def GetGpsPosition(self) -> GeoPosition or None:
        raise NotImplementedError()

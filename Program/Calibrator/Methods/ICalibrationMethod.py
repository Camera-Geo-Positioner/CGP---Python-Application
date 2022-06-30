# This program has been developed by students from the bachelor Computer
# Science at Utrecht University within the Software Project course.
# © Copyright Utrecht University (Department of Information
# and Computing Sciences)

"""
Interface for the actual calibration methods.
These are the actual implementations of the calibration methods and return the calibration configuration used in
conversion from 2D to 3D.
"""

from abc import ABC, abstractmethod
from Calibrator.Configurations.ICalibrationConfiguration import ICalibrationConfiguration
from Windowing.MasterWindow import *


class ICalibrationMethod(ABC):
    @abstractmethod
    def MakeWorldRepresentation(self, srcImage, masterWindow: MasterWindow) -> ICalibrationConfiguration or None:
        raise NotImplementedError("Method not implemented")

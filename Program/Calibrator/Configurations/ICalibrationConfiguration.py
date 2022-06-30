# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software Project course.
# © Copyright Utrecht University (Department of Information and Computing Sciences)

"""
A calibration configuration used by converters to convert 2D to 3D.
"""

import os
from abc import abstractmethod
from IO.Pathing import GetDataPath
from IO.SerializableJSON import SerializableJSON


class ICalibrationConfiguration(SerializableJSON):
    @abstractmethod
    def Save(self, cameraId):
        """ Save the configuration

        Parameters
        ----------
        cameraId : string
            The camera id
        """

        # Save the configuration
        self.ToJSON(self._GetJSONPath(cameraId))

    @abstractmethod
    def Load(self, cameraId, arguments=None):
        """ Load the configuration

        Parameters
        ----------
        cameraId : string
            The camera id
        arguments : Dict
            dictionary of program arguments
        """

        # Load the configuration
        self.FromJSON(self._GetJSONPath(cameraId))

    @staticmethod
    def Exists(methodClass, cameraId):
        """ Check if the configuration exists

        Parameters
        ----------
        methodClass : class
            The class of the configuration
        cameraId : string
            The camera id
        """

        className = methodClass.__name__
        fullName = className + '_' + str(cameraId) + '.json'
        fullPath = GetDataPath() / fullName
        return fullPath.exists()

    def _GetJSONPath(self, cameraId):
        """ Get the path to the JSON file

        Parameters
        ----------
        cameraId : string
            The camera id
        """

        # Format path with camera id and the calibration method name
        className = self.__class__.__name__
        fullName = className + '_' + str(cameraId) + '.json'
        fullPath = GetDataPath() / fullName
        return fullPath

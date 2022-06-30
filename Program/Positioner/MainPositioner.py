# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software Project course.
# © Copyright Utrecht University (Department of Information and Computing Sciences)

"""
Pipeline object that handles the conversion of the 2D objects to 3D objects and sending it to the API.
"""

from FrameAnalyzer.IDataWriteConnection import *
from Positioner.IConvertor import *
from API.APIController import *


# The Positioner takes 2D object data and transforms it into 3D object data to send to the visualizer
class MainPositioner(IDataWriteConnection):
    """
    The main connecting component for converting the 2D positions to 3D positions.
    Converts the DetectedObject[] data to DetectedObjectPosition[] data with the given IConvertor.
    Sends the DetectedObjectPotion[] data via the given API.
    """
    convertor: IConvertor = None
    api: APIController = None
    writeToConsole: bool = False

    def __init__(self, convertor: IConvertor, api: APIController, writeToConsole: bool = False):
        self.convertor = convertor
        self.api = api
        self.writeToConsole = writeToConsole

    def WriteData(self, detections: [DetectedObject], frameIndex: int, frameReadDatetime: datetime):
        """
        Implementation of WriteData from the IDataWriteConnection.
        Converts the DetectedObject[] data using the given IConvertor and sends it through the API.

        Parameters
        ----------
        detections : [DetectedObject]
            The DetectedObject[] data.
        frameIndex : int
            The index of the frame belonging to the DetectedObject[] data.
        frameReadDatetime : datetime
            The time at which the frame was initially loaded into the system
        """
        # No detections
        if detections is None:
            return
        if len(detections) <= 0:
            return

        if self.writeToConsole:
            print('Frame: {0}'.format(frameIndex))
            # for detection in detections:
            #     print(detection)

        # Convert the data to 3D
        if self.convertor is None:
            return
        detectedObjectPositions = self.convertor.ConversionSinglePixelError(detections, frameIndex)

        if self.writeToConsole:
            for detection in detectedObjectPositions:
                print(detection)

        # Send data through the API
        if self.api is None:
            return
        self.api.Send(detectedObjectPositions, frameIndex, frameReadDatetime)

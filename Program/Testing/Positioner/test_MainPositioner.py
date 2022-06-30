# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software Project course.
# © Copyright Utrecht University (Department of Information and Computing Sciences)


from Positioner.MainPositioner import *
from Positioner.IConvertor import *
from unittest.mock import patch, MagicMock

from datetime import datetime
import asyncio

convertor = IConvertor(None)
convertor.staticError = MagicMock()
convertor.staticError.GetMaxError = MagicMock(return_value=0)
detections = [DetectedObject(1, 1, 0, 0), DetectedObject(5, 5, 1, 0)]


# Test if positioner works with normal input
def test_Normal():
    api = TestAPI(asyncio.run(GetLoop()))
    positioner = MainPositioner(convertor, api, True)
    positioner.WriteData(detections, 0, datetime.now())


# Test if the positioner does not crash without a convertor
def test_NullConvertor():
    api = TestAPI(asyncio.run(GetLoop()))
    positioner = MainPositioner(None, api)
    positioner.WriteData(detections, 0, datetime.now())


# Test if the positioner does not crash without an API
def test_NullAPI():
    positioner = MainPositioner(convertor, None)
    positioner.WriteData(detections, 0, datetime.now())


# Test if the positioner does not crash with empty detection input
def test_EmptyDetections():
    api = TestAPI(asyncio.run(GetLoop()))
    positioner = MainPositioner(convertor, api)
    positioner.WriteData([], 0, datetime.now())


# Test if the positioner does not crash with null detection input
def test_NullDetections():
    api = TestAPI(asyncio.run(GetLoop()))
    positioner = MainPositioner(convertor, api)
    positioner.WriteData(None, 0, datetime.now())


# Test if the positioner does not crash with empty convertor return
def test_EmptyReturn():
    api = TestAPI(asyncio.run(GetLoop()))
    emptyConvertor = EmptyConvertor(None)
    positioner = MainPositioner(emptyConvertor, api)
    positioner.WriteData(detections, 0, datetime.now())


async def GetLoop():
    return asyncio.get_running_loop()


# Test implementation of the API, simply write to the console
class TestAPI(APIController):

    # Test implementation, write to the console
    def Send(self, detectedObjects: List[DetectedObjectPosition], frameIndex=1, frameTimeStamp=datetime.now()):
        if len(detectedObjects) <= 0:
            return

        print('Frame: {0}'.format(frameIndex))
        for detection in detectedObjects:
            print('({0}, {1}, {2}, {3}, {4})'.format(str(detection.longitude),
                                                     str(detection.latitude),
                                                     str(detection.altitude),
                                                     str(detection.id),
                                                     str(detection.type)))


# Test implementation of the IConvertor
class EmptyConvertor(IConvertor):

    # Test implementation that returns an empty list
    def Convert2DTo3D(self, detectedObjects: [DetectedObject], frameIndex: int, showConversions=False):
        return []       # test output

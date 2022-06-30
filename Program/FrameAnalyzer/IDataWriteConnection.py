# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software Project course.
# © Copyright Utrecht University (Department of Information and Computing Sciences)

"""
Interface for the next step in the data pipeline after the FrameAnalyzer.
"""

from datetime import datetime
from FrameAnalyzer.IDetector import DetectedObject


class IDataWriteConnection:
    """
    The interface for the DataWriteConnection objects that can be used in the MainFrameAnalyzer.
    """

    def WriteData(self, detections: [DetectedObject], frameIndex: int, frameReadDatetime: datetime):
        """
        Write DetectionObject[] data together with the frameIndex to another (part of the) program.

        Parameters
        ----------
        detections : [DetectedObject]
            The DetectedObject[] data to be written.
        frameIndex : int
            The frame index belonging to the DetectedObject[] data.
        frameReadDatetime : datetime
            The time at which the frame was initially loaded into the system
        """
        if len(detections) <= 0:
            return detections, frameIndex, frameReadDatetime

        print('Frame: {0}'.format(frameIndex))
        for detection in detections:
            print('({0}, {1}, {2}, {3})'.format(str(detection.x), str(detection.y), str(detection.id),
                                                str(detection.type)))

        return detections, frameIndex, frameReadDatetime

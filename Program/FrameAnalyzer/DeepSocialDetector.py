# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software Project course.
# © Copyright Utrecht University (Department of Information and Computing Sciences)


from collections import namedtuple
from FrameAnalyzer.DeepSocial.deepsocial_main import darknet_helper
from FrameAnalyzer.DeepSocial.darknet import darknet, sort as sort
from FrameAnalyzer.IDetector import IDetector, DetectedObject
from Windowing.Sub.CameraSubWindow import *
import numpy as np
import cv2
from pdoc import __pdoc__

__pdoc__["DeepSocial"] = False


class DeepSocialDetector(IDetector):
    """
    An implementation of the IDetector interface.
    Uses the darknet to find humans.
    """

    # (0:OFF/ 1:ON)
    subWindow: CameraSubWindow

    # constructor of the deepsocial detector
    def __init__(self, showDetections=False, frameWidth=960, frameHeight=540, detectionThreshold=0.5, subWindow=None):
        """
        Initialize the DeepSocialDetector object.

        Parameters
        ----------
        showDetections : bool
            Whether to show the detections on the frame. Debuginfo.
        frameWidth : int
            The width of the frames that the detector is going to work with.
        frameHeight : int
            The height of the frame that the detector is going to work with.
        detectionThreshold : float
            The threshold of how certain the detection of a human needs to be before being used.
        subWindow : CameraSubWindow
            The subWindow used to show the detections
        """

        self.tracker = sort.Sort(max_age=25, min_hits=4, iou_threshold=0.3)
        self.frameWidth = frameWidth
        self.frameHeight = frameHeight
        self.showDetections = showDetections
        self.detectionThreshold = detectionThreshold
        self.subWindow = subWindow

        # load in our YOLOv4 architecture network
        self.network, self.class_names, self.class_colors = darknet.load_network(
            "FrameAnalyzer/DeepSocial/darknet/cfg/yolov4.cfg",
            "FrameAnalyzer/DeepSocial/darknet/cfg/coco.data",
            "FrameAnalyzer/DeepSocial/DeepSocial.weights")
        # self.class_names = ['person', 'bicycle', 'car', 'motorbike', 'bus', 'truck']
        self.class_names = ['person']
        return

    def ExtractHumans(self, detections):
        """
        Use the given list of detections and return all detections labeled 'person' as DetectedObject[].

        Parameters
        ----------
        detections : [str, float, int, int, int, int]
            list of detections in format [label, confidence, xmin, ymin, xmax, ymax]

        Returns
        -------
        DetectedObject[]
            An array of DetectedObject objects of type 'human'.

        """

        detected = []
        if len(detections) > 0:  # At least 1 detection in the image and check detection presence in a frame
            idList = []
            id = 0
            # check if the detection-class is in the class_names list (in our case only 'person')
            for label, confidence, bbox in detections:
                if label in self.class_names:
                    xmin, ymin, xmax, ymax = darknet.bbox2points(bbox)
                    id += 1
                    if id not in idList:
                        idList.append(id)
                    detected.append(
                        [int(xmin), int(ymin), int(xmax), int(ymax), float(idList[-1]), float(confidence)])
        return np.array(detected)

    def GetHumanPositions(self, inputFrame, frameIndex: int):
        """
        Use the given frame and frameIndex to detect objects and return them as DetectedObject[].

        Parameters
        ----------
        inputFrame : numpy.ndarray
            The frame that is analyzed.
        frameIndex : int
            The index of the frame being analyzed.

        Returns
        -------
        DetectedObject[]
            An array of DetectedObject objects of type 'human'.
        """

        if inputFrame is None:
            return [], frameIndex
        image = inputFrame.copy()

        detectedObjects = []

        detections, widthRatio, heightRatio = darknet_helper(image, self.frameWidth, self.frameHeight, self.network,
                                                             self.class_names, self.detectionThreshold)
        detectedHumans = self.ExtractHumans(detections)

        trackedBoxesIds = self.tracker.update(detectedHumans) if len(detectedHumans) != 0 else detectedHumans

        detectionImage = image
        for box in trackedBoxesIds:
            xmin, ymin, xmax, ymax, id = [int(x) for x in box]
            # check if the bottom of the box is on the lower edge of the video
            if self.frameHeight - ymax > 5:
                # for now label is set to human, TODO: change to real label
                detectedObjects.append(DetectedObject(box[2], box[3], id, "human"))
                if self.showDetections and self.subWindow is not None:
                    id = str(id)
                    # drawing boxes around the tracked objects
                    cv2.rectangle(detectionImage, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)
                    cv2.rectangle(detectionImage, (xmin, ymin - 13), (xmin + len(id) * 10, ymin), (0, 200, 255), -1)
                    cv2.putText(detectionImage, id, (xmin + 2, ymin - 2), cv2.FONT_HERSHEY_SIMPLEX, .4, (0, 0, 0), 1,
                                cv2.LINE_AA)

        if self.subWindow is not None:
            self.subWindow.ShowFrame(detectionImage)

        return detectedObjects, frameIndex  # output: [x,y,id,label], frameIndex

    def Close(self):
        pass

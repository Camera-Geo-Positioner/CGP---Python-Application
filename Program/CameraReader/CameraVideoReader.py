# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software Project course.
# © Copyright Utrecht University (Department of Information and Computing Sciences)

"""
The Camera Video Reader is a buffer-less VideoCapture object. It constantly reads video and returns the latest frame.
"""
import threading
import time
import cv2
from datetime import datetime


class VideoCapture:
    """A buffer-less VideoCapture object"""
    # videoCapture object variables
    captureObject: cv2.VideoCapture = None
    width: int = 0
    height: int = 0
    captureObjectFPS: float = 0
    fileOrStreamLocation: str = None

    # stream reading variables
    readingThread: threading.Thread = None
    status: bool = True
    isStream: bool = False
    readingStream: bool = False
    paused: bool = False

    # frame variables
    hasFrame: threading.Condition = None
    lastFrame = None
    frameIndex: int = 0
    frameReadDatetime: datetime = 0
    currentFrameTime: float = 0
    previousFrameTime: float = 0

    def __init__(self):
        # videoCapture object variables
        self.captureObject = None
        self.width = 0
        self.height = 0
        self.captureObjectFPS = 0
        self.fileOrStreamLocation = None

        # stream reading variables
        self.readingThread = None
        self.status = True
        self.isStream = False
        self.readingStream = False
        self.paused = False

        # frame variables
        self.hasFrame = threading.Condition()
        self.lastFrame = None
        self.frameIndex = 0
        self.previousFrameTime = 0
        self.currentFrameTime = 0

    def ConnectCaptureObject(self, fileOrStreamLocation: str, isStream: bool):
        """
        Connect to a camera object or video file and start reading a stream from it.

        Parameters
        ----------
        fileOrStreamLocation : str
            The location of the camera or video file
        isStream : bool
            Checks if the data is a stream or not
        """
        self.fileOrStreamLocation = fileOrStreamLocation
        self.isStream = isStream

        # open the capture object
        self.captureObject = cv2.VideoCapture(fileOrStreamLocation)
        if not self.captureObject.isOpened():
            print("Could not open CaptureObject")
            return
        self.width = self.captureObject.get(3)
        self.height = self.captureObject.get(4)
        self.captureObjectFPS = self.captureObject.get(cv2.CAP_PROP_FPS)

        # check if the capture object is a real-time video stream
        if str.startswith(fileOrStreamLocation, "rtsp://") or\
           str.startswith(fileOrStreamLocation, "http://") or\
           str.startswith(fileOrStreamLocation, "https://"):
            isStream = True

        # Frame times
        self.currentFrameTime = time.time()
        self.previousFrameTime = self.currentFrameTime
        self.readingStream = True

        # Start reading thread
        if isStream:
            self.readingThread = threading.Thread(target=self._ReadStream)
            self.readingThread.daemon = True
            self.readingThread.start()
        else:
            self.readingThread = threading.Thread(target=self._ReadVideo)
            self.readingThread.daemon = True
            self.readingThread.start()

    def ReleaseCaptureObject(self):
        """
        Release the capture object and stop reading the stream.

        Returns
        -------
        bool
            Returns True if the release was successful
        """
        if self.captureObject is None:
            return False

        # Stop reading thread
        self.readingStream = False
        if self.readingThread is not None:
            self.readingThread.join()
        self.readingThread = None

        # Stop capture object
        status = self.captureObject.release()
        self.captureObject = None
        print('Capture Object disconnected')

        return status

    def _ReadStream(self):
        """Thread to read frames from a stream."""
        while self.readingStream:
            self.previousFrameTime = self.currentFrameTime
            self._SingleRead()
            self.frameIndex += 1
            time.sleep(0.003)

    def _SingleRead(self):
        """Read a single frame from the captureObject."""
        (status, lastFrame) = self.captureObject.read()
        with self.hasFrame:
            self.status = status
            self.lastFrame = lastFrame
            self.frameReadDatetime = datetime.now()
            self.hasFrame.notify()

    def _ReadVideo(self):
        """Thread to continuously read frames from a video."""
        self._SingleRead()

        timeForFrame = 1 / self.captureObjectFPS
        while self.readingStream:
            # Check if paused
            if self.paused:
                time.sleep(0.01)
                continue

            self.previousFrameTime = self.currentFrameTime
            if time.time() - self.currentFrameTime > timeForFrame:
                self.frameIndex += 1
                self._SingleRead()
                self.currentFrameTime = time.time()
            time.sleep(0.003)

    def ReadLastFrame(self):
        """
        Return the last frame read from the camera or video.

        Returns
        -------
        bool, Frame, int
            The status of the Frame,
            the Frame itself,
            the Frame index
        """
        with self.hasFrame:
            self.hasFrame.wait()
            return self.status, self.lastFrame, self.frameIndex, self.frameReadDatetime

    def GetWidth(self):
        """
        Get the width of the camera object

        Returns
        -------
        int
        """
        return self.width

    def GetHeight(self):
        """
        Get the height of the camera object

        Returns
        -------
        int
        """
        return self.height

    def IsOpened(self):
        """
        Check if the captureObject is opened

        Returns
        -------
        bool
        """
        if self.captureObject is None:
            return False
        return self.captureObject.isOpened()

    def GetFPS(self):
        """
        Get the current reading fps and the fps of the captureObject

        Returns
        -------
        int, int
            The build in fps,
            the current fps
        """
        fps = 0
        if self.currentFrameTime is not self.previousFrameTime:
            fps = 1.0 / (self.currentFrameTime - self.previousFrameTime)
        return fps, self.captureObjectFPS

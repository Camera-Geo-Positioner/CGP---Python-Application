# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software Project course.
# © Copyright Utrecht University (Department of Information and Computing Sciences)


from CameraReader.CameraVideoReader import *


def test_NormalVideo():
    cameraReader = VideoCapture()

    # Load video
    cameraReader.ConnectCaptureObject('Testing/Assets/testVideo.mp4', False)
    if not cameraReader.IsOpened():
        cameraReader.ConnectCaptureObject('Program/Testing/Assets/testVideo.mp4', False)
    if not cameraReader.IsOpened():
        raise TypeError('No testVideo file')

    # Check size
    assert cameraReader.GetWidth() == 1920
    assert cameraReader.GetHeight() == 1080

    # Check fps
    fps, NormalFPS = cameraReader.GetFPS()
    assert int(NormalFPS) == 60

    # Read last Frame
    status, frame, index, frameReadDatetime = cameraReader.ReadLastFrame()

    # Check status
    assert status

    # Release
    cameraReader.ReleaseCaptureObject()


def test_NormalStream():
    cameraReader = VideoCapture()

    # Load video
    cameraReader.ConnectCaptureObject('Testing/Assets/testVideo.mp4', True)
    if not cameraReader.IsOpened():
        cameraReader.ConnectCaptureObject('Program/Testing/Assets/testVideo.mp4', True)
    if not cameraReader.IsOpened():
        raise TypeError('No testVideo file')

    # Check size
    assert cameraReader.GetWidth() == 1920
    assert cameraReader.GetHeight() == 1080

    # Check fps
    fps, NormalFPS = cameraReader.GetFPS()
    assert int(NormalFPS) == 60

    # Read last Frame
    status, frame, index, frameReadDatetime = cameraReader.ReadLastFrame()

    # Check status
    assert status

    # Release
    cameraReader.ReleaseCaptureObject()


# Test the fps function on divide by zero
def test_FPS():
    cameraReader = VideoCapture()
    cameraReader.currentFrameTime = 1
    cameraReader.previousFrameTime = 1
    fps, objectFPS = cameraReader.GetFPS()

    assert fps == 0
    assert objectFPS == 0

    cameraReader.previousFrameTime = 0

    fps, objectFPS = cameraReader.GetFPS()

    assert fps == 1
    assert objectFPS == 0

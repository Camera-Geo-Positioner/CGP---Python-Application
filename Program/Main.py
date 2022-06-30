# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software Project course.
# © Copyright Utrecht University (Department of Information and Computing Sciences)

# %%
import argparse
import asyncio
import concurrent.futures
import threading
import cv2

import aioconsole
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict
from datetime import datetime, time

from API.APIController import APIController
from CameraReader.CameraController import CameraController
from Positioner.Accuracy.StaticAccuracyDataset import StaticAccuracyDataset
from Windowing.Sub.CameraSubWindow import CameraSubWindow
from Windowing.MasterWindow import *
from FrameAnalyzer.IDetector import IDetector
from FrameAnalyzer.MainFrameAnalyzer import MainFrameAnalyzer
from FrameAnalyzer.DetectionFactory import DetectionFactory
from Positioner.Convertors import Convertors
from Positioner.DetectedObjectPosition import DetectedObjectPosition
from Positioner.IConvertor import IConvertor
from Positioner.MainPositioner import MainPositioner
from Calibrator.MainCalibrator import MainCalibrator
from ArgsGUI import UserArgsInput

# events
calibrationDoneEvent: threading.Event = threading.Event()
videoAnalyzerCancelEvent: threading.Event = threading.Event()


async def CommandInput(api: APIController):
    """
    Async console input handler. Reads from the console and handles these inputs.

    Parameters
    ----------
    api : APIController
        The api used for sending data, here only used for testing
    """

    try:
        calibrationDoneEvent.wait()

        while True:
            command = await aioconsole.ainput()
            if command == "exit":
                break
            if command == "test":
                api.Send([DetectedObjectPosition(2, 3, 6, 1, 'human')], 0, datetime.now())
    except concurrent.futures.CancelledError:
        return


class Program:
    # objects
    api: APIController

    # tasks
    inputTask: Any
    apiTask: Any
    videoAnalyzerTask: Any
    arguments: Dict[str, Any]

    def __init__(self):
        self.api = None
        self.inputTask = None
        self.apiTask = None
        self.videoAnalyzerTask = None
        self.arguments = None

    @staticmethod
    def ValidateAllArguments(arguments: Dict[str, Any]):
        """
        Validate all arguments.

        Parameters
        ----------
        arguments : Dict[str, Any]
            The arguments to be validated

        Returns
        -------
        bool
            True if arguments are correct, otherwise false
        """
        try:
            APIController.ValidateApiArguments(arguments)
            CameraController.ValidateReaderArguments(arguments)
            MainFrameAnalyzer.ValidateFrameAnalyzerArguments(arguments)
            MainCalibrator.ValidateCalibratorArguments(arguments)
            StaticAccuracyDataset.ValidateStaticAccuracyDatasetArguments(arguments)
        except (ValueError, TypeError) as e:
            print(e)
            return False
        return True

    def ParseArguments(self):
        """
        Parse the arguments

        Returns
        -------
        Dict[str, Any]
            The arguments as a dictionary
        """
        # Create the argument parser
        argumentParser = argparse.ArgumentParser()

        # Add arguments
        APIController.AddApiArguments(argumentParser)
        CameraController.AddVideoReaderArguments(argumentParser)
        MainFrameAnalyzer.AddFrameAnalyzerArguments(argumentParser)
        MainCalibrator.AddCalibratorArguments(argumentParser)
        StaticAccuracyDataset.AddStaticAccuracyDatasetArguments(argumentParser)
        UserArgsInput.UserArgsInput().AddArgsGUIArguments(argumentParser)

        # Parse all arguments
        arguments = vars(argumentParser.parse_args())

        # Validate all arguments
        if not self.ValidateAllArguments(arguments):
            return None

        if arguments['displayArgsGUI']:
            arguments = UserArgsInput.UserArgsInput().GetArgsFromUser(arguments)

        self.arguments = arguments
        return arguments

    async def Main(self):
        """
        The start of the program.
        The main async function of the program,
        starts all other async functions and cancels them when the program exits.
        Also creates the api used for sending data.
        """

        # Start everything
        await self._Startup()

        # Wait for video input to stop
        await asyncio.wait([self.apiTask, self.inputTask, self.videoAnalyzerTask], return_when=asyncio.FIRST_COMPLETED)

        # Clean everything
        await self._Cleanup()

    async def _Startup(self):
        """Creation of all the tasks for the program."""

        loop = asyncio.get_running_loop()
        executor = ThreadPoolExecutor(1)

        if self.arguments is None:
            self.ParseArguments()

        # Setup API
        self.api = APIController(loop, not self.arguments["noEncryption"])
        self.apiTask = loop.create_task(self.api.Start(self.arguments["port"]))
        await self.api.UntilConnected()

        # Setup positioner pipeline
        pipeline = PositionerPipeline()
        self.videoAnalyzerTask = loop.run_in_executor(
            executor, pipeline.RunPipeline, self.api, self.arguments)

        # Setup input loop
        self.inputTask = loop.create_task(CommandInput(self.api))

    async def _Cleanup(self):
        """Cleaning up all the tasks of the program."""

        print("Stopping...")

        # Cleanup, stop all other async functions
        self.inputTask.cancel()
        self.api.Stop()
        videoAnalyzerCancelEvent.set()

        # Wait till all other async functions are correctly finished
        await asyncio.gather(self.apiTask, self.videoAnalyzerTask, self.inputTask)


class PositionerPipeline:
    """Separate Positioner Pipeline Object"""

    cameraController: CameraController = None
    mainWindow: MasterWindow = None
    frameAnalyzer: MainFrameAnalyzer = None
    detector: IDetector

    def __init__(self):
        self.cameraController = None
        self.mainWindow = None
        self.frameAnalyzer = None
        self.detector = None

    def RunPipeline(self, api: APIController, arguments: Dict[str, Any]):
        """
        Pipeline that builds all objects needed for the detection, tracking and positioning of object in a frame.

        Parameters
        ----------
        api : APIController
            The API used in the pipeline.
        arguments : Dict[str, Any]
            The arguments used to run the pipeline
        """

        # Start positioner pipeline
        self._Startup(api, arguments)

        # Start FrameAnalyzer and Positioner
        if not videoAnalyzerCancelEvent.is_set():
            self.cameraController.StartVideoAnalyzer(self.frameAnalyzer, arguments['analyzeWidth'],
                                                     arguments['analyzeHeight'], videoAnalyzerCancelEvent)

        # stop positioner pipeline
        self._Cleanup()

    def _Startup(self, api: APIController, arguments: Dict[str, Any]):
        """
        The startup for the positioner pipeline, builds and connects all pipeline objects.

        Parameters
        ----------
        api : APIController
            The API used in the pipeline.
        arguments : Dict[str, Any]
            The arguments used to create the pipeline.
        """

        # Setup master window
        self.mainWindow = MasterWindow(1080, 640, "CGP - Python Applicatie")
        self.mainWindow.Open(True, videoAnalyzerCancelEvent)

        # Setup Camera
        self.cameraController = CameraController()
        connected = self.cameraController.StartVideoReader(arguments)
        if not connected:
            self._Cleanup()
            return

        # Grab the last from the camera controller for calibration
        image = self.cameraController.videoReader.ReadLastFrame()[1]
        image = cv2.resize(image, (arguments['analyzeWidth'], arguments['analyzeHeight']))

        # Pause the video controller
        self.cameraController.videoReader.paused = True

        # Calibrate, retrieve the chosen calibration configuration
        calibrationConfiguration = MainCalibrator.Calibrate(
            self.cameraController.GetUniqueIdentifier(),
            image,
            self.mainWindow,
            arguments
        )

        if calibrationConfiguration is None and not MainCalibrator.calibrated:
            print('Calibration failed, forcefully exiting...')
            self._Cleanup()
            return

        # Resume the video controller
        self.cameraController.videoReader.paused = False

        # Setup convertor and positioner
        if calibrationConfiguration is not None:
            converterSubWindow = CameraSubWindow()
            self.mainWindow.rightSubWindow = converterSubWindow
            convertor = Convertors[type(calibrationConfiguration)](calibrationConfiguration, converterSubWindow)
        else:
            convertor = IConvertor(None)
        calibrationDoneEvent.set()

        # create sub window
        detectionSubWindow = CameraSubWindow()
        self.mainWindow.leftSubWindow = detectionSubWindow

        # Setup Pipeline
        positioner = MainPositioner(convertor, api, True)
        dataWriteConnection = positioner
        self.detector = DetectionFactory.CreateDetector(arguments, videoAnalyzerCancelEvent, detectionSubWindow)
        self.frameAnalyzer = MainFrameAnalyzer(self.detector, dataWriteConnection)

    def _Cleanup(self):
        """Cleans the pipeline when it is closed."""

        # set events
        calibrationDoneEvent.set()
        videoAnalyzerCancelEvent.set()

        # close camera
        if self.cameraController.videoReader is not None:
            self.cameraController.videoReader.paused = False

        if self.mainWindow is not None:
            self.mainWindow.Close()

        if self.detector is not None:
            self.detector.Close()

        self.cameraController.StopVideoReader()


if __name__ == '__main__':
    program = Program()
    mainArguments = program.ParseArguments()

    if mainArguments is not None:
        if mainArguments["calibrateDataSet"] is "":
            asyncio.run(program.Main())
        else:
            StaticAccuracyDataset.RunStaticAccuracyDataSet(mainArguments)
        print("Done")

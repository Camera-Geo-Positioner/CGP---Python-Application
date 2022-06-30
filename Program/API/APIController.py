# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software Project course.
# © Copyright Utrecht University (Department of Information and Computing Sciences)

"""
API Controller, uses and is the control object of the API Server.
"""

import asyncio
from datetime import datetime, tzinfo
import json
import pathlib
from typing import List, Dict, Any

from API.APIServer import APIServer
from Positioner.DetectedObjectPosition import DetectedObjectPosition
import argparse
import socket


class APIController:
    """Controller object for the API"""
    server: APIServer = None

    def __init__(self, loop, encryption=False):
        """
        Constructor for the APIController.

        Parameters
        ----------
        loop : Any
            The loop used to create futures
        encryption : bool
            Check if the encryption is used
        """
        if not encryption:
            print("WARNING: API Encryption disabled!")
        if loop is None:
            raise TypeError("No loop given, need a loop to create futures.")
        self.server = APIServer(loop, pathlib.Path(__file__) if encryption else None)

    @staticmethod
    def AddApiArguments(parser: argparse.ArgumentParser):  # pragma: no cover
        """
        Parse the default API Controller arguments.

        Parameters
        ----------
        parser : argparse.ArgumentParser
            The parser that parses the arguments
        """

        if parser is None:
            raise TypeError("Parser is none.")

        parser.add_argument("-p", "--port",
                            type=int,
                            default="8080",
                            help="port of the API server")
        parser.add_argument("-ne", "--noEncryption", action="store_true", default=False)

    @staticmethod
    def ValidateApiArguments(arguments: Dict[str, Any]):
        """
        Validate the parsed arguments.

        Parameters
        ----------
        arguments : Dict[str, Any]
            The arguments that are validated
        """
        if arguments is None or not arguments:
            raise TypeError("Arguments are empty or None.")
        # Define port for further use
        port = arguments["port"]
        # Test if port is a number
        if not isinstance(port, int):
            raise TypeError(f"Port {port} is not a number.")
        # Test if port is within range
        if port < 1024 or port > 65535:
            raise ValueError(f"Port {port} out of range. Please choose a port between 1024-65535.")
        # Create temporary socket and check whether port is in use or not
        testSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            testSock.bind(("127.0.0.1", port))
            connectionFailed = False
        except:
            connectionFailed = True
        if connectionFailed:
            raise RuntimeError(f"Port {port} already in use. Please choose a different port")
        testSock.close()

    async def Start(self, port=8080, interface=""):
        """
        Start the API server

        Parameters
        ----------
        port : int
            The port the API server should listen on
        interface : str
            The interface the API server should listen on
        """
        print("Starting API...")
        await self.server.Start(port, interface)

    def UntilConnected(self):
        """
        Check if the API server has connected to the port

        Returns
        -------
        asyncio.Future
        """
        return self.server.UntilConnected()

    def Stop(self):
        """Stop the API server"""
        self.server.Stop()

    def Send(self, detectedObjects: List[DetectedObjectPosition], frameIndex: int, frameTimeStamp: datetime = None):
        """
        Send DetectedObjectPosition[] data to all the clients connected to the API

        Parameters
        ----------
        detectedObjects : List[DetectedObjectPosition]
            The DetectedObjectPosition[] data to be broadcast
        frameIndex : int
            The index of the frame belonging to the DetectedObjectPosition[] data
        frameTimeStamp : datetime
            The time at which this frame was received, including the current timezone
        """
        if detectedObjects is None:
            return
        data = {
            "frameIndex": frameIndex,
            "frameTimeStamp":
                frameTimeStamp.astimezone().isoformat() if frameTimeStamp is not None
                else '0001-01-01T00:00:00',
            "sentTimeStamp": datetime.now().astimezone().isoformat(),
            "detectedObjects": [{key: value for key, value in detectedObject._asdict().items() if value is not None}
                                for detectedObject in detectedObjects]
        }
        self.server.BroadcastData(json.dumps(data))

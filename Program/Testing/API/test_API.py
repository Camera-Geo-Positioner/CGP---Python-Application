# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software Project course.
# © Copyright Utrecht University (Department of Information and Computing Sciences)

from API.APIController import *
from API.APIServer import *
from Positioner.DetectedObjectPosition import DetectedObjectPosition
import asyncio
from pytest import raises
import random
from datetime import datetime
import pytest
import socket


port = random.randint(8000, 10000)
interface = "localhost"

objects = [DetectedObjectPosition(-4, 3, 10, 1, 'human'), DetectedObjectPosition(5, 0.274, 3, 3, 'human')]
date = '2022-05-03T16:15:46.663021+02:00'
date = datetime.fromisoformat(date)
data = {"frameIndex": 1, "frameTimeStamp": date.astimezone().isoformat(),
        "detectedObjects": [{key: value for key, value in detectedObject._asdict().items()
                            if value is not None} for detectedObject in objects]}


# The API with normal input
def test_Normal():
    # Create testClients in separate thread
    testClient1 = TestClient()
    testClient2 = TestClient()

    # Run the server
    asyncio.run(RunServer([objects], [testClient1, testClient2], port))

    # Check data
    for message in testClient1.messages:
        messageData = json.loads(message)
        for k, v in data.items():
            assert messageData[k] == v
    for message in testClient2.messages:
        messageData = json.loads(message)
        for k, v in data.items():
            assert messageData[k] == v


# Check the crash when there is no loop in the construction of the API
def test_NoLoop():
    raises(TypeError, APIController, None, False)


# Check how the API handles Null Messages
def test_NoMessage():
    # Run the server
    asyncio.run(RunServer([None], [], port + 1))


# Check how the API handles no clients
def test_NoClients():
    # Run the server
    asyncio.run(RunServer([objects], [], port + 2))


# Check if the argument parser handles None
def test_add_api_arguments_none():
    pytest.raises(TypeError, APIController.AddApiArguments, None)


# Different combinations of arguments to be checked
validate_reader_arguments_data = [
    ({"port": 23}, ValueError),
    ({"port": 65537}, ValueError),
    ({"port": "poortnummer"}, TypeError),
    ({}, TypeError),
    (None, TypeError)]


# Check if proper exceptions are raised
@pytest.mark.parametrize("arguments,expected", validate_reader_arguments_data)
def test_validate_reader_arguments(arguments, expected):
    pytest.raises(expected, APIController.ValidateApiArguments, arguments)


# Check if the argument parser throws an exception if the chosen port is already in use
def test_already_in_use():
    testSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    poort = random.randint(10000, 11000)
    try:
        testSock.bind(("127.0.0.1", poort))
    except:
        pytest.fail("Failed test: test port already in use")
    pytest.raises(RuntimeError, APIController.ValidateApiArguments, {"port": poort})
    testSock.close()


async def RunServer(messages: [[DetectedObjectPosition]], clients, port):
    api = APIController(asyncio.get_running_loop(), False)
    loop = asyncio.get_running_loop()
    task = loop.create_task(api.Start(port, interface))
    await api.UntilConnected()

    # Start client threads
    clientTasks = []
    for client in clients:
        clientTasks.append(loop.create_task(client.Connect(port, interface)))

    # Wait till all clients are connected
    while len(api.server.clients) < len(clients):
        await asyncio.sleep(1)

    for message in messages:
        api.Send(message, 1, date)

    # Stop the server
    api.Stop()
    await task

    # Close clients
    if len(clients) > 0:
        await asyncio.wait(clientTasks, timeout=3)


# get a loop
async def GetLoop():
    return asyncio.get_running_loop()


# A simple test client that receives 1 message at a time
class TestClient:
    messages = []

    def __init__(self):
        self.messages = []

    # Connect to a server and receive 1 message
    async def Connect(self, port, interface):
        async with websockets.connect("ws://{0}:{1}".format(interface, port)) as websocket:
            message = await websocket.recv()
            self.messages.append(message)
            print(message)

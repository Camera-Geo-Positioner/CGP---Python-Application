# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software Project course.
# © Copyright Utrecht University (Department of Information and Computing Sciences)

"""
API Server, creates a connection to a http socket and sends and receives messages from this socket.
"""

import asyncio
import json
import pathlib
import ssl
from typing import Optional

import websockets
from websockets.exceptions import ConnectionClosedOK, ConnectionClosedError


class APIServer:
    """A WebSocket server that can broadcast data to all connected clients"""
    clients: set = set()
    sslContext: ssl.SSLContext = None

    def __init__(self, loop, serverCertificateFolder: Optional[pathlib.Path]):
        """
        Initializes the server, but doesn't start it yet (See `Start` for that)

        Parameters
        ----------
        loop : Any
            a loop to create futures
        serverCertificateFolder : Optional[pathlib.Path]
            Optional path to the folder containing a file named 'server.pem'
            The 'server.pem' is the certificate this server should use for TLS connections.
            When `None`, the server uses the raw WebSocket protocol without encryption
        """
        if serverCertificateFolder:     # pragma: no cover
            self.sslContext = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            self.sslContext.load_cert_chain(serverCertificateFolder.with_name('server.pem'))
            self.sslContext.verify_mode = ssl.CERT_REQUIRED
            self.sslContext.load_verify_locations(cafile=serverCertificateFolder.with_name('ca.crt'))
        self.connectFuture = loop.create_future()
        self.doneFuture = loop.create_future()

    async def Start(self, port=8080, interface=""):
        """
        Starts the server and waits till the server is correctly started.

        Parameters
        ----------
        port : int
            The port the server should connect to
        interface : str
            The interface of the server
        """
        async with websockets.serve(self._ClientHandler, interface, port, ssl=self.sslContext):
            print("Server started, connected to port: " + str(port))
            self.connectFuture.set_result(True)
            await self.doneFuture

    def UntilConnected(self):
        """
        Check if the server is connected to the assigned port.

        Returns
        -------
        asyncio.Future
        """
        return self.connectFuture

    def Stop(self):
        """Stop the API server."""
        self.doneFuture.set_result(None)

    async def _ClientHandler(self, websocket: websockets.WebSocketServerProtocol):  # pragma: no cover
        """
        The client handler, handles the massages from individual clients.

        Parameters
        ----------
        websocket: The websocket the client is connected to
        """
        identifier = websocket.remote_address
        if self.sslContext is not None:
            # Get the client certificate
            certificate = websocket.transport.get_extra_info("ssl_object").getpeercert()
            # certificate['subject'] is a tuple, convert to a dictionary
            subject = dict(x[0] for x in certificate['subject'])
            identifier = f'{subject["commonName"]}@{identifier}'

        print(f'Connection by {identifier}')

        try:
            self.clients.add(websocket)
            isOpen = True
            while isOpen:
                message = await websocket.recv()
                isOpen = await self._OnClientCommand(websocket, json.loads(message))
            print(f'Connection from {identifier} closed by exit command')
        except ConnectionClosedOK:
            print(f'Connection from {identifier} closed')
        except ConnectionClosedError as e:
            print(f'Connection from {identifier} closed incorrectly: {e}')
        finally:
            self.clients.remove(websocket)  # Removes the client from the set if it was already added

    async def _OnClientCommand(self, websocket: websockets.WebSocketServerProtocol, command):  # pragma: no cover
        """
        Function to handle client messages, used by the _ClientHandler.

        Parameters
        ----------
        websocket : websockets.WebSocketServerProtocol
            The websocket the client is connected to
        command : str|dict
            The command that was sent by the client
        """
        if command is not dict or 'type' not in command:
            return True

        if command['type'] == 'exit':
            return False
        return True

    def BroadcastData(self, data):
        """
        Broadcast data to all the currently connected clients.

        Parameters
        ----------
        data : Any
            The data to be broadcast to the clients
        """
        websockets.broadcast(self.clients, data)

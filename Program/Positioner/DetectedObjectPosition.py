# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software Project course.
# © Copyright Utrecht University (Department of Information and Computing Sciences)

"""
The actual object created by the convertors and that is sent through the API.
"""

from typing import NamedTuple, Optional


class DetectedObjectPosition(NamedTuple):
    """Denotes the 3D position of a detected object"""
    latitude: float
    """The latitude of the object in WGS-84 degrees"""
    longitude: float
    """The longitude of the object in WGS-84 degrees"""
    altitude: float
    """The height of the object in meters"""
    id: int
    """A unique identifier of the object"""
    type: str
    """A string denoting the detected type of the object, for example 'human'"""
    locationRadius: Optional[float] = None
    """The accuracy of the given 3D location, given by a radius in meters"""
    rijksdriehoekX: Optional[float] = None
    """The x coordinate of the object in Rijksdriehoek coordinates"""
    rijksdriehoekY: Optional[float] = None
    """The y coordinate of the object in Rijksdriehoek coordinates"""

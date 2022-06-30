# This program has been developed by students from the bachelor Computer
# Science at Utrecht University within the Software Project course.
# © Copyright Utrecht University (Department of Information
# and Computing Sciences)

import sys
import pathlib


def AssureAbsolutePath(path) -> pathlib.Path:
    """
    Assure a given path is absolute.
    """

    # Convert path to pathlib path
    path = pathlib.Path(path)

    # Check if the given path is relative, if so, make it absolute
    # given the root of the project directory
    if not path.is_absolute():
        # Get project root path
        root = pathlib.Path(__file__).parent.parent

        path = root / path

    # Create pathlib path from the given path
    return path


def GetDataPath() -> pathlib.Path:
    """
    Get the data directory for each specific platform.
    """

    home = pathlib.Path.home()
    result = None
    if sys.platform == "win32":
        result = home / "AppData/Roaming"
    elif sys.platform == "linux":
        result = home / ".local/share"
    elif sys.platform == "darwin":
        result = home / "Library/Application Support"
    result = AssureAbsolutePath(str(result / "WatchfulEye"))

    # Make sure the result directory exists
    if not result.exists():
        result.mkdir(parents=True)
    return result

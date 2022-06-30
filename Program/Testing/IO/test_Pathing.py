# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software Project course.
# © Copyright Utrecht University (Department of Information and Computing Sciences)

import os

from IO.Pathing import *


class TestPathing:
    def test_AssureAbsolutePath(self):
        # Assume a relative path
        relativeTestPath = "Testing/"
        absoluteTestPath = AssureAbsolutePath(relativeTestPath)

        # Check if different
        assert relativeTestPath is not str(absoluteTestPath), "The relative and absolute path are the same."

        # Check if a correct path
        assert os.path.isabs(absoluteTestPath), "The path is not an absolute path."

    def test_GetDataPath(self):
        # Get the data path
        dataPath = GetDataPath()

        # Check if it is a correct path
        assert os.path.isabs(dataPath), "The data path is not an absolute path."

        # Check if it matches the system
        if sys.platform == "win32":
            assert str(dataPath).__contains__('AppData'), "The data path does not contain the AppData folder."
        elif sys.platform == "linux":
            assert str(dataPath).__contains__('local'), "The data path does not contain the local folder."
        elif sys.platform == "darwin":
            assert str(dataPath).__contains__('Application Support'), \
                "The data path does not contain the Application Support folder."

# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software Project course.
# © Copyright Utrecht University (Department of Information and Computing Sciences)

import json
import os
from types import SimpleNamespace


class SerializableJSON:
    def ToJSON(self, path, indentation=None):
        """
        Parse the object values to a JSON file at the specified path.
        """

        # Parse to JSON and write to file
        jsonString = json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=indentation)
        with open(path, 'w') as file:
            file.write(jsonString)

    def FromJSON(self, path):
        """
        Read a JSON file from the specified path and parses the values to the object.
        """

        # Check if the file exists
        if not os.path.isfile(path):
            raise FileNotFoundError("The file does not exist")

        # Load the file
        with open(path, 'r') as file:
            jsonString = file.read()
            jsonObject = json.loads(jsonString)
            self.__dict__.update(jsonObject)

    @staticmethod
    def ParseToSimpleNamespace(data):
        """"
        Parse the object values to a SimpleNamespace object.

        Parameters
        ----------
        data : dict
            The dictionary to parse.

        Returns
        -------
        SimpleNamespace
            The parsed SimpleNamespace object.
        """

        return json.loads(data, object_hook=lambda d: SimpleNamespace(**d))

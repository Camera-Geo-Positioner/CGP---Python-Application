# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software Project course.
# © Copyright Utrecht University (Department of Information and Computing Sciences)

"""
Interface for getting the args with a GUI.
"""

import abc
from typing import Dict


class IArgsWindow:

    @abc.abstractmethod
    def GetArgsFromUser(self, currentArguments) -> Dict[str, any] or None:
        raise NotImplementedError()

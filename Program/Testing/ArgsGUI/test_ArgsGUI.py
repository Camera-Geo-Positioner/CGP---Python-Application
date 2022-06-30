# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software Project course.
# © Copyright Utrecht University (Department of Information and Computing Sciences)

import pytest
from unittest.mock import Mock
from ArgsGUI import UserArgsInput
from ArgsGUI.UserArgsInput import UserArgsInput


class TestArgsGUI:
    def test_OnClosing(self):
        x = Mock()
        x.closed = False

        UserArgsInput.OnClosing(x)

        assert x.closed

    @pytest.mark.parametrize("test_APIPortEntry", [-101, -100, -1, 0, 123, 10000, 10001])
    @pytest.mark.parametrize("test_minValue", [-100, -1, 0, 1, 100, 10000, 9999])
    @pytest.mark.parametrize("test_maxValue", [-100, -1, 0, 1, 100, 10000, 9999])
    def test_ValidateInteger_valid(self, test_APIPortEntry, test_minValue, test_maxValue):
        x = Mock()
        x.testing = True
        entry = Mock()
        entry.get = Mock(return_value=str(test_APIPortEntry))

        if test_minValue < test_APIPortEntry < test_maxValue:
            assert UserArgsInput.ValidateInteger(x, entry, test_minValue, test_maxValue)
        else:
            assert not UserArgsInput.ValidateInteger(x, entry, test_minValue, test_maxValue)

    @pytest.mark.parametrize("test_APIPortEntry", [None, False, True, 6.456, ['a', 'b', 6], 'cat', 2.000009])
    def test_ValidateInteger_invalid(self, test_APIPortEntry):
        x = Mock()
        x.testing = True
        entry = Mock()
        entry.get = Mock(return_value=str(test_APIPortEntry))

        assert not UserArgsInput.ValidateInteger(x, entry, 0, 10000)

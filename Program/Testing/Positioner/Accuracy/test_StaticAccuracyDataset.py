# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software Project course.
# © Copyright Utrecht University (Department of Information and Computing Sciences)

import argparse
from unittest.mock import Mock
from Positioner.Accuracy.StaticAccuracyDataset import StaticAccuracyDataset, StaticAccuracyError


class TestStaticAccuracyDataset:
    def test_GetConfigurationCalibration(self):
        # Any dictionary object in the dataset configuration list
        # should be converted to a simple namespace object, even if nested
        dataset = StaticAccuracyDataset()
        dataset.calibrationConfigurations["test"] = {"test": "test"}
        convertedConfiguration = dataset.GetCalibrationConfiguration("test")
        assert convertedConfiguration.test == "test", "The configuration was not converted to a namespace object"

    def test_Load(self):
        StaticAccuracyDataset.FromJSON = Mock()
        assert isinstance(StaticAccuracyDataset.Load(""), StaticAccuracyDataset), "The dataset does not load correctly"

    def test_ArgumentHandling(self):
        parser = argparse.ArgumentParser()
        StaticAccuracyDataset.AddStaticAccuracyDatasetArguments(parser)
        result = vars(parser.parse_args([]))
        assert result["calibrateDataSet"] is not None, \
            "The dataset does not add arguments correctly"
        assert result["calibrateDataSetMethod"] is not None, \
            "The dataset does not add arguments correctly"
        assert StaticAccuracyDataset.ValidateStaticAccuracyDatasetArguments(
            result
        ) is False, "The dataset does not validate arguments correctly"


class TestStaticAccuracyError:
    def test_Add(self):
        error = StaticAccuracyError()
        error.AddError(10)
        error.AverageErrors()

        assert error.averageError == 10, "The average error was not calculated correctly"

        error.AddError(5)
        error.AverageErrors()

        assert error.averageError == 7.5, "The average error was not calculated correctly"
        assert error.GetMaxError() == 10, "Max error not calculated properly"

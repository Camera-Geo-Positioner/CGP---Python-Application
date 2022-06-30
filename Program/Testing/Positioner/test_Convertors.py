# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software Project course.
# © Copyright Utrecht University (Department of Information and Computing Sciences)

from Positioner.Convertors import Convertors
from Calibrator.Configurations.HomographyCalibrationConfiguration import HomographyCalibrationConfiguration
from Positioner.HomographyConverter import HomographyConverter


def test_Convertors():
    # check number convertors
    assert len(Convertors) == 1

    assert Convertors[HomographyCalibrationConfiguration] == HomographyConverter

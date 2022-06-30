# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software Project course.
# © Copyright Utrecht University (Department of Information and Computing Sciences)

"""
Global dictionary for the different conversion methods.
"""

# Homography
from Calibrator.Configurations.HomographyCalibrationConfiguration import HomographyCalibrationConfiguration
from Positioner.HomographyConverter import HomographyConverter

# Others
# ...

# Convertor dictionary
Convertors = {
    HomographyCalibrationConfiguration: HomographyConverter
}

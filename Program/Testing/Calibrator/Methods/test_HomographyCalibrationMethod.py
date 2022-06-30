# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software Project course.
# © Copyright Utrecht University (Department of Information and Computing Sciences)
import pygame_gui
import pytest
import pygame
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from Calibrator.ImageReceiver.SmartImage import SmartImage
from Calibrator.Methods.HomographyCalibrationMethod import HomographyCalibrationMethod
from Windowing.MasterWindow import MasterWindow


class TestHomographyCalibrationMethod:
    calibrator = HomographyCalibrationMethod

    # test if matrices do nothing basically
    @pytest.mark.parametrize("x, y, size", [(20, 20, 50),
                                            (50, 50, 100),
                                            (30.7, 22.46, 126.85),
                                            (0, 0, 10000)])
    def test_TransformationMatrix1(self, x, y, size):
        shape1 = [(0, 0), (size, 0), (size, size), (0, size)]
        shape2 = [(0, 0), (size, 0), (size, size), (0, size)]
        M = self.calibrator.GetTransformationMatrix(shape1, shape2)

        # transform point to topdown pixel coordinates
        x2 = (M[0][0] * x + M[0][1] * y + M[0][2]) / (M[2][0] * x + M[2][1] * y + M[2][2])
        y2 = (M[1][0] * x + M[1][1] * y + M[1][2]) / (M[2][0] * x + M[2][1] * y + M[2][2])
        assert round(x2) == round(x) and round(y2) == round(y), f"crashed for x == {x} and y == {y} and size == {size}."

    # test if matrices do throw exception basically
    @pytest.mark.parametrize("x, y, size", [(30, 30, 0),
                                            (20, 50, -100)])
    @pytest.mark.xfail(raises=Exception)
    def test_TransformationMatrix6(self, x, y, size):
        shape1 = [(0, 0), (size, 0), (size, size), (0, size)]
        shape2 = [(0, 0), (size, 0), (size, size), (0, size)]
        M = self.calibrator.GetTransformationMatrix(shape1, shape2)

    # test if simple rotation works
    def test_TransformationMatrix2(self):
        shape1 = [(0, 0), (100, 0), (100, 100), (0, 100)]
        shape2 = [(100, 0), (100, 100), (0, 100), (0, 0)]
        M = self.calibrator.GetTransformationMatrix(shape1, shape2)
        (x, y) = (25, 25)
        # transform point to topdown pixel coordinates
        x2 = (M[0][0] * x + M[0][1] * y + M[0][2]) / (M[2][0] * x + M[2][1] * y + M[2][2])
        y2 = (M[1][0] * x + M[1][1] * y + M[1][2]) / (M[2][0] * x + M[2][1] * y + M[2][2])
        assert round(x2) == 75 and round(y2) == 25, f"x2 = {x2}, y2 = {y2}. rotation1."

    # test if simple rotation works
    def test_TransformationMatrix3(self):
        shape1 = [(0, 0), (100, 0), (100, 100), (0, 100)]
        shape2 = [(100, 100), (0, 100), (0, 0), (100, 0)]
        M = self.calibrator.GetTransformationMatrix(shape1, shape2)
        (x, y) = (25, 25)
        # transform point to topdown pixel coordinates
        x2 = (M[0][0] * x + M[0][1] * y + M[0][2]) / (M[2][0] * x + M[2][1] * y + M[2][2])
        y2 = (M[1][0] * x + M[1][1] * y + M[1][2]) / (M[2][0] * x + M[2][1] * y + M[2][2])
        assert round(x2) == 75 and round(y2) == 75, f"x2 = {x2}, y2 = {y2}. rotation2."

    # test if matrices scale points well
    @pytest.mark.parametrize("x, y, size, scale", [(20, 20, 50, 1),
                                                   (50, 50, 100, 10),
                                                   (0, 0, 10000, 100)])
    def test_TransformationMatrix4(self, x, y, size, scale):
        shape1 = [(0, 0), (size, 0), (size, size), (0, size)]
        shape2 = [(0, 0), (size * scale, 0), (size * scale, size * scale), (0, size * scale)]
        M = self.calibrator.GetTransformationMatrix(shape1, shape2)

        # transform point to topdown pixel coordinates
        x2 = (M[0][0] * x + M[0][1] * y + M[0][2]) / (M[2][0] * x + M[2][1] * y + M[2][2])
        y2 = (M[1][0] * x + M[1][1] * y + M[1][2]) / (M[2][0] * x + M[2][1] * y + M[2][2])
        assert round(x2) == round(x * scale) and round(y2) == round(y * scale), \
            f"crashed for x == {x} and y == {y} and size == {size} and scale == {scale}."

    # test if matrices scale points well
    @pytest.mark.parametrize("x, y, size, scale", [(30, 30, 50, -1),
                                                   (30, 30, 0, 1),
                                                   (20, 50, -100, 2),
                                                   (20, 50, 100, 0)])
    @pytest.mark.xfail(raises=Exception)
    def test_TransformationMatrix5(self, x, y, size, scale):
        shape1 = [(0, 0), (size, 0), (size, size), (0, size)]
        shape2 = [(0, 0), (size * scale, 0), (size * scale, size * scale), (0, size * scale)]
        self.calibrator.GetTransformationMatrix(shape1, shape2)

    @pytest.mark.parametrize("shape", [[(5, 6), (5, 6)]])
    def test_CheckIfCorrectShape1(self, shape):
        with pytest.raises(Exception) as ex:
            HomographyCalibrationMethod._CheckIfCorrectShape(shape)
        assert "shape not correct" in str(ex.value)

    @pytest.mark.parametrize("shape", [[(-1, 4), (5, -3)]])
    def test_CheckIfCorrectShape2(self, shape):
        with pytest.raises(Exception) as ex:
            HomographyCalibrationMethod._CheckIfCorrectShape(shape)
        assert "shape out of bounds" in str(ex.value)

    def test_MakeWorldRepresentation1(self):
        mockPyGame()
        obj = self.calibrator()
        result = obj.MakeWorldRepresentation(None, None)

        assert (result is None)

    def test_MakeWorldRepresentation2(self):
        arr = np.zeros(2)
        img = SmartImage(arr)
        obj = HomographyCalibrationMethod()
        p = patch(
            "Calibrator.ImageReceiver.CycloMedia.CycloMedia.CreateGeoSmartImage",
            new=MagicMock(return_value=(None, None))
        )
        p = patch(
            "Calibrator.ImageReceiver.MapBoxAPI.MapBoxAPI.CreateGeoSmartImage",
            MagicMock(return_value=None)
        )


def mockPyGame():
    pygame.init = Mock()
    pygame.display_set_mode = Mock()
    pygame.display = Mock()
    pygame.display.get_surface = Mock()
    pygame.display.get_surface().get_size = Mock(return_value=(100, 100))
    pygame.event.get = Mock(return_value=[])

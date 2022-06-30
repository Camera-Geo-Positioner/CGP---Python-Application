import unittest
from unittest.mock import MagicMock, patch
from Calibrator.Input.Primitives.SquarePrimitive import SquarePrimitive
from Calibrator.Input.Primitives.IPrimitive import IPrimitivePoint, IPrimitive
from Windowing.Rendering import Rendering


class TestSquarePrimitive(unittest.TestCase):
    primitive = SquarePrimitive()

    def test_Init(self):
        assert sum(isinstance(point, IPrimitivePoint) * 1 for point in self.primitive.points) == 2

    def test_IsMouseOver(self):
        # Get default Square primitive relative points
        relativePoints = self.primitive.GetRelativePoints()

        # Calculate center of the square primitive relative points
        centerX = \
            ((relativePoints[0][0] + relativePoints[1][0]) / 2)
        centerY = \
            ((relativePoints[0][1] + relativePoints[1][1]) / 2)

        assert self.primitive.IsMouseOver(centerX, centerY) is True, \
            "Valid mouse position is not detected over a default plane primitive."

    @patch("Windowing.Rendering.Rendering.RenderLine", MagicMock())
    @patch("Windowing.Rendering.Rendering.RenderPoint", MagicMock())
    def test_Render(self):
        self.primitive.Render(MagicMock(), 0, 200, 800, 800)


if __name__ == '__main__':
    unittest.main()

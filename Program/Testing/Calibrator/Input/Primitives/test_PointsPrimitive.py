from unittest.mock import MagicMock, patch
import pytest
from Calibrator.Input.Primitives.PointsPrimitive import PointsPrimitive
from Calibrator.Input.Primitives.IPrimitive import IPrimitivePoint, IPrimitive


class TestPointsPrimitive:

    primitive = PointsPrimitive()

    def test_init(self):
        assert sum(isinstance(point, IPrimitivePoint) * 1 for point in self.primitive.points) == 8

    @pytest.mark.parametrize("x, y", [(0, 0), (0.5, 0.5), (1, 1), (0, 1)])
    def test_IsMouseOver(self, x, y):
        assert not self.primitive.IsMouseOver(x, y), "someHow true?"

    def test_Render(self):
        with patch.object(IPrimitive, "Render"):
            self.primitive.Render(MagicMock(), 0, 200, 800, 800)

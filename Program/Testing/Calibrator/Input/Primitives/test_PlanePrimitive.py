# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software Project course.
# © Copyright Utrecht University (Department of Information and Computing Sciences)
import pytest

from Calibrator.Input.Primitives.IPrimitive import IPrimitivePoint
from Calibrator.Input.Primitives.PlanePrimitive import PlanePrimitive


class TestPlanePrimitive:
    @pytest.mark.parametrize("relativeX, relativeY, relativeWidth, relativeHeight",
                             [(1, 1, 1, 1),
                              (987543, 324876, 439875, 214387),
                              (-2654, -2324, -23748, -47539)])
    def test_init(self, relativeX, relativeY, relativeWidth, relativeHeight):
        # Get default plane primitive
        planePrimitive = PlanePrimitive(relativeX, relativeY, relativeWidth, relativeHeight)

        # Test for point 1
        assert planePrimitive.points[0].relativeX == \
            IPrimitivePoint(-relativeWidth / 2, -relativeHeight / 2).relativeX, "Wrong X coordinate"
        assert planePrimitive.points[0].relativeY == \
            IPrimitivePoint(-relativeWidth / 2, -relativeHeight / 2).relativeY, "Wrong Y coordinate"
        # Test for point 2
        assert planePrimitive.points[1].relativeX == \
            IPrimitivePoint(relativeWidth / 2, -relativeHeight / 2).relativeX, "Wrong X coordinate"
        assert planePrimitive.points[1].relativeY == \
            IPrimitivePoint(relativeWidth / 2, -relativeHeight / 2).relativeY, "Wrong Y coordinate"
        # Test for point 3
        assert planePrimitive.points[2].relativeX == \
            IPrimitivePoint(relativeWidth / 2, relativeHeight / 2).relativeX, "Wrong X coordinate"
        assert planePrimitive.points[2].relativeY == \
            IPrimitivePoint(relativeWidth / 2, relativeHeight / 2).relativeY, "Wrong Y coordinate"
        # Test for point 4
        assert planePrimitive.points[3].relativeX == \
            IPrimitivePoint(-relativeWidth / 2, relativeHeight / 2).relativeX, "Wrong X coordinate"
        assert planePrimitive.points[3].relativeY == \
            IPrimitivePoint(-relativeWidth / 2, relativeHeight / 2).relativeY, "Wrong Y coordinate"

        # Test that the given relativeX and relativeY are not manipulated when creating the planePrimitive.
        assert planePrimitive.x == relativeX, "Wrong relative X"
        assert planePrimitive.y == relativeY, "Wrong relative Y"

    def test_invalidInputString(self):
        with pytest.raises(TypeError) as excinfo:
            relativeX = "string"
            relativeY = "string"
            relativeWidth = "string"
            relativeHeight = "string"

            # Get an incorrect plane primitive
            planePrimitive = PlanePrimitive(relativeX, relativeY, relativeWidth, relativeHeight)

    def test_IsMouseOver(self):
        # Get default plane primitive relative points
        planePrimitive = PlanePrimitive()
        relativePoints = planePrimitive.GetRelativePoints()

        # Calculate center of the plane primitive relative points
        centerX = \
            (((relativePoints[0][0] + relativePoints[1][0]) / 2) +
             ((relativePoints[2][0] + relativePoints[3][0]) / 2)) / 2
        centerY = \
            (((relativePoints[0][1] + relativePoints[1][1]) / 2) +
             ((relativePoints[2][1] + relativePoints[3][1]) / 2)) / 2

        assert planePrimitive.IsMouseOver(centerX, centerY) is True, \
            "Valid mouse position is not detected over a default plane primitive."

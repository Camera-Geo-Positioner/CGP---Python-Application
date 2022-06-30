# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software Project course.
# © Copyright Utrecht University (Department of Information and Computing Sciences)

from unittest.mock import Mock
from Calibrator.Input.Primitives.IPrimitive import IPrimitive, IPrimitivePoint
from Calibrator.Input.Primitives.PlanePrimitive import PlanePrimitive


class TestIPrimitive:
    """ Method used for creating a testable IPrimitive object. """
    @staticmethod
    def _CreatePrimitive():
        # We create a rectangle IPrimitive, but we don't need to test the rectangle functionality,
        # so we will modify the points of the rectangle to have a single (0, 0) point.
        plane = PlanePrimitive()
        plane.x = 0
        plane.y = 0
        plane.points = [IPrimitivePoint(0, 0)]
        return plane

    def test_MoveTo(self):
        primitive = TestIPrimitive._CreatePrimitive()
        primitive.MoveTo(0.5, 0.5)
        assert (primitive.x, primitive.y) == (0.5, 0.5), "Primitive did not move to the correct position."

    def test_GetAbsolutePoints(self):
        primitive = TestIPrimitive._CreatePrimitive()

        absoluteWidth = 100
        absoluteHeight = 100
        absolutePoints = primitive.GetAbsolutePoints(absoluteWidth, absoluteHeight)

        assert len(absolutePoints) == len(primitive.points), "Primitive did not return the correct amount of points."
        assert (absolutePoints[0][0], absolutePoints[0][1]) == (0, 0), "Primitive did not return the correct points."

    def test_GetAbsolutePoint(self):
        primitive = TestIPrimitive._CreatePrimitive()

        absoluteWidth = 100
        absoluteHeight = 100
        absolutePoint = primitive.GetAbsolutePoint(0, absoluteWidth, absoluteHeight)

        assert (absolutePoint[0], absolutePoint[1]) == (0, 0), "Primitive did not return the correct point."

    def test_GetRelativePoints(self):
        primitive = TestIPrimitive._CreatePrimitive()

        relativePoints = primitive.GetRelativePoints()

        assert len(relativePoints) == len(primitive.points), "Primitive did not return the correct amount of points."
        assert (relativePoints[0][0], relativePoints[0][1]) == (0, 0), "Primitive did not return the correct points."

    def test_GetRelativePoint(self):
        primitive = TestIPrimitive._CreatePrimitive()

        relativePoint = primitive.GetRelativePoint(0)

        assert (relativePoint[0], relativePoint[1]) == (0, 0), "Primitive did not return the correct point."

    def test_IsMouseOverPoint(self):
        primitive = TestIPrimitive._CreatePrimitive()

        # Default point is (0, 0) - thus make sure the mouse is not over the point
        mouseOverPoint, pointIndex = primitive.IsMouseOverPoint(1, 1)

        assert mouseOverPoint is False, "Primitive point was incorrectly detected as being over."
        assert pointIndex is None, "Primitive point index was incorrectly detected as being over."

        # Make sure the mouse is over the point
        mouseOverPoint, pointIndex = primitive.IsMouseOverPoint(0, 0)

        assert mouseOverPoint is True, "Primitive point was not detected as being over."
        assert pointIndex is 0, "Primitive point index was not detected as being over."

    def test_HandleMouseMovement(self):
        primitive = TestIPrimitive._CreatePrimitive()

        # Make sure the mouse is not over the point
        primitive.HandleMouseMovement(1, 1)

        assert primitive.moveAsWhole is False, "Primitive was incorrectly detected as moving."
        assert primitive.movePoint is False, "Primitive point was incorrectly detected as moving."
        assert primitive.movePointIndex is None, "Primitive point index was incorrectly detected as moving."

        # Make sure the mouse is over the point
        primitive.HandleMouseMovement(0, 0)

        assert primitive.moveAsWhole is False, "Primitive was not detected as moving."
        assert primitive.movePoint is True, "Primitive point was not detected as moving."
        assert primitive.movePointIndex == 0, "Primitive point index was not detected as moving."

    def test_ResetMouseMovement(self):
        primitive = TestIPrimitive._CreatePrimitive()
        primitive.moveAsWhole = True
        primitive.movePoint = True
        primitive.movePointIndex = 0

        primitive.ResetMouseMovement()
        assert primitive.moveAsWhole is False, "Primitive moving as whole was not reset."
        assert primitive.movePoint is False, "Primitive moving a point was not reset."
        assert primitive.movePointIndex is None, "Primitive moving point index was not reset."


class TestIPrimitivePoint:
    def test_MoveTo(self):
        point = IPrimitivePoint(0, 0)
        point.MoveTo(0.5, 0.5)
        assert (point.relativeX, point.relativeY) == (0.5, 0.5), "Primitive point did not move to the correct position."

    def test_IsMouseOver(self):
        point = IPrimitivePoint(0, 0)

        # Default point is (0, 0) - thus make sure the mouse is not over the point
        assert point.IsMouseOver(0, 0, 1, 1) is False, "Primitive point was incorrectly detected as being over."

        # Make sure the mouse is over the point
        assert point.IsMouseOver(0, 0, 0, 0) is True, "Primitive point was not detected as being over."

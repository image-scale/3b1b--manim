"""
Tests for manimlib.utils.bezier
"""
import numpy as np
import pytest

from manimlib.utils.bezier import bezier, partial_bezier_points


def test_bezier_linear():
    # Linear bezier between 0 and 1
    b = bezier([0.0, 1.0])
    assert b(0.0) == pytest.approx(0.0)
    assert b(0.5) == pytest.approx(0.5)
    assert b(1.0) == pytest.approx(1.0)


def test_bezier_quadratic():
    # Quadratic: midpoint at t=0.5 should be average of control points
    b = bezier([0.0, 1.0, 2.0])
    assert b(0.0) == pytest.approx(0.0)
    assert b(1.0) == pytest.approx(2.0)


def test_bezier_single_point():
    b = bezier([3.0])
    assert b(0.0) == pytest.approx(3.0)
    assert b(0.5) == pytest.approx(3.0)
    assert b(1.0) == pytest.approx(3.0)


def test_bezier_empty_raises():
    with pytest.raises(Exception):
        bezier([])


def test_bezier_with_arrays():
    points = [np.array([0.0, 0.0]), np.array([1.0, 1.0])]
    b = bezier(points)
    result = b(0.5)
    np.testing.assert_array_almost_equal(result, [0.5, 0.5])


def test_partial_bezier_points_full_range():
    pts = [0.0, 1.0, 2.0]
    result = partial_bezier_points(pts, 0.0, 1.0)
    assert len(result) == 3


def test_partial_bezier_points_at_end():
    pts = [0.0, 1.0, 2.0]
    result = partial_bezier_points(pts, 1.0, 1.0)
    assert all(abs(r - 2.0) < 1e-9 for r in result)

"""
Tests for manimlib.utils.space_ops
"""
import math
import numpy as np
import pytest

from manimlib.utils.space_ops import (
    cross, get_norm, get_dist, normalize, cross2d,
    midpoint,
)


def test_cross_basic():
    v1 = np.array([1.0, 0.0, 0.0])
    v2 = np.array([0.0, 1.0, 0.0])
    result = cross(v1, v2)
    np.testing.assert_array_almost_equal(result, [0.0, 0.0, 1.0])


def test_cross_anticommutative():
    v1 = np.array([1.0, 2.0, 3.0])
    v2 = np.array([4.0, 5.0, 6.0])
    np.testing.assert_array_almost_equal(cross(v1, v2), -cross(v2, v1))


def test_get_norm_zero():
    assert get_norm([0.0, 0.0, 0.0]) == pytest.approx(0.0)


def test_get_norm_unit():
    assert get_norm([1.0, 0.0, 0.0]) == pytest.approx(1.0)


def test_get_norm_pythagoras():
    assert get_norm([3.0, 4.0, 0.0]) == pytest.approx(5.0)


def test_get_dist():
    v1 = np.array([0.0, 0.0, 0.0])
    v2 = np.array([3.0, 4.0, 0.0])
    assert get_dist(v1, v2) == pytest.approx(5.0)


def test_normalize_unit_vector():
    v = np.array([3.0, 4.0, 0.0])
    n = normalize(v)
    assert get_norm(n) == pytest.approx(1.0)
    np.testing.assert_array_almost_equal(n, [0.6, 0.8, 0.0])


def test_normalize_zero_vector():
    v = np.array([0.0, 0.0, 0.0])
    n = normalize(v)
    np.testing.assert_array_almost_equal(n, [0.0, 0.0, 0.0])


def test_normalize_fallback():
    v = np.array([0.0, 0.0, 0.0])
    fallback = np.array([1.0, 0.0, 0.0])
    n = normalize(v, fallback)
    np.testing.assert_array_almost_equal(n, [1.0, 0.0, 0.0])


def test_cross2d():
    v1 = np.array([1.0, 0.0])
    v2 = np.array([0.0, 1.0])
    assert cross2d(v1, v2) == pytest.approx(1.0)


def test_midpoint():
    p1 = np.array([0.0, 0.0, 0.0])
    p2 = np.array([2.0, 4.0, 6.0])
    m = midpoint(p1, p2)
    np.testing.assert_array_almost_equal(m, [1.0, 2.0, 3.0])

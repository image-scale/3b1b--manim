"""
Tests for manimlib.utils.rate_functions
"""
import pytest

from manimlib.utils.rate_functions import (
    linear, smooth, rush_into, rush_from, double_smooth, slow_into,
)


def _check_rate_fn(fn, strict_zero=True, strict_one=True):
    """Check a rate function maps [0,1] -> [0,1] and is monotone-ish."""
    if strict_zero:
        assert fn(0) == pytest.approx(0.0, abs=1e-9)
    if strict_one:
        assert fn(1) == pytest.approx(1.0, abs=1e-9)


def test_linear_zero():
    assert linear(0.0) == pytest.approx(0.0)


def test_linear_one():
    assert linear(1.0) == pytest.approx(1.0)


def test_linear_mid():
    assert linear(0.5) == pytest.approx(0.5)


def test_smooth_endpoints():
    _check_rate_fn(smooth)


def test_smooth_midpoint_is_half():
    assert smooth(0.5) == pytest.approx(0.5, abs=1e-9)


def test_smooth_monotone():
    vals = [smooth(t / 10) for t in range(11)]
    assert all(vals[i] <= vals[i + 1] for i in range(len(vals) - 1))


def test_rush_into_endpoints():
    _check_rate_fn(rush_into)


def test_rush_from_endpoints():
    _check_rate_fn(rush_from)


def test_double_smooth_endpoints():
    _check_rate_fn(double_smooth)


def test_double_smooth_midpoint():
    assert double_smooth(0.5) == pytest.approx(0.5, abs=1e-9)


def test_slow_into_endpoints():
    _check_rate_fn(slow_into)

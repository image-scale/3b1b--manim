"""
Tests for manimlib.utils.color
"""
import numpy as np
import pytest
from colour import Color

from manimlib.utils.color import (
    color_to_rgb, color_to_rgba, rgb_to_color, rgba_to_color,
    rgb_to_hex, hex_to_rgb, invert_color, color_to_int_rgb,
)


def test_hex_to_rgb_white():
    rgb = hex_to_rgb("#FFFFFF")
    np.testing.assert_array_almost_equal(rgb, [1.0, 1.0, 1.0])


def test_hex_to_rgb_black():
    rgb = hex_to_rgb("#000000")
    np.testing.assert_array_almost_equal(rgb, [0.0, 0.0, 0.0])


def test_rgb_to_hex_white():
    result = rgb_to_hex([1.0, 1.0, 1.0])
    assert result.upper() == "#FFFFFF"


def test_rgb_to_hex_black():
    result = rgb_to_hex([0.0, 0.0, 0.0])
    assert result.upper() == "#000000"


def test_color_to_rgb_from_string():
    rgb = color_to_rgb("#FF0000")
    assert rgb[0] == pytest.approx(1.0, abs=0.01)
    assert rgb[1] == pytest.approx(0.0, abs=0.01)


def test_color_to_rgb_from_color():
    c = Color("#00FF00")
    rgb = color_to_rgb(c)
    assert rgb[1] == pytest.approx(1.0, abs=0.01)


def test_color_to_rgba_default_alpha():
    rgba = color_to_rgba("#FF0000")
    assert len(rgba) == 4
    assert rgba[3] == pytest.approx(1.0)


def test_color_to_rgba_custom_alpha():
    rgba = color_to_rgba("#FF0000", alpha=0.5)
    assert rgba[3] == pytest.approx(0.5)


def test_rgb_to_color_returns_color():
    c = rgb_to_color([1.0, 0.0, 0.0])
    assert isinstance(c, Color)


def test_rgba_to_color():
    c = rgba_to_color(np.array([1.0, 0.0, 0.0, 0.5]))
    assert isinstance(c, Color)


def test_invert_color():
    white = "#FFFFFF"
    inverted = invert_color(white)
    rgb = color_to_rgb(inverted)
    np.testing.assert_array_almost_equal(rgb, [0.0, 0.0, 0.0], decimal=1)


def test_color_to_int_rgb():
    result = color_to_int_rgb("#FFFFFF")
    np.testing.assert_array_equal(result, [255, 255, 255])

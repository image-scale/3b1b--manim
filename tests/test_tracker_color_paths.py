import numpy as np
import pytest
from animlib import (
    ValueTracker, ExponentialValueTracker,
    Mobject, VMobject, Circle, Rectangle, Square, Dot,
    Transform, MoveToTarget, FadeIn,
    Scene,
    ORIGIN, UP, DOWN, LEFT, RIGHT, PI, TAU,
    RED, BLUE, GREEN, WHITE, BLACK,
    color_to_rgb, color_to_rgba, rgb_to_hex, hex_to_rgb,
    interpolate_color, color_gradient, average_color, random_color,
    color_to_int_rgb, color_to_int_rgba, color_to_hex, invert_color,
    straight_path, path_along_arc, clockwise_path, counterclockwise_path,
    prepare_animation, linear,
)


class TestValueTracker:
    def test_create_default(self):
        vt = ValueTracker()
        assert abs(vt.get_value()) < 1e-10

    def test_create_with_value(self):
        vt = ValueTracker(5.0)
        assert abs(vt.get_value() - 5.0) < 1e-10

    def test_set_value(self):
        vt = ValueTracker(0)
        vt.set_value(42)
        assert abs(vt.get_value() - 42) < 1e-10

    def test_increment_value(self):
        vt = ValueTracker(10)
        vt.increment_value(5)
        assert abs(vt.get_value() - 15) < 1e-10

    def test_interpolation(self):
        vt = ValueTracker(0)
        start = ValueTracker(0)
        end = ValueTracker(10)
        vt.interpolate(start, end, 0.5)
        assert abs(vt.get_value() - 5.0) < 1e-10

    def test_copy(self):
        vt = ValueTracker(7)
        c = vt.copy()
        c.set_value(99)
        assert abs(vt.get_value() - 7) < 1e-10

    def test_animation_with_scene(self):
        s = Scene(fps=10)
        vt = ValueTracker(0)
        s.add(vt)
        target = vt.generate_target()
        target.set_value(10)
        s.play(MoveToTarget(vt), run_time=0.5)
        assert abs(vt.get_value() - 10) < 1.0

    def test_become(self):
        vt1 = ValueTracker(5)
        vt2 = ValueTracker(20)
        vt1.become(vt2)
        assert abs(vt1.get_value() - 20) < 1e-10


class TestExponentialValueTracker:
    def test_create(self):
        evt = ExponentialValueTracker(2.0)
        assert abs(evt.get_value() - 2.0) < 0.01

    def test_set_value(self):
        evt = ExponentialValueTracker(1.0)
        evt.set_value(10.0)
        assert abs(evt.get_value() - 10.0) < 0.01

    def test_interpolation_multiplicative(self):
        evt = ExponentialValueTracker(1.0)
        start = ExponentialValueTracker(1.0)
        end = ExponentialValueTracker(100.0)
        evt.interpolate(start, end, 0.5)
        val = evt.get_value()
        assert val > 1.0 and val < 100.0


class TestAnimateProperty:
    def test_animate_returns_builder(self):
        c = Circle()
        builder = c.animate
        assert hasattr(builder, 'build')

    def test_animate_shift(self):
        c = Circle()
        builder = c.animate.shift(RIGHT)
        anim = prepare_animation(builder)
        assert isinstance(anim, MoveToTarget)

    def test_animate_chain(self):
        c = Circle()
        builder = c.animate.shift(RIGHT).scale(2)
        anim = prepare_animation(builder)
        anim.begin()
        anim.interpolate(1.0)

    def test_animate_in_scene(self):
        s = Scene(fps=10)
        c = Circle()
        s.add(c)
        s.play(c.animate.shift(RIGHT * 3), run_time=0.3)

    def test_animate_set_color(self):
        c = Circle()
        builder = c.animate.set_color(RED)
        anim = prepare_animation(builder)
        anim.begin()
        anim.interpolate(1.0)


class TestColorToRGB:
    def test_hex_to_rgb(self):
        rgb = hex_to_rgb("#FF0000")
        assert np.allclose(rgb, [1, 0, 0])

    def test_hex_to_rgb_green(self):
        rgb = hex_to_rgb("#00FF00")
        assert np.allclose(rgb, [0, 1, 0])

    def test_hex_to_rgb_blue(self):
        rgb = hex_to_rgb("#0000FF")
        assert np.allclose(rgb, [0, 0, 1])

    def test_hex_to_rgb_white(self):
        rgb = hex_to_rgb("#FFFFFF")
        assert np.allclose(rgb, [1, 1, 1])

    def test_hex_to_rgb_black(self):
        rgb = hex_to_rgb("#000000")
        assert np.allclose(rgb, [0, 0, 0])


class TestColorToRGBA:
    def test_default_alpha(self):
        rgba = color_to_rgba("#FF0000")
        assert np.allclose(rgba, [1, 0, 0, 1])

    def test_custom_alpha(self):
        rgba = color_to_rgba("#FF0000", 0.5)
        assert np.allclose(rgba, [1, 0, 0, 0.5])


class TestRGBToHex:
    def test_red(self):
        assert rgb_to_hex([1, 0, 0]) == "#FF0000"

    def test_green(self):
        assert rgb_to_hex([0, 1, 0]) == "#00FF00"

    def test_blue(self):
        assert rgb_to_hex([0, 0, 1]) == "#0000FF"

    def test_white(self):
        assert rgb_to_hex([1, 1, 1]) == "#FFFFFF"

    def test_black(self):
        assert rgb_to_hex([0, 0, 0]) == "#000000"

    def test_roundtrip(self):
        original = "#A3B5C7"
        rgb = hex_to_rgb(original)
        result = rgb_to_hex(rgb)
        assert result == original


class TestInterpolateColor:
    def test_alpha_zero(self):
        result = interpolate_color("#FF0000", "#0000FF", 0)
        rgb = hex_to_rgb(result)
        assert np.allclose(rgb, [1, 0, 0], atol=0.01)

    def test_alpha_one(self):
        result = interpolate_color("#FF0000", "#0000FF", 1)
        rgb = hex_to_rgb(result)
        assert np.allclose(rgb, [0, 0, 1], atol=0.01)

    def test_alpha_half(self):
        result = interpolate_color("#FF0000", "#0000FF", 0.5)
        rgb = hex_to_rgb(result)
        assert rgb[0] > 0 and rgb[2] > 0


class TestColorGradient:
    def test_single_output(self):
        result = color_gradient(["#FF0000", "#0000FF"], 1)
        assert len(result) == 1

    def test_two_outputs(self):
        result = color_gradient(["#FF0000", "#0000FF"], 2)
        assert len(result) == 2
        assert hex_to_rgb(result[0])[0] > 0.9
        assert hex_to_rgb(result[1])[2] > 0.9

    def test_multiple_outputs(self):
        result = color_gradient(["#FF0000", "#00FF00", "#0000FF"], 5)
        assert len(result) == 5

    def test_gradient_endpoints_match(self):
        result = color_gradient(["#FF0000", "#0000FF"], 3)
        assert np.allclose(hex_to_rgb(result[0]), [1, 0, 0], atol=0.01)
        assert np.allclose(hex_to_rgb(result[-1]), [0, 0, 1], atol=0.01)


class TestAverageColor:
    def test_average_same_colors(self):
        result = average_color("#FF0000", "#FF0000")
        rgb = hex_to_rgb(result)
        assert np.allclose(rgb, [1, 0, 0], atol=0.01)

    def test_average_different_colors(self):
        result = average_color("#FF0000", "#0000FF")
        rgb = hex_to_rgb(result)
        assert rgb[0] > 0 and rgb[2] > 0


class TestRandomColor:
    def test_random_color_format(self):
        c = random_color()
        assert isinstance(c, str)
        assert c.startswith("#")
        assert len(c) == 7


class TestColorUtilities:
    def test_color_to_rgb(self):
        rgb = color_to_rgb(RED)
        assert len(rgb) == 3
        assert all(0 <= v <= 1 for v in rgb)

    def test_color_to_int_rgb(self):
        result = color_to_int_rgb("#FF0000")
        assert result[0] == 255
        assert result[1] == 0
        assert result[2] == 0

    def test_color_to_int_rgba(self):
        result = color_to_int_rgba("#FF0000", 0.5)
        assert result[0] == 255
        assert result[3] == 128 or result[3] == 127

    def test_color_to_hex(self):
        result = color_to_hex("#FF0000")
        assert result == "#FF0000"

    def test_invert_color(self):
        result = invert_color("#FF0000")
        rgb = hex_to_rgb(result)
        assert np.allclose(rgb, [0, 1, 1], atol=0.01)


class TestStraightPath:
    def test_alpha_zero(self):
        start = np.array([0, 0, 0], dtype=float)
        end = np.array([4, 0, 0], dtype=float)
        result = straight_path(start, end, 0)
        assert np.allclose(result, start)

    def test_alpha_one(self):
        start = np.array([0, 0, 0], dtype=float)
        end = np.array([4, 0, 0], dtype=float)
        result = straight_path(start, end, 1)
        assert np.allclose(result, end)

    def test_alpha_half(self):
        start = np.array([0, 0, 0], dtype=float)
        end = np.array([4, 0, 0], dtype=float)
        result = straight_path(start, end, 0.5)
        assert np.allclose(result, [2, 0, 0])


class TestPathAlongArc:
    def test_arc_path_endpoints(self):
        pf = path_along_arc(PI)
        start = np.array([1, 0, 0], dtype=float)
        end = np.array([-1, 0, 0], dtype=float)
        result_0 = pf(start, end, 0)
        result_1 = pf(start, end, 1)
        assert np.allclose(result_0, start, atol=0.1)
        assert np.allclose(result_1, end, atol=0.1)

    def test_arc_path_midpoint_off_straight(self):
        pf = path_along_arc(PI)
        start = np.array([1, 0, 0], dtype=float)
        end = np.array([-1, 0, 0], dtype=float)
        mid = pf(start, end, 0.5)
        straight_mid = (start + end) / 2
        assert not np.allclose(mid, straight_mid, atol=0.1)

    def test_small_angle_is_straight(self):
        pf = path_along_arc(0.001)
        assert pf is straight_path

    def test_clockwise_path(self):
        pf = clockwise_path()
        start = np.array([1, 0, 0], dtype=float)
        end = np.array([-1, 0, 0], dtype=float)
        mid = pf(start, end, 0.5)
        assert mid[1] < 0

    def test_counterclockwise_path(self):
        pf = counterclockwise_path()
        start = np.array([1, 0, 0], dtype=float)
        end = np.array([-1, 0, 0], dtype=float)
        mid = pf(start, end, 0.5)
        assert mid[1] > 0

    def test_arc_path_batch(self):
        pf = path_along_arc(PI / 2)
        starts = np.array([[1, 0, 0], [0, 1, 0]], dtype=float)
        ends = np.array([[0, 1, 0], [-1, 0, 0]], dtype=float)
        result = pf(starts, ends, 0.5)
        assert result.shape == (2, 3)

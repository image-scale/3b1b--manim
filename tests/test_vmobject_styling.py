import numpy as np
import pytest
from animlib import (
    VMobject, VGroup, DashedVMobject, Ellipse,
    Circle, Rectangle, Line, Dot,
    ORIGIN, UP, DOWN, LEFT, RIGHT, PI, TAU,
    RED, BLUE, GREEN, WHITE, BLACK,
    DEFAULT_STROKE_WIDTH,
)
from animlib.mobject import Mobject


class TestVMobjectFillStyle:
    def test_default_fill_opacity_zero(self):
        vm = VMobject()
        assert vm.get_fill_opacity() == 0.0

    def test_set_fill_color(self):
        vm = VMobject()
        vm.set_fill(RED)
        assert vm.get_fill_color() == RED

    def test_set_fill_opacity(self):
        vm = VMobject()
        vm.set_fill(opacity=0.7)
        assert abs(vm.get_fill_opacity() - 0.7) < 1e-10

    def test_set_fill_both(self):
        vm = VMobject()
        vm.set_fill(BLUE, opacity=0.5)
        assert vm.get_fill_color() == BLUE
        assert abs(vm.get_fill_opacity() - 0.5) < 1e-10

    def test_has_fill_false_by_default(self):
        vm = VMobject()
        assert not vm.has_fill()

    def test_has_fill_true_when_opacity_nonzero(self):
        vm = VMobject()
        vm.set_fill(opacity=0.5)
        assert vm.has_fill()


class TestVMobjectStrokeStyle:
    def test_default_stroke_width(self):
        vm = VMobject()
        assert abs(vm.get_stroke_width() - DEFAULT_STROKE_WIDTH) < 1e-10

    def test_set_stroke_color(self):
        vm = VMobject()
        vm.set_stroke(RED)
        assert vm.get_stroke_color() == RED

    def test_set_stroke_width(self):
        vm = VMobject()
        vm.set_stroke(width=5.0)
        assert abs(vm.get_stroke_width() - 5.0) < 1e-10

    def test_set_stroke_opacity(self):
        vm = VMobject()
        vm.set_stroke(opacity=0.3)
        assert abs(vm.get_stroke_opacity() - 0.3) < 1e-10

    def test_has_stroke_true_by_default(self):
        vm = VMobject()
        assert vm.has_stroke()

    def test_has_stroke_false_when_zero_width(self):
        vm = VMobject()
        vm.set_stroke(width=0)
        assert not vm.has_stroke()

    def test_has_stroke_false_when_zero_opacity(self):
        vm = VMobject()
        vm.set_stroke(opacity=0)
        assert not vm.has_stroke()


class TestVMobjectSetColor:
    def test_set_color_sets_both(self):
        vm = VMobject()
        vm.set_color(GREEN)
        assert vm.get_fill_color() == GREEN
        assert vm.get_stroke_color() == GREEN

    def test_set_color_with_opacity(self):
        vm = VMobject()
        vm.set_color(RED, opacity=0.8)
        assert vm.get_fill_opacity() == 0.8
        assert vm.get_stroke_opacity() == 0.8

    def test_get_color_returns_fill_when_filled(self):
        vm = VMobject()
        vm.set_fill(BLUE, opacity=1.0)
        assert vm.get_color() == BLUE

    def test_get_color_returns_stroke_when_no_fill(self):
        vm = VMobject()
        vm.set_stroke(RED)
        assert vm.get_color() == RED


class TestVMobjectMatchStyle:
    def test_match_style(self):
        source = VMobject()
        source.set_fill(RED, 0.7)
        source.set_stroke(BLUE, 3.0, 0.9)
        target = VMobject()
        target.match_style(source)
        assert target.get_fill_color() == RED
        assert abs(target.get_fill_opacity() - 0.7) < 1e-10
        assert target.get_stroke_color() == BLUE
        assert abs(target.get_stroke_width() - 3.0) < 1e-10
        assert abs(target.get_stroke_opacity() - 0.9) < 1e-10


class TestVMobjectBackstroke:
    def test_set_backstroke(self):
        vm = VMobject()
        vm.set_backstroke(width=5)
        assert vm._stroke_behind is True


class TestVMobjectPathBuilding:
    def test_start_new_path(self):
        vm = VMobject()
        vm.start_new_path([1, 2, 0])
        assert vm.has_points()
        assert np.allclose(vm.get_start(), [1, 2, 0])

    def test_add_line_to(self):
        vm = VMobject()
        vm.start_new_path([0, 0, 0])
        vm.add_line_to([1, 0, 0])
        assert vm.get_num_curves() >= 1
        assert np.allclose(vm.get_end(), [1, 0, 0])

    def test_add_quadratic_bezier(self):
        vm = VMobject()
        vm.start_new_path([0, 0, 0])
        vm.add_quadratic_bezier_curve_to([0.5, 1, 0], [1, 0, 0])
        assert vm.get_num_curves() == 1
        assert np.allclose(vm.get_end(), [1, 0, 0])

    def test_add_smooth_curve(self):
        vm = VMobject()
        vm.start_new_path([0, 0, 0])
        vm.add_line_to([1, 0, 0])
        vm.add_smooth_curve_to([2, 1, 0])
        assert vm.get_num_curves() >= 2

    def test_close_path(self):
        vm = VMobject()
        vm.start_new_path([0, 0, 0])
        vm.add_line_to([1, 0, 0])
        vm.add_line_to([1, 1, 0])
        vm.close_path()
        assert vm.is_closed()

    def test_set_points_as_corners(self):
        vm = VMobject()
        corners = [[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]]
        vm.set_points_as_corners(corners)
        assert vm.has_points()
        assert vm.get_num_curves() == 3
        assert np.allclose(vm.get_start(), [0, 0, 0])
        assert np.allclose(vm.get_end(), [0, 1, 0])


class TestVMobjectSmoothing:
    def test_make_smooth(self):
        vm = VMobject()
        corners = [[0, 0, 0], [1, 0, 0], [2, 1, 0], [3, 0, 0]]
        vm.set_points_as_corners(corners)
        original_anchors = vm.get_anchors().copy()
        vm.make_smooth()
        smooth_anchors = vm.get_anchors()
        assert len(smooth_anchors) >= len(original_anchors)

    def test_make_jagged(self):
        vm = VMobject()
        corners = [[0, 0, 0], [1, 0, 0], [2, 1, 0], [3, 0, 0]]
        vm.set_points_as_corners(corners)
        vm.make_smooth()
        vm.make_jagged()
        anchors = vm.get_anchors()
        for curve in vm.get_bezier_tuples():
            handle = curve[1]
            anchor1 = curve[0]
            anchor2 = curve[2]
            mid = (anchor1 + anchor2) / 2
            assert np.allclose(handle, mid, atol=0.01)


class TestVMobjectCurveQueries:
    def test_get_anchors(self):
        vm = VMobject()
        vm.start_new_path([0, 0, 0])
        vm.add_line_to([1, 0, 0])
        vm.add_line_to([2, 0, 0])
        anchors = vm.get_anchors()
        assert len(anchors) == 3
        assert np.allclose(anchors[0], [0, 0, 0])
        assert np.allclose(anchors[-1], [2, 0, 0])

    def test_get_num_curves(self):
        vm = VMobject()
        vm.start_new_path([0, 0, 0])
        vm.add_line_to([1, 0, 0])
        vm.add_line_to([2, 0, 0])
        vm.add_line_to([3, 0, 0])
        assert vm.get_num_curves() == 3

    def test_is_closed_open_path(self):
        vm = VMobject()
        vm.start_new_path([0, 0, 0])
        vm.add_line_to([1, 0, 0])
        assert not vm.is_closed()

    def test_is_closed_closed_path(self):
        vm = VMobject()
        vm.start_new_path([0, 0, 0])
        vm.add_line_to([1, 0, 0])
        vm.add_line_to([0, 1, 0])
        vm.close_path()
        assert vm.is_closed()

    def test_get_arc_length_straight_line(self):
        vm = VMobject()
        vm.start_new_path([0, 0, 0])
        vm.add_line_to([3, 4, 0])
        length = vm.get_arc_length(n_sample_points=50)
        assert abs(length - 5.0) < 0.2

    def test_get_bezier_tuples(self):
        vm = VMobject()
        vm.start_new_path([0, 0, 0])
        vm.add_line_to([1, 0, 0])
        vm.add_line_to([2, 0, 0])
        tuples = list(vm.get_bezier_tuples())
        assert len(tuples) == 2
        for t in tuples:
            assert t.shape == (3, 3)


class TestPointwiseBecomePartial:
    def test_partial_first_half(self):
        circle = Circle()
        partial = VMobject()
        partial.pointwise_become_partial(circle, 0, 0.5)
        assert partial.has_points()
        assert partial.get_num_points() < circle.get_num_points()

    def test_partial_full_curve(self):
        line = Line([0, 0, 0], [4, 0, 0])
        partial = VMobject()
        partial.pointwise_become_partial(line, 0, 1)
        assert partial.has_points()

    def test_partial_empty_range(self):
        circle = Circle()
        partial = VMobject()
        partial.pointwise_become_partial(circle, 0.5, 0.5)
        assert not partial.has_points()


class TestDashedVMobject:
    def test_dashed_circle(self):
        circle = Circle()
        dashed = DashedVMobject(circle, num_dashes=10)
        assert len(dashed.submobjects) > 0
        assert len(dashed.submobjects) <= 10

    def test_dashed_line(self):
        line = Line([0, 0, 0], [4, 0, 0])
        dashed = DashedVMobject(line, num_dashes=5)
        assert len(dashed.submobjects) > 0


class TestEllipse:
    def test_ellipse_dimensions(self):
        e = Ellipse(width=4, height=2)
        assert abs(e.get_width() - 4) < 0.3
        assert abs(e.get_height() - 2) < 0.3

    def test_ellipse_centered(self):
        e = Ellipse()
        assert np.allclose(e.get_center(), ORIGIN, atol=0.1)


class TestVGroup:
    def test_vgroup_accepts_vmobjects(self):
        c = Circle()
        r = Rectangle()
        vg = VGroup(c, r)
        assert len(vg) == 2

    def test_vgroup_rejects_non_vmobjects(self):
        m = Mobject()
        with pytest.raises(TypeError):
            VGroup(m)

    def test_vgroup_style_propagation(self):
        c1 = Circle()
        c2 = Circle()
        vg = VGroup(c1, c2)
        vg.set_fill(RED, 0.5)
        assert c1.get_fill_color() == RED
        assert abs(c1.get_fill_opacity() - 0.5) < 1e-10
        assert c2.get_fill_color() == RED


class TestVMobjectCopy:
    def test_copy_preserves_style(self):
        vm = VMobject()
        vm.set_fill(RED, 0.5)
        vm.set_stroke(BLUE, 3.0)
        c = vm.copy()
        assert c.get_fill_color() == RED
        assert abs(c.get_fill_opacity() - 0.5) < 1e-10
        assert c.get_stroke_color() == BLUE
        assert abs(c.get_stroke_width() - 3.0) < 1e-10

    def test_copy_style_independent(self):
        vm = VMobject()
        vm.set_fill(RED, 0.5)
        c = vm.copy()
        c.set_fill(BLUE, 0.9)
        assert vm.get_fill_color() == RED
        assert abs(vm.get_fill_opacity() - 0.5) < 1e-10

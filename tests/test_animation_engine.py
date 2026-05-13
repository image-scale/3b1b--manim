import numpy as np
import pytest
from animlib import (
    smooth, linear, rush_into, rush_from, slow_into,
    double_smooth, there_and_back, there_and_back_with_pause,
    squish_rate_func, wiggle, lingering, exponential_decay,
    overshoot, running_start, not_quite_there,
    Animation, Transform, ReplacementTransform, MoveToTarget,
    ApplyMethod, ApplyFunction, Restore,
    FadeIn, FadeOut, FadeTransform,
    ShowCreation, Write, ShowIncreasingSubsets,
    Mobject, VMobject, VGroup, Circle, Rectangle, Line, Dot, Square,
    ORIGIN, UP, DOWN, LEFT, RIGHT, PI, RED, BLUE, WHITE,
)


class TestRateFunctions:
    def test_smooth_endpoints(self):
        assert abs(smooth(0) - 0) < 1e-10
        assert abs(smooth(1) - 1) < 1e-10

    def test_smooth_midpoint(self):
        assert abs(smooth(0.5) - 0.5) < 1e-10

    def test_smooth_monotonic(self):
        values = [smooth(t) for t in np.linspace(0, 1, 20)]
        for i in range(len(values) - 1):
            assert values[i] <= values[i + 1] + 1e-10

    def test_linear_identity(self):
        for t in np.linspace(0, 1, 10):
            assert abs(linear(t) - t) < 1e-10

    def test_rush_into_endpoints(self):
        assert abs(rush_into(0) - 0) < 1e-10
        assert abs(rush_into(1) - 1) < 1e-10

    def test_rush_into_starts_slow(self):
        assert rush_into(0.1) < 0.1

    def test_rush_from_endpoints(self):
        assert abs(rush_from(0) - 0) < 1e-10
        assert abs(rush_from(1) - 1) < 1e-10

    def test_rush_from_starts_fast(self):
        assert rush_from(0.1) > 0.1

    def test_there_and_back_endpoints(self):
        assert abs(there_and_back(0) - 0) < 1e-10
        assert abs(there_and_back(1) - 0) < 1e-10

    def test_there_and_back_peak(self):
        assert abs(there_and_back(0.5) - 1) < 1e-6

    def test_double_smooth_endpoints(self):
        assert abs(double_smooth(0) - 0) < 1e-10
        assert abs(double_smooth(1) - 1) < 1e-10

    def test_double_smooth_midpoint(self):
        assert abs(double_smooth(0.5) - 0.5) < 1e-10

    def test_squish_rate_func(self):
        squished = squish_rate_func(smooth, 0.2, 0.8)
        assert abs(squished(0) - 0) < 1e-10
        assert abs(squished(0.1) - 0) < 1e-10
        assert abs(squished(0.9) - 1) < 1e-10
        assert abs(squished(1) - 1) < 1e-10
        mid_val = squished(0.5)
        assert 0.4 < mid_val < 0.6

    def test_slow_into(self):
        assert abs(slow_into(0) - 0) < 1e-10
        assert abs(slow_into(1) - 1) < 1e-10

    def test_there_and_back_with_pause(self):
        f = there_and_back_with_pause
        assert abs(f(0) - 0) < 1e-6
        assert abs(f(0.5) - 1) < 1e-6

    def test_exponential_decay(self):
        assert abs(exponential_decay(0) - 0) < 1e-10
        val = exponential_decay(1)
        assert val > 0.99

    def test_not_quite_there(self):
        f = not_quite_there(proportion=0.5)
        assert abs(f(1) - 0.5) < 1e-10


class TestAnimationBase:
    def test_animation_stores_mobject(self):
        m = Mobject()
        m.set_points([[0, 0, 0]])
        anim = Animation(m)
        assert anim.mobject is m

    def test_animation_default_run_time(self):
        m = Mobject()
        anim = Animation(m)
        assert anim.run_time == 1.0

    def test_animation_begin_creates_starting(self):
        m = Mobject()
        m.set_points([[0, 0, 0]])
        anim = Animation(m)
        anim.begin()
        assert anim.starting_mobject is not None
        assert anim.starting_mobject is not m

    def test_animation_interpolate_calls_rate_func(self):
        m = Mobject()
        m.set_points([[0, 0, 0]])
        call_log = []
        def track_rate(t):
            call_log.append(t)
            return t
        anim = Animation(m, rate_func=track_rate)
        anim.begin()
        anim.interpolate(0.5)
        assert len(call_log) > 0

    def test_animation_finish(self):
        m = Mobject()
        m.set_points([[0, 0, 0]])
        anim = Animation(m)
        anim.begin()
        anim.finish()


class TestTransform:
    def test_transform_morphs_mobject(self):
        m1 = Mobject()
        m1.set_points([[0, 0, 0]])
        m2 = Mobject()
        m2.set_points([[5, 5, 5]])
        t = Transform(m1, m2)
        t.begin()
        t.interpolate(0.0)
        assert np.allclose(m1.get_points()[0], [0, 0, 0], atol=0.1)
        t.interpolate(1.0)
        assert np.allclose(m1.get_points()[0], [5, 5, 5], atol=0.1)

    def test_transform_midpoint(self):
        m1 = Mobject()
        m1.set_points([[0, 0, 0]])
        m2 = Mobject()
        m2.set_points([[10, 0, 0]])
        t = Transform(m1, m2, rate_func=linear)
        t.begin()
        t.interpolate(0.5)
        assert abs(m1.get_points()[0][0] - 5) < 0.5

    def test_transform_aligns_points(self):
        m1 = VMobject()
        m1.start_new_path([0, 0, 0])
        m1.add_line_to([1, 0, 0])
        m2 = VMobject()
        m2.start_new_path([0, 0, 0])
        m2.add_line_to([1, 0, 0])
        m2.add_line_to([2, 0, 0])
        t = Transform(m1, m2)
        t.begin()

    def test_replacement_transform(self):
        m1 = Mobject()
        m1.set_points([[0, 0, 0]])
        m2 = Mobject()
        m2.set_points([[5, 5, 5]])
        rt = ReplacementTransform(m1, m2)
        assert rt.replace_mobject_with_target_in_scene is True

    def test_move_to_target(self):
        m = Mobject()
        m.set_points([[0, 0, 0]])
        target = m.generate_target()
        target.shift(RIGHT * 5)
        anim = MoveToTarget(m)
        anim.begin()
        anim.interpolate(1.0)
        assert abs(m.get_points()[0][0] - 5) < 0.5

    def test_move_to_target_no_target_raises(self):
        m = Mobject()
        m.set_points([[0, 0, 0]])
        with pytest.raises(ValueError):
            MoveToTarget(m)

    def test_apply_method(self):
        m = Mobject()
        m.set_points([[0, 0, 0]])
        anim = ApplyMethod(m.shift, RIGHT * 3)
        anim.begin()
        anim.interpolate(1.0)
        assert abs(m.get_points()[0][0] - 3) < 0.5

    def test_apply_function(self):
        m = Mobject()
        m.set_points([[0, 0, 0]])
        def func(mob):
            mob.shift(UP * 2)
        anim = ApplyFunction(func, m)
        anim.begin()
        anim.interpolate(1.0)
        assert abs(m.get_points()[0][1] - 2) < 0.5

    def test_restore(self):
        m = Mobject()
        m.set_points([[0, 0, 0]])
        m.save_state()
        m.shift(RIGHT * 10)
        anim = Restore(m)
        anim.begin()
        anim.interpolate(1.0)
        assert np.allclose(m.get_points()[0], [0, 0, 0], atol=0.5)


class TestFading:
    def test_fade_in(self):
        c = Circle()
        c.set_opacity(1.0)
        fi = FadeIn(c)
        fi.begin()
        assert fi.starting_mobject.get_opacity() == 0
        fi.interpolate(1.0)

    def test_fade_in_with_shift(self):
        c = Circle()
        original_y = c.get_center()[1]
        fi = FadeIn(c, shift=UP)
        fi.begin()
        start_center = fi.starting_mobject.get_center()
        assert start_center[1] < original_y

    def test_fade_out(self):
        c = Circle()
        fo = FadeOut(c)
        assert fo.remover is True
        fo.begin()
        fo.interpolate(1.0)

    def test_fade_out_with_shift(self):
        c = Circle()
        fo = FadeOut(c, shift=DOWN)
        fo.begin()

    def test_fade_out_is_remover(self):
        c = Circle()
        fo = FadeOut(c)
        assert fo.remover is True

    def test_fade_transform(self):
        c = Circle()
        r = Rectangle()
        ft = FadeTransform(c, r)
        ft.begin()
        ft.interpolate(0.5)
        ft.finish()


class TestCreationAnimations:
    def test_show_creation(self):
        c = Circle()
        sc = ShowCreation(c)
        sc.begin()
        sc.interpolate(0.0)
        assert c.get_num_points() >= 0
        sc.interpolate(0.5)
        sc.interpolate(1.0)

    def test_show_creation_draws_progressively(self):
        line = Line([0, 0, 0], [4, 0, 0])
        sc = ShowCreation(line, rate_func=linear)
        sc.begin()
        sc.interpolate(0.01)
        early_length = line.get_width()
        sc.interpolate(0.99)
        late_length = line.get_width()
        assert late_length > early_length

    def test_show_creation_lag_ratio(self):
        sc = ShowCreation(Circle(), lag_ratio=1.0)
        assert sc.lag_ratio == 1.0

    def test_write(self):
        c = Circle()
        c.set_fill(RED, opacity=1.0)
        w = Write(c)
        w.begin()
        w.interpolate(0.25)
        w.interpolate(0.75)
        w.finish()

    def test_write_auto_run_time(self):
        small_group = VGroup(*[Circle() for _ in range(5)])
        w = Write(small_group)
        assert w.run_time == 1.0

    def test_show_increasing_subsets(self):
        group = VGroup(*[Dot([i, 0, 0]) for i in range(5)])
        anim = ShowIncreasingSubsets(group, rate_func=linear)
        anim.begin()
        anim.interpolate_mobject(0.0)
        assert len(group.submobjects) == 0
        anim.interpolate_mobject(0.5)
        assert len(group.submobjects) >= 2
        anim.interpolate_mobject(1.0)
        assert len(group.submobjects) == 5


class TestTransformWithVMobject:
    def test_transform_circle_to_square(self):
        c = Circle()
        s = Square()
        t = Transform(c, s, rate_func=linear)
        t.begin()
        t.interpolate(0.5)
        t.interpolate(1.0)
        end_pts = c.get_points()
        target_pts = s.get_points()
        assert len(end_pts) == len(target_pts)

    def test_fade_in_circle(self):
        c = Circle()
        c.set_fill(RED, 1.0)
        fi = FadeIn(c)
        fi.begin()
        fi.interpolate(1.0)
        fi.finish()

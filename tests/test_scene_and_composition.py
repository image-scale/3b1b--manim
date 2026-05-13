import numpy as np
import pytest
from animlib import (
    AnimationGroup, Succession, LaggedStart, LaggedStartMap,
    Scene,
    Animation, Transform, ReplacementTransform, FadeIn, FadeOut,
    ShowCreation, Write,
    Mobject, VMobject, VGroup, Group,
    Circle, Rectangle, Square, Dot, Line,
    ORIGIN, UP, DOWN, LEFT, RIGHT, PI, RED, BLUE, WHITE,
    smooth, linear,
)


class TestAnimationGroup:
    def test_parallel_animations(self):
        c = Circle()
        r = Rectangle()
        ag = AnimationGroup(
            FadeIn(c),
            FadeIn(r),
            lag_ratio=0.0,
        )
        ag.begin()
        ag.interpolate(0.5)
        ag.finish()

    def test_sequential_with_lag_ratio_1(self):
        c = Circle()
        r = Rectangle()
        ag = AnimationGroup(
            FadeIn(c),
            FadeIn(r),
            lag_ratio=1.0,
        )
        ag.begin()
        assert ag.run_time > 1.0

    def test_auto_run_time(self):
        c = Circle()
        r = Rectangle()
        a1 = FadeIn(c)
        a1.run_time = 2.0
        a2 = FadeIn(r)
        a2.run_time = 1.0
        ag = AnimationGroup(a1, a2, lag_ratio=0.0)
        assert ag.run_time == 2.0

    def test_begin_finish_on_sub_animations(self):
        c = Circle()
        r = Rectangle()
        a1 = FadeIn(c)
        a2 = FadeIn(r)
        ag = AnimationGroup(a1, a2)
        ag.begin()
        assert a1.starting_mobject is not None
        assert a2.starting_mobject is not None
        ag.finish()

    def test_interpolate_parallel(self):
        c = Circle()
        r = Rectangle()
        ag = AnimationGroup(
            Transform(c, Rectangle()),
            Transform(r, Circle()),
            lag_ratio=0.0,
        )
        ag.begin()
        ag.interpolate(0.0)
        ag.interpolate(0.5)
        ag.interpolate(1.0)


class TestSuccession:
    def test_succession_sequential(self):
        c = Circle()
        s1 = FadeIn(c)
        s1.run_time = 1.0
        s2 = Transform(c, Rectangle())
        s2.run_time = 1.0
        succ = Succession(s1, s2)
        assert succ.run_time >= 2.0

    def test_succession_transitions(self):
        c = Circle()
        r = Rectangle()
        s1 = FadeIn(c)
        s1.run_time = 1.0
        s2 = FadeIn(r)
        s2.run_time = 1.0
        succ = Succession(s1, s2)
        succ.begin()
        succ.interpolate(0.25)
        succ.interpolate(0.75)
        succ.finish()


class TestLaggedStart:
    def test_lagged_start_default_ratio(self):
        c1, c2, c3 = Circle(), Circle(), Circle()
        ls = LaggedStart(FadeIn(c1), FadeIn(c2), FadeIn(c3))
        assert ls.lag_ratio == 0.05

    def test_lagged_start_custom_ratio(self):
        c1, c2 = Circle(), Circle()
        ls = LaggedStart(FadeIn(c1), FadeIn(c2), lag_ratio=0.2)
        assert ls.lag_ratio == 0.2


class TestLaggedStartMap:
    def test_lagged_start_map(self):
        dots = VGroup(*[Dot([i, 0, 0]) for i in range(5)])
        lsm = LaggedStartMap(FadeIn, dots)
        assert len(lsm.animations) == 5
        lsm.begin()
        lsm.interpolate(0.5)
        lsm.finish()


class TestSceneBasics:
    def test_scene_creation(self):
        s = Scene()
        assert len(s.get_mobjects()) == 0

    def test_scene_add(self):
        s = Scene()
        c = Circle()
        s.add(c)
        assert c in s.get_mobjects()

    def test_scene_add_duplicate(self):
        s = Scene()
        c = Circle()
        s.add(c)
        s.add(c)
        assert s.get_mobjects().count(c) == 1

    def test_scene_remove(self):
        s = Scene()
        c = Circle()
        s.add(c)
        s.remove(c)
        assert c not in s.get_mobjects()

    def test_scene_clear(self):
        s = Scene()
        s.add(Circle(), Rectangle())
        s.clear()
        assert len(s.get_mobjects()) == 0

    def test_scene_add_rejects_non_mobject(self):
        s = Scene()
        with pytest.raises(TypeError):
            s.add("not a mobject")


class TestScenePlay:
    def test_play_fade_in(self):
        s = Scene()
        c = Circle()
        s.play(FadeIn(c))
        assert c in s.get_mobjects()
        assert s.num_plays == 1

    def test_play_auto_adds_mobject(self):
        s = Scene()
        c = Circle()
        assert c not in s.get_mobjects()
        s.play(FadeIn(c))
        assert c in s.get_mobjects()

    def test_play_transform(self):
        s = Scene()
        c = Circle()
        r = Rectangle()
        s.add(c)
        s.play(Transform(c, r))
        assert s.num_plays == 1

    def test_play_replacement_transform(self):
        s = Scene()
        c = Circle()
        r = Rectangle()
        s.add(c)
        s.play(ReplacementTransform(c, r))
        assert c not in s.get_mobjects()
        assert r in s.get_mobjects()

    def test_play_remover(self):
        s = Scene()
        c = Circle()
        s.add(c)
        s.play(FadeOut(c))
        assert c not in s.get_mobjects()

    def test_play_advances_time(self):
        s = Scene()
        c = Circle()
        initial_time = s.get_time()
        s.play(FadeIn(c), run_time=2.0)
        assert s.get_time() > initial_time

    def test_play_multiple_animations(self):
        s = Scene()
        c = Circle()
        r = Rectangle()
        s.play(FadeIn(c), FadeIn(r))
        assert c in s.get_mobjects()
        assert r in s.get_mobjects()


class TestSceneWait:
    def test_wait_default(self):
        s = Scene()
        t0 = s.get_time()
        s.wait()
        assert s.get_time() > t0

    def test_wait_with_duration(self):
        s = Scene()
        t0 = s.get_time()
        s.wait(duration=2.0)
        elapsed = s.get_time() - t0
        assert abs(elapsed - 2.0) < 0.1

    def test_wait_stop_condition(self):
        s = Scene()
        counter = [0]
        def condition():
            counter[0] += 1
            return counter[0] >= 3
        s.wait(duration=10.0, stop_condition=condition)
        assert s.get_time() < 10.0

    def test_wait_runs_updaters(self):
        s = Scene()
        m = Mobject()
        m.set_points([[0, 0, 0]])
        call_count = [0]
        def updater(mob, dt):
            call_count[0] += 1
        m.add_updater(updater, call_func=False)
        s.add(m)
        s.wait(duration=0.5)
        assert call_count[0] > 0


class TestSceneUpdaters:
    def test_updaters_run_during_play(self):
        s = Scene()
        tracker = Mobject()
        tracker.set_points([[0, 0, 0]])
        call_count = [0]
        def updater(mob, dt):
            call_count[0] += 1
        tracker.add_updater(updater, call_func=False)
        s.add(tracker)
        c = Circle()
        s.play(FadeIn(c), run_time=0.5)
        assert call_count[0] > 0


class TestSceneConstruct:
    def test_scene_run(self):
        class MyScene(Scene):
            def construct(self):
                c = Circle()
                self.add(c)
                self.play(FadeIn(c), run_time=0.1)
                self.wait(duration=0.1)

        scene = MyScene()
        scene.run()
        assert len(scene.get_mobjects()) > 0


class TestSceneBringFrontBack:
    def test_bring_to_front(self):
        s = Scene()
        c = Circle()
        r = Rectangle()
        s.add(c, r)
        s.bring_to_front(c)
        assert s.get_mobjects()[-1] is c

    def test_bring_to_back(self):
        s = Scene()
        c = Circle()
        r = Rectangle()
        s.add(c, r)
        s.bring_to_back(r)
        assert s.get_mobjects()[0] is r

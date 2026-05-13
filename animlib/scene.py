import numpy as np
from animlib.animation import Animation, prepare_animation
from animlib.easing import smooth
from animlib.mobject import Mobject


class Scene:
    def __init__(
        self,
        skip_animations=False,
        always_update_mobjects=False,
        default_wait_time=1.0,
        fps=30,
    ):
        self.mobjects = []
        self.time = 0.0
        self.num_plays = 0
        self.skip_animations = skip_animations
        self.always_update_mobjects = always_update_mobjects
        self.default_wait_time = default_wait_time
        self.fps = fps

    def setup(self):
        pass

    def construct(self):
        pass

    def run(self):
        self.setup()
        self.construct()
        self.tear_down()

    def tear_down(self):
        pass

    # --- Mobject management ---

    def add(self, *mobjects):
        for mob in mobjects:
            if not isinstance(mob, Mobject):
                raise TypeError(f"Expected Mobject, got {type(mob)}")
            if mob not in self.mobjects:
                self.mobjects.append(mob)
        self.mobjects.sort(key=lambda m: m.z_index)
        return self

    def remove(self, *mobjects):
        for mob in mobjects:
            family = mob.get_family()
            self.mobjects = [m for m in self.mobjects if m not in family]
        return self

    def clear(self):
        self.mobjects = []
        return self

    def get_mobjects(self):
        return list(self.mobjects)

    def bring_to_front(self, *mobjects):
        for mob in mobjects:
            if mob in self.mobjects:
                self.mobjects.remove(mob)
            self.mobjects.append(mob)
        return self

    def bring_to_back(self, *mobjects):
        for mob in mobjects:
            if mob in self.mobjects:
                self.mobjects.remove(mob)
        self.mobjects = list(mobjects) + self.mobjects
        return self

    def replace(self, old_mobject, *new_mobjects):
        if old_mobject in self.mobjects:
            idx = self.mobjects.index(old_mobject)
            self.mobjects[idx:idx + 1] = list(new_mobjects)
        return self

    # --- Animation ---

    def play(self, *proto_animations, run_time=None, rate_func=None, lag_ratio=None):
        animations = [prepare_animation(a) for a in proto_animations]
        for anim in animations:
            if run_time is not None:
                anim.run_time = run_time
            if rate_func is not None:
                anim.rate_func = rate_func
            if lag_ratio is not None:
                anim.lag_ratio = lag_ratio

        self._begin_animations(animations)
        self._progress_through_animations(animations)
        self._finish_animations(animations)
        self.num_plays += 1

    def _begin_animations(self, animations):
        for anim in animations:
            anim.begin()
            mob = anim.mobject
            if mob not in self.mobjects:
                self.add(mob)

    def _progress_through_animations(self, animations):
        max_run_time = max(anim.run_time for anim in animations) if animations else 0
        if max_run_time <= 0:
            return
        dt = 1.0 / self.fps
        t = 0.0
        while t <= max_run_time:
            for anim in animations:
                alpha = min(t / anim.run_time, 1.0) if anim.run_time > 0 else 1.0
                anim.interpolate(alpha)
            self._update_mobjects(dt)
            self.time += dt
            t += dt

    def _finish_animations(self, animations):
        for anim in animations:
            anim.finish()
            anim.clean_up_from_scene(self)

    def wait(self, duration=None, stop_condition=None):
        if duration is None:
            duration = self.default_wait_time
        dt = 1.0 / self.fps
        t = 0.0
        while t < duration:
            self._update_mobjects(dt)
            self.time += dt
            t += dt
            if stop_condition is not None and stop_condition():
                break

    def _update_mobjects(self, dt):
        for mob in self.mobjects:
            mob.update(dt=dt, recurse=True)

    # --- Queries ---

    def get_time(self):
        return self.time

    def __repr__(self):
        return f"Scene(mobjects={len(self.mobjects)}, time={self.time:.2f})"

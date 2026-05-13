import numpy as np
from animlib.easing import smooth, linear
from animlib.bezier import interpolate, integer_interpolate
from animlib.constants import ORIGIN, OUT
from animlib.math_utils import clip


class Animation:
    def __init__(
        self,
        mobject,
        run_time=1.0,
        rate_func=None,
        lag_ratio=0.0,
        remover=False,
        final_alpha_value=1.0,
        suspend_mobject_updating=False,
        **kwargs,
    ):
        self.mobject = mobject
        self.run_time = run_time
        self.rate_func = rate_func if rate_func is not None else smooth
        self.lag_ratio = lag_ratio
        self.remover = remover
        self.final_alpha_value = final_alpha_value
        self.suspend_mobject_updating = suspend_mobject_updating
        self.starting_mobject = None
        self.families = None

    def begin(self):
        self.starting_mobject = self.create_starting_mobject()
        self._setup_families()
        self.interpolate(0)

    def create_starting_mobject(self):
        return self.mobject.copy()

    def _setup_families(self):
        mob_family = self.mobject.get_family()
        start_family = self.starting_mobject.get_family()
        n = min(len(mob_family), len(start_family))
        self.families = list(zip(mob_family[:n], start_family[:n]))

    def interpolate(self, alpha):
        self.interpolate_mobject(alpha)

    def interpolate_mobject(self, alpha):
        for i, (submob, start_submob) in enumerate(self.families):
            sub_alpha = self.get_sub_alpha(alpha, i, len(self.families))
            self.interpolate_submobject(submob, start_submob, sub_alpha)

    def interpolate_submobject(self, submob, start_submob, alpha):
        submob.interpolate(start_submob, start_submob, alpha)

    def get_sub_alpha(self, alpha, index, num_submobjects):
        if num_submobjects <= 1 or self.lag_ratio == 0:
            return self.rate_func(alpha)

        full_length = 1 + (num_submobjects - 1) * self.lag_ratio
        start = index * self.lag_ratio / full_length
        end = start + 1.0 / full_length
        sub_alpha = clip((alpha - start) / (end - start), 0, 1)
        return self.rate_func(sub_alpha)

    def finish(self):
        self.interpolate(self.final_alpha_value)

    def clean_up_from_scene(self, scene):
        if self.remover and scene is not None:
            scene.remove(self.mobject)

    def get_all_mobjects(self):
        return [self.mobject, self.starting_mobject]

    def update_mobjects(self, dt):
        for mob in self.get_all_mobjects():
            if mob is not None and mob is not self.mobject:
                mob.update(dt=dt)

    def copy(self):
        import copy
        return copy.copy(self)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.mobject.__class__.__name__})"


def prepare_animation(anim):
    if hasattr(anim, 'build'):
        return anim.build()
    return anim

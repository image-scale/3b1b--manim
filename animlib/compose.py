import numpy as np
from animlib.animation import Animation, prepare_animation
from animlib.easing import smooth, linear
from animlib.bezier import interpolate, integer_interpolate
from animlib.math_utils import clip
from animlib.mobject import Mobject, Group
from animlib.vmobject import VGroup


class AnimationGroup(Animation):
    def __init__(
        self,
        *animations,
        run_time=-1,
        lag_ratio=0.0,
        group=None,
        rate_func=None,
        **kwargs,
    ):
        self.animations = [prepare_animation(a) for a in animations]
        self.specified_run_time = run_time
        if group is not None:
            self.group = group
        else:
            all_mobs = []
            for anim in self.animations:
                if anim.mobject not in all_mobs:
                    all_mobs.append(anim.mobject)
            has_vmobject = all(hasattr(m, '_fill_color') for m in all_mobs)
            if has_vmobject and all_mobs:
                self.group = VGroup(*all_mobs)
            elif all_mobs:
                self.group = Group(*all_mobs)
            else:
                self.group = Group()
        if rate_func is None:
            rate_func = linear
        super().__init__(
            self.group,
            lag_ratio=lag_ratio,
            rate_func=rate_func,
            **kwargs,
        )
        self.timings = self._build_timings()
        if self.specified_run_time > 0:
            self.run_time = self.specified_run_time
        elif self.timings:
            self.run_time = max(end for _, _, end in self.timings)
        else:
            self.run_time = 1.0

    def _build_timings(self):
        if not self.animations:
            return []
        timings = []
        max_end = 0
        for i, anim in enumerate(self.animations):
            if self.lag_ratio == 0:
                start_time = 0
            else:
                start_time = i * self.lag_ratio * anim.run_time
            end_time = start_time + anim.run_time
            max_end = max(max_end, end_time)
            timings.append((anim, start_time, end_time))
        return timings

    def begin(self):
        for anim, _, _ in self.timings:
            anim.begin()
        self.starting_mobject = self.group.copy()
        self.families = [(self.group, self.starting_mobject)]

    def interpolate(self, alpha):
        time = self.rate_func(alpha) * self.run_time
        for anim, start, end in self.timings:
            duration = end - start
            if duration < 1e-10:
                sub_alpha = 1.0 if time >= start else 0.0
            elif time <= start:
                sub_alpha = 0.0
            elif time >= end:
                sub_alpha = 1.0
            else:
                sub_alpha = (time - start) / duration
            anim.interpolate(clip(sub_alpha, 0, 1))

    def finish(self):
        for anim, _, _ in self.timings:
            anim.finish()

    def clean_up_from_scene(self, scene):
        for anim, _, _ in self.timings:
            anim.clean_up_from_scene(scene)

    def get_all_mobjects(self):
        result = [self.group]
        for anim, _, _ in self.timings:
            result.extend(anim.get_all_mobjects())
        return result

    def update_mobjects(self, dt):
        for anim, _, _ in self.timings:
            anim.update_mobjects(dt)


class Succession(AnimationGroup):
    def __init__(self, *animations, lag_ratio=1.0, **kwargs):
        super().__init__(*animations, lag_ratio=lag_ratio, **kwargs)

    def begin(self):
        if self.timings:
            self.timings[0][0].begin()
        self.active_index = 0
        self.starting_mobject = self.group.copy()
        self.families = [(self.group, self.starting_mobject)]

    def interpolate(self, alpha):
        time = self.rate_func(alpha) * self.run_time
        for i, (anim, start, end) in enumerate(self.timings):
            if time < start:
                continue
            if time > end:
                if i == self.active_index and i + 1 < len(self.timings):
                    anim.finish()
                    self.active_index = i + 1
                    self.timings[i + 1][0].begin()
                continue
            if i > self.active_index:
                for j in range(self.active_index, i):
                    self.timings[j][0].finish()
                self.timings[i][0].begin()
                self.active_index = i
            duration = end - start
            if duration > 1e-10:
                sub_alpha = (time - start) / duration
            else:
                sub_alpha = 1.0
            anim.interpolate(clip(sub_alpha, 0, 1))
            return

    def finish(self):
        for anim, _, _ in self.timings:
            if hasattr(anim, 'starting_mobject') and anim.starting_mobject is not None:
                anim.finish()

    def clean_up_from_scene(self, scene):
        for anim, _, _ in self.timings:
            anim.clean_up_from_scene(scene)


class LaggedStart(AnimationGroup):
    def __init__(self, *animations, lag_ratio=0.05, **kwargs):
        super().__init__(*animations, lag_ratio=lag_ratio, **kwargs)


class LaggedStartMap(LaggedStart):
    def __init__(self, anim_func, group, run_time=2.0, lag_ratio=0.05, **kwargs):
        anim_kwargs = {}
        anim_keys = {'run_time', 'rate_func', 'lag_ratio', 'remover', 'final_alpha_value'}
        remaining = {}
        for k, v in kwargs.items():
            if k in anim_keys:
                remaining[k] = v
            else:
                anim_kwargs[k] = v
        animations = [anim_func(submob, **anim_kwargs) for submob in group.submobjects]
        remaining['run_time'] = run_time
        remaining['lag_ratio'] = lag_ratio
        super().__init__(*animations, **remaining)

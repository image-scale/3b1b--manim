import numpy as np
from animlib.animation import Animation
from animlib.transform import Transform
from animlib.easing import smooth, linear
from animlib.bezier import interpolate
from animlib.constants import ORIGIN, WHITE, BLACK, DEFAULT_STROKE_WIDTH
from animlib.vmobject import VMobject


class Fade(Transform):
    def __init__(self, mobject, shift=None, scale=1.0, **kwargs):
        self.shift_vec = np.array(shift, dtype=float) if shift is not None else ORIGIN.copy()
        self.scale_factor = scale
        super().__init__(mobject, **kwargs)


class FadeIn(Fade):
    def __init__(self, mobject, shift=None, scale=1.0, **kwargs):
        super().__init__(mobject, shift=shift, scale=scale, **kwargs)

    def create_starting_mobject(self):
        start = self.mobject.copy()
        start.set_opacity(0)
        if self.scale_factor != 1.0 and self.scale_factor != 0:
            start.scale(1.0 / self.scale_factor)
        if np.any(np.abs(self.shift_vec) > 1e-10):
            start.shift(-self.shift_vec)
        return start

    def create_target(self):
        return self.mobject.copy()


class FadeOut(Fade):
    def __init__(self, mobject, shift=None, scale=1.0, **kwargs):
        kwargs.setdefault('remover', True)
        kwargs.setdefault('final_alpha_value', 0.0)
        super().__init__(mobject, shift=shift, scale=scale, **kwargs)

    def create_target(self):
        target = self.mobject.copy()
        target.set_opacity(0)
        if self.scale_factor != 1.0:
            target.scale(self.scale_factor)
        if np.any(np.abs(self.shift_vec) > 1e-10):
            target.shift(self.shift_vec)
        return target


class FadeTransform(Transform):
    def __init__(self, mobject, target_mobject, stretch=True, dim_to_match=1, **kwargs):
        self.original_target = target_mobject
        kwargs.setdefault('replace_mobject_with_target_in_scene', True)
        super().__init__(mobject, target_mobject=target_mobject, **kwargs)

    def begin(self):
        self.mobject.save_state()
        super().begin()

    def clean_up_from_scene(self, scene):
        super().clean_up_from_scene(scene)

    def create_target(self):
        return self.original_target.copy()


class ShowPartial(Animation):
    def __init__(self, mobject, **kwargs):
        super().__init__(mobject, **kwargs)

    def begin(self):
        self.starting_mobject = self.create_starting_mobject()
        self._setup_families()
        self.interpolate(0)

    def _setup_families(self):
        mob_family = self.mobject.get_family()
        start_family = self.starting_mobject.get_family()
        n = min(len(mob_family), len(start_family))
        self.families = list(zip(mob_family[:n], start_family[:n]))

    def interpolate_submobject(self, submob, start_submob, alpha):
        a, b = self.get_bounds(alpha)
        if isinstance(submob, VMobject) and isinstance(start_submob, VMobject):
            submob.pointwise_become_partial(start_submob, a, b)
        else:
            submob.interpolate(start_submob, start_submob, alpha)

    def get_bounds(self, alpha):
        raise NotImplementedError


class ShowCreation(ShowPartial):
    def __init__(self, mobject, lag_ratio=1.0, **kwargs):
        super().__init__(mobject, lag_ratio=lag_ratio, **kwargs)

    def get_bounds(self, alpha):
        return (0, alpha)


class Uncreate(ShowCreation):
    def __init__(self, mobject, **kwargs):
        kwargs.setdefault('remover', True)
        kwargs.setdefault('rate_func', lambda t: smooth(1 - t))
        super().__init__(mobject, **kwargs)


class DrawBorderThenFill(Animation):
    def __init__(
        self,
        vmobject,
        run_time=2.0,
        stroke_color=None,
        stroke_width=2.0,
        rate_func=None,
        **kwargs,
    ):
        self.stroke_color = stroke_color or WHITE
        self.outline_width = stroke_width
        if rate_func is None:
            rate_func = double_smooth_wrapper
        super().__init__(vmobject, run_time=run_time, rate_func=rate_func, **kwargs)

    def begin(self):
        self.starting_mobject = self.create_starting_mobject()
        self.outline = self.get_outline()
        self._setup_families()
        self.interpolate(0)

    def create_starting_mobject(self):
        return self.mobject.copy()

    def get_outline(self):
        outline = self.starting_mobject.copy()
        if isinstance(outline, VMobject):
            outline.set_fill(opacity=0)
            outline.set_stroke(
                color=self.stroke_color,
                width=self.outline_width,
            )
        return outline

    def _setup_families(self):
        mob_family = self.mobject.get_family()
        start_family = self.starting_mobject.get_family()
        outline_family = self.outline.get_family()
        n = min(len(mob_family), len(start_family), len(outline_family))
        self.families = list(zip(
            mob_family[:n], start_family[:n], outline_family[:n]
        ))

    def interpolate_mobject(self, alpha):
        for i, (submob, start, outline) in enumerate(self.families):
            sub_alpha = self.get_sub_alpha(alpha, i, len(self.families))
            self.interpolate_submobject(submob, start, outline, sub_alpha)

    def interpolate_submobject(self, submob, start, outline, alpha):
        if alpha < 0.5:
            draw_alpha = alpha * 2
            if isinstance(submob, VMobject) and isinstance(outline, VMobject):
                submob.pointwise_become_partial(outline, 0, draw_alpha)
            submob.set_opacity(0)
            if isinstance(submob, VMobject):
                submob.set_stroke(opacity=draw_alpha)
        else:
            fill_alpha = (alpha - 0.5) * 2
            submob.interpolate(outline, start, fill_alpha)


def double_smooth_wrapper(t):
    from animlib.easing import double_smooth
    return double_smooth(t)


class Write(DrawBorderThenFill):
    def __init__(self, vmobject, run_time=-1, lag_ratio=-1, stroke_color=None, **kwargs):
        family_size = len(vmobject.get_family())
        if run_time < 0:
            run_time = 1.0 if family_size < 15 else 2.0
        if lag_ratio < 0:
            lag_ratio = min(4.0 / max(family_size, 1), 0.2)
        super().__init__(
            vmobject,
            run_time=run_time,
            lag_ratio=lag_ratio,
            stroke_color=stroke_color,
            **kwargs,
        )


class ShowIncreasingSubsets(Animation):
    def __init__(self, group, **kwargs):
        self.all_submobs = list(group.submobjects)
        super().__init__(group, **kwargs)

    def begin(self):
        self.starting_mobject = self.mobject.copy()
        self.families = [(self.mobject, self.starting_mobject)]
        self.interpolate(0)

    def interpolate_mobject(self, alpha):
        n_to_show = int(np.round(alpha * len(self.all_submobs)))
        n_to_show = max(0, min(n_to_show, len(self.all_submobs)))
        self.mobject.submobjects = list(self.all_submobs[:n_to_show])

    def finish(self):
        self.interpolate(self.final_alpha_value)

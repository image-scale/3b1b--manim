import numpy as np
from animlib.animation import Animation
from animlib.easing import smooth
from animlib.bezier import interpolate
from animlib.constants import ORIGIN, OUT, PI


def _path_along_arc(arc_angle, axis=None):
    if axis is None:
        axis = np.array([0.0, 0.0, 1.0])

    def path_func(start_points, end_points, alpha):
        if abs(arc_angle) < 0.01:
            return interpolate(start_points, end_points, alpha)
        start_points = np.array(start_points, dtype=float)
        end_points = np.array(end_points, dtype=float)
        midpoints = (start_points + end_points) / 2
        diff = end_points - start_points

        from animlib.math_utils import rotation_matrix
        rot_90 = rotation_matrix(PI / 2, axis)
        perp = (rot_90 @ diff.T).T

        half_angle = arc_angle / 2
        if abs(np.tan(half_angle)) > 1e-10:
            offset = perp / (2 * np.tan(half_angle))
        else:
            return interpolate(start_points, end_points, alpha)

        centers = midpoints + offset
        angle = alpha * arc_angle
        cos_a = np.cos(angle)
        sin_a = np.sin(angle)
        from_center = start_points - centers
        result = centers + cos_a * from_center
        cross_part = np.cross(
            np.broadcast_to(axis, from_center.shape),
            from_center
        )
        result = result + sin_a * cross_part
        return result

    return path_func


class Transform(Animation):
    def __init__(
        self,
        mobject,
        target_mobject=None,
        path_arc=0.0,
        path_arc_axis=None,
        path_func=None,
        replace_mobject_with_target_in_scene=False,
        **kwargs,
    ):
        self.target_mobject = target_mobject
        self.path_arc = path_arc
        self.path_arc_axis = path_arc_axis if path_arc_axis is not None else OUT.copy()
        self.replace_mobject_with_target_in_scene = replace_mobject_with_target_in_scene
        if path_func is not None:
            self.path_func = path_func
        elif abs(path_arc) > 0.01:
            self.path_func = _path_along_arc(path_arc, self.path_arc_axis)
        else:
            self.path_func = interpolate
        super().__init__(mobject, **kwargs)

    def begin(self):
        self.target_copy = self.create_target()
        self.mobject.align_data_and_family(self.target_copy)
        self.starting_mobject = self.create_starting_mobject()
        self.starting_mobject.align_data_and_family(self.target_copy)
        self._setup_transform_families()
        self.interpolate(0)

    def create_target(self):
        if self.target_mobject is not None:
            return self.target_mobject.copy()
        return self.mobject.copy()

    def _setup_transform_families(self):
        mob_family = self.mobject.get_family()
        start_family = self.starting_mobject.get_family()
        target_family = self.target_copy.get_family()
        n = min(len(mob_family), len(start_family), len(target_family))
        self.families = list(zip(
            mob_family[:n], start_family[:n], target_family[:n]
        ))

    def interpolate_mobject(self, alpha):
        for i, family_tuple in enumerate(self.families):
            submob, start_submob, target_submob = family_tuple
            sub_alpha = self.get_sub_alpha(alpha, i, len(self.families))
            self.interpolate_submobject(submob, start_submob, target_submob, sub_alpha)

    def interpolate_submobject(self, submob, start_submob, target_submob, alpha):
        submob.interpolate(start_submob, target_submob, alpha, self.path_func)

    def clean_up_from_scene(self, scene):
        super().clean_up_from_scene(scene)
        if self.replace_mobject_with_target_in_scene and scene is not None:
            scene.remove(self.mobject)
            if self.target_mobject is not None:
                scene.add(self.target_mobject)

    def get_all_mobjects(self):
        result = [self.mobject, self.starting_mobject]
        if hasattr(self, 'target_copy'):
            result.append(self.target_copy)
        return result


class ReplacementTransform(Transform):
    def __init__(self, mobject, target_mobject, **kwargs):
        super().__init__(
            mobject,
            target_mobject=target_mobject,
            replace_mobject_with_target_in_scene=True,
            **kwargs,
        )


class MoveToTarget(Transform):
    def __init__(self, mobject, **kwargs):
        if mobject.target is None:
            raise ValueError("MoveToTarget requires mobject.target to be set (call generate_target() first)")
        super().__init__(mobject, target_mobject=mobject.target, **kwargs)


class ApplyMethod(Transform):
    def __init__(self, method, *args, **kwargs):
        self.method = method
        self.method_args = args
        anim_kwargs = {}
        method_kwargs = {}
        anim_keys = {
            'run_time', 'rate_func', 'lag_ratio', 'remover',
            'final_alpha_value', 'path_arc', 'path_func',
        }
        for k, v in kwargs.items():
            if k in anim_keys:
                anim_kwargs[k] = v
            else:
                method_kwargs[k] = v
        self.method_kwargs = method_kwargs
        mobject = method.__self__
        super().__init__(mobject, **anim_kwargs)

    def create_target(self):
        target = self.mobject.copy()
        method_name = self.method.__name__
        getattr(target, method_name)(*self.method_args, **self.method_kwargs)
        return target


class ApplyFunction(Transform):
    def __init__(self, function, mobject, **kwargs):
        self.function = function
        super().__init__(mobject, **kwargs)

    def create_target(self):
        target = self.mobject.copy()
        self.function(target)
        return target


class Restore(Transform):
    def __init__(self, mobject, **kwargs):
        if mobject.saved_state is None:
            raise ValueError("Restore requires mobject.saved_state to be set (call save_state() first)")
        super().__init__(mobject, target_mobject=mobject.saved_state, **kwargs)

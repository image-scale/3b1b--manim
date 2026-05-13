import numpy as np
from animlib.bezier import interpolate
from animlib.math_utils import get_norm, rotation_matrix
from animlib.constants import OUT, PI


STRAIGHT_PATH_THRESHOLD = 0.01


def straight_path(start_points, end_points, alpha):
    return interpolate(start_points, end_points, alpha)


def path_along_arc(arc_angle, axis=None):
    if axis is None:
        axis = np.array([0.0, 0.0, 1.0])
    axis = np.array(axis, dtype=float)

    if abs(arc_angle) < STRAIGHT_PATH_THRESHOLD:
        return straight_path

    def path_func(start_points, end_points, alpha):
        start_points = np.array(start_points, dtype=float)
        end_points = np.array(end_points, dtype=float)
        midpoints = (start_points + end_points) / 2
        diff = end_points - start_points
        rot_90 = rotation_matrix(PI / 2, axis)

        if diff.ndim == 1:
            perp = rot_90 @ diff
        else:
            perp = (rot_90 @ diff.T).T

        half_angle = arc_angle / 2
        tan_half = np.tan(half_angle)
        if abs(tan_half) < 1e-10:
            return interpolate(start_points, end_points, alpha)

        offset = perp / (2 * tan_half)
        centers = midpoints + offset
        angle = alpha * arc_angle
        cos_a = np.cos(angle)
        sin_a = np.sin(angle)
        from_center = start_points - centers

        result = centers + cos_a * from_center
        if from_center.ndim == 1:
            cross_part = np.cross(axis, from_center)
        else:
            cross_part = np.cross(
                np.broadcast_to(axis, from_center.shape),
                from_center
            )
        result = result + sin_a * cross_part
        return result

    return path_func


def clockwise_path():
    return path_along_arc(-PI)


def counterclockwise_path():
    return path_along_arc(PI)

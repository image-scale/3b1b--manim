import numpy as np
import math
from functools import lru_cache


def clip(a, min_val, max_val):
    if a < min_val:
        return min_val
    elif a > max_val:
        return max_val
    return a


@lru_cache(maxsize=20)
def choose(n, k):
    return math.comb(n, k)


def normalize(vect, fallback=None):
    vect = np.array(vect, dtype=float)
    norm = np.linalg.norm(vect)
    if norm > 0:
        return vect / norm
    if fallback is not None:
        return np.array(fallback, dtype=float)
    return np.zeros_like(vect)


def get_norm(vect):
    return np.linalg.norm(vect)


def cross(v1, v2):
    return np.cross(v1, v2)


def cross2d(a, b):
    return a[..., 0] * b[..., 1] - a[..., 1] * b[..., 0]


def angle_of_vector(vector):
    return np.arctan2(vector[1], vector[0])


def rotation_matrix(angle, axis=None):
    if axis is None:
        axis = np.array([0.0, 0.0, 1.0])
    axis = normalize(axis, fallback=[0.0, 0.0, 1.0])
    c = math.cos(angle)
    s = math.sin(angle)
    t = 1 - c
    x, y, z = axis
    return np.array([
        [t * x * x + c, t * x * y - s * z, t * x * z + s * y],
        [t * x * y + s * z, t * y * y + c, t * y * z - s * x],
        [t * x * z - s * y, t * y * z + s * x, t * z * z + c],
    ])


def rotate_vector(vector, angle, axis=None):
    if axis is None:
        axis = np.array([0.0, 0.0, 1.0])
    mat = rotation_matrix(angle, axis)
    return mat @ np.array(vector, dtype=float)


def center_of_mass(points):
    points = np.array(points, dtype=float)
    return np.mean(points, axis=0)


def midpoint(p1, p2):
    return (np.array(p1, dtype=float) + np.array(p2, dtype=float)) / 2.0


def compass_directions(n=4, start_vect=None):
    if start_vect is None:
        start_vect = np.array([1.0, 0.0, 0.0])
    angle_step = 2 * np.pi / n
    return np.array([
        rotate_vector(start_vect, k * angle_step)
        for k in range(n)
    ])


def get_unit_normal(v1, v2, tol=1e-6):
    cp = cross(v1, v2)
    norm = get_norm(cp)
    if norm < tol:
        return np.array([0.0, -1.0, 0.0])
    return cp / norm

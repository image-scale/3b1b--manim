"""Spatial operations utilities."""
import numpy as np


def cross(v1, v2):
    """Compute the cross product of two 3D vectors."""
    return np.cross(v1, v2)


def get_norm(v):
    """Get the Euclidean norm (length) of a vector."""
    return np.linalg.norm(v)


def get_dist(v1, v2):
    """Get the Euclidean distance between two points."""
    return get_norm(np.array(v1) - np.array(v2))


def normalize(v, fallback=None):
    """Return the unit vector in the direction of v.

    If v has zero length, return fallback (or zero vector if not specified).
    """
    norm = get_norm(v)
    if norm == 0:
        if fallback is not None:
            return fallback
        return np.zeros_like(v)
    return np.array(v) / norm


def cross2d(v1, v2):
    """Compute the 2D cross product (scalar).

    This is the z-component of the 3D cross product of vectors in the xy-plane.
    """
    return v1[0] * v2[1] - v1[1] * v2[0]


def midpoint(p1, p2):
    """Return the midpoint between two points."""
    return (np.array(p1) + np.array(p2)) / 2.0

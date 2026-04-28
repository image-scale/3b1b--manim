"""Bezier curve utilities."""
import numpy as np
from manimlib.utils.simple_functions import choose


def bezier(points):
    """Return a function that evaluates the Bezier curve defined by points at parameter t.

    Uses the Bernstein polynomial formulation of Bezier curves.
    """
    n = len(points) - 1
    if n < 0:
        raise Exception("Cannot create bezier curve from empty list of points")

    def result(t):
        # For arrays of t values, use broadcasting
        coeffs = np.array([
            choose(n, k) * ((1 - t) ** (n - k)) * (t ** k)
            for k in range(n + 1)
        ])
        # Sum up the weighted control points
        return sum(c * p for c, p in zip(coeffs, points))

    return result


def partial_bezier_points(points, a, b):
    """Get the control points for a subsection of the bezier curve from t=a to t=b.

    Uses De Casteljau's algorithm to subdivide the curve.
    """
    if a == 1.0:
        # At t=1, all points collapse to the end point
        return [points[-1]] * len(points)

    # First subdivide at a to get the second half starting at a
    a_points = _split_bezier(points, a)[1]

    # Then normalize b to the new parameter space
    if a < 1.0:
        new_b = (b - a) / (1 - a)
    else:
        new_b = 0

    # Subdivide at new_b to get the first half ending at b
    return _split_bezier(a_points, new_b)[0]


def _split_bezier(points, t):
    """Split a bezier curve at parameter t into two curves.

    Returns (left_points, right_points) where left is [0, t] and right is [t, 1].
    """
    n = len(points)
    if n == 1:
        return [points[0]], [points[0]]

    # De Casteljau's algorithm
    # Build up the triangle of intermediate points
    levels = [list(points)]
    for i in range(n - 1):
        prev = levels[-1]
        new_level = []
        for j in range(len(prev) - 1):
            p = (1 - t) * np.array(prev[j]) + t * np.array(prev[j + 1])
            new_level.append(p)
        levels.append(new_level)

    # Left curve: first point of each level
    left = [level[0] for level in levels]
    # Right curve: last point of each level (reversed)
    right = [level[-1] for level in levels]

    return left, right

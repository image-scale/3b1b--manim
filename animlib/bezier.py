import numpy as np
from animlib.math_utils import choose, cross2d, get_norm, midpoint, normalize


def bezier(points):
    n = len(points) - 1
    points = [np.array(p, dtype=float) for p in points]
    coeffs = [choose(n, k) for k in range(n + 1)]

    def evaluate(t):
        result = np.zeros_like(points[0], dtype=float)
        for k in range(n + 1):
            result = result + coeffs[k] * ((1 - t) ** (n - k)) * (t ** k) * points[k]
        return result

    return evaluate


def partial_bezier_points(points, a, b):
    if a == 0:
        return _split_bezier(points, b)[0]
    a_to_1 = _split_bezier(points, a)[1]
    if b == 1:
        return a_to_1
    end_prop = (b - a) / (1 - a)
    return _split_bezier(a_to_1, end_prop)[0]


def _split_bezier(points, t):
    points = [np.array(p, dtype=float) for p in points]
    n = len(points)
    left = []
    right = []
    work = list(points)
    left.append(work[0].copy())
    right.append(work[-1].copy())
    for _ in range(n - 1):
        new_work = []
        for i in range(len(work) - 1):
            new_work.append((1 - t) * work[i] + t * work[i + 1])
        work = new_work
        left.append(work[0].copy())
        right.append(work[-1].copy())
    right.reverse()
    return left, right


def interpolate(start, end, alpha):
    return (1 - alpha) * np.array(start, dtype=float) + alpha * np.array(end, dtype=float)


def integer_interpolate(start, end, alpha):
    full = int(interpolate(start, end, alpha))
    if full == end:
        full -= 1
    residue = (alpha * (end - start) - (full - start)) / 1.0
    return full, residue


def inverse_interpolate(start, end, value):
    if start == end:
        return 0.0
    return (value - start) / (end - start)


def quadratic_bezier_points_for_arc(angle, n_components=8):
    n = n_components
    if n == 0:
        return np.zeros((1, 3))
    theta = angle / n
    points = np.zeros((2 * n + 1, 3))
    for i in range(n + 1):
        a = i * theta
        points[2 * i] = [np.cos(a), np.sin(a), 0]
    if abs(theta) > 1e-10:
        d = 1.0 / np.cos(theta / 2)
        for i in range(n):
            a = (i + 0.5) * theta
            points[2 * i + 1] = [d * np.cos(a), d * np.sin(a), 0]
    else:
        for i in range(n):
            points[2 * i + 1] = midpoint(points[2 * i], points[2 * i + 2])
    return points


def approx_smooth_quadratic_bezier_handles(anchors):
    anchors = np.array(anchors, dtype=float)
    n = len(anchors) - 1
    if n < 1:
        return np.zeros((0, anchors.shape[1]))
    handles = np.zeros((n, anchors.shape[1]))
    for i in range(n):
        if i == 0:
            handles[i] = midpoint(anchors[0], anchors[1])
        elif i == n - 1:
            handles[i] = midpoint(anchors[-2], anchors[-1])
        else:
            h_right = 0.25 * anchors[i - 1] + anchors[i] - 0.25 * anchors[i + 1]
            h_left = -0.25 * anchors[i] + anchors[i + 1] + 0.25 * anchors[i + 2] if i + 2 < len(anchors) else midpoint(anchors[i], anchors[i + 1])
            handles[i] = midpoint(h_right, h_left)
    return handles

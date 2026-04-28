"""Simple mathematical utility functions."""
import numpy as np
from math import factorial


def sigmoid(x):
    """Standard sigmoid function."""
    return 1 / (1 + np.exp(-x))


def choose(n, k):
    """Binomial coefficient - n choose k."""
    return factorial(n) // (factorial(k) * factorial(n - k))


def clip(a, min_val, max_val):
    """Clip a value to be within [min_val, max_val]."""
    if a < min_val:
        return min_val
    if a > max_val:
        return max_val
    return a


def arr_clip(arr, min_val, max_val):
    """Clip array values in place to [min_val, max_val]."""
    arr[arr < min_val] = min_val
    arr[arr > max_val] = max_val

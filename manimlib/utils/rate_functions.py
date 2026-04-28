"""Rate functions for animations."""


def linear(t):
    """Linear interpolation - no easing."""
    return t


def smooth(t):
    """Smooth interpolation using smoothstep (3t² - 2t³).

    Has zero derivative at t=0 and t=1, creating smooth acceleration/deceleration.
    """
    return 3 * t ** 2 - 2 * t ** 3


def rush_into(t):
    """Accelerate into the end - starts slow, ends fast."""
    return 2 * smooth(0.5 * t)


def rush_from(t):
    """Start fast and decelerate toward the end."""
    return 2 * smooth(0.5 * t + 0.5) - 1


def double_smooth(t):
    """Apply smooth twice - first half and second half separately.

    Creates an even smoother transition with a pause-like effect in the middle.
    """
    if t < 0.5:
        return 0.5 * smooth(2 * t)
    else:
        return 0.5 + 0.5 * smooth(2 * t - 1)


def slow_into(t):
    """Decelerate smoothly into the end position."""
    return 1 - (1 - t) ** 2

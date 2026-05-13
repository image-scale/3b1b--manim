import numpy as np
from animlib.bezier import bezier


def linear(t):
    return t


def smooth(t):
    s = 1 - t
    return (t ** 3) * (10 * s * s + 5 * s * t + t * t)


def rush_into(t):
    return 2 * smooth(0.5 * t)


def rush_from(t):
    return 2 * smooth(0.5 * (t + 1)) - 1


def slow_into(t):
    return np.sqrt(1 - (1 - t) ** 2)


def double_smooth(t):
    if t < 0.5:
        return 0.5 * smooth(2 * t)
    return 0.5 * (1 + smooth(2 * t - 1))


def there_and_back(t):
    new_t = 2 * t if t < 0.5 else 2 * (1 - t)
    return smooth(new_t)


def there_and_back_with_pause(t, pause_ratio=1.0 / 3):
    a = 1.0 / (1 - pause_ratio)
    if t < 0.5 - pause_ratio / 2:
        return smooth(a * t)
    elif t < 0.5 + pause_ratio / 2:
        return 1.0
    else:
        return smooth(a - a * t)


def running_start(t, pull_factor=-0.5):
    return bezier([0, 0, pull_factor, pull_factor, 1, 1, 1])(t)


def overshoot(t, pull_factor=1.5):
    return bezier([0, 0, pull_factor, pull_factor, 1, 1])(t)


def not_quite_there(func=None, proportion=0.7):
    if func is None:
        func = smooth
    def result(t):
        return proportion * func(t)
    return result


def wiggle(t, wiggles=2):
    return there_and_back(t) * np.sin(wiggles * np.pi * t)


def squish_rate_func(func, a=0.4, b=0.6):
    def result(t):
        if t < a:
            return func(0)
        elif t > b:
            return func(1)
        else:
            return func((t - a) / (b - a))
    return result


def lingering(t):
    return squish_rate_func(lambda x: x, 0, 0.8)(t)


def exponential_decay(t, half_life=0.1):
    return 1 - np.exp(-t / half_life)

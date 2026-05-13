import numpy as np
from animlib.mobject import Mobject
from animlib.bezier import interpolate


class ValueTracker(Mobject):
    def __init__(self, value=0, **kwargs):
        self._value = np.array([float(value)], dtype=np.float64)
        super().__init__(**kwargs)

    def init_points(self):
        self.set_points([[0, 0, 0]])

    def get_value(self):
        return float(self._value[0])

    def set_value(self, value):
        self._value[0] = float(value)
        return self

    def increment_value(self, d_value):
        self._value[0] += float(d_value)
        return self

    def interpolate(self, mob1, mob2, alpha, path_func=None):
        if isinstance(mob1, ValueTracker) and isinstance(mob2, ValueTracker):
            self._value[0] = interpolate(mob1._value[0], mob2._value[0], alpha)
        return self

    def copy(self):
        result = super().copy()
        result._value = self._value.copy()
        return result

    def become(self, target):
        super().become(target)
        if isinstance(target, ValueTracker):
            self._value = target._value.copy()
        return self


class ExponentialValueTracker(ValueTracker):
    def __init__(self, value=1, **kwargs):
        super().__init__(value=np.log(max(abs(value), 1e-300)), **kwargs)
        self._exp_sign = 1 if value >= 0 else -1

    def get_value(self):
        return self._exp_sign * np.exp(float(self._value[0]))

    def set_value(self, value):
        self._exp_sign = 1 if value >= 0 else -1
        self._value[0] = np.log(max(abs(value), 1e-300))
        return self

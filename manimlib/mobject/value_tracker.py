"""Value tracker mobjects."""
from manimlib.mobject.mobject import Mobject


class ValueTracker(Mobject):
    """A mobject that stores and tracks a numerical value.

    Useful for animations that depend on a changing parameter.
    """

    def __init__(self, value=0.0):
        """Initialize with a value.

        Args:
            value: The initial value to track (default 0.0)
        """
        super().__init__()
        self.value = value

    def get_value(self):
        """Get the current tracked value."""
        return self.value

    def set_value(self, value):
        """Set the tracked value."""
        self.value = value
        return self

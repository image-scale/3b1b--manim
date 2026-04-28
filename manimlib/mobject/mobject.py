"""Base Mobject class."""
import numpy as np


class Mobject:
    """Base class for all mathematical objects."""

    def __init__(self):
        """Initialize mobject with an empty points array."""
        self.points = np.array([])

    def move_to(self, target):
        """Move the mobject to the target position.

        Args:
            target: Target position as array-like [x, y, z]
        """
        # Minimal implementation - just stores the target
        # In full manim, this would shift all points
        pass

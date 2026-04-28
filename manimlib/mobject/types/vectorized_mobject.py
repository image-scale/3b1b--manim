"""Vectorized mobject types."""
import numpy as np

from manimlib.mobject.mobject import Mobject


class VMobject(Mobject):
    """Vectorized mobject - drawn using bezier curves."""

    def __init__(self):
        """Initialize VMobject."""
        super().__init__()

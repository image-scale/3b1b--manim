"""Geometric mobjects."""
from manimlib.mobject.types.vectorized_mobject import VMobject


class Line(VMobject):
    """A straight line between two points."""

    def __init__(self, start, end):
        """Create a line from start to end point."""
        super().__init__()
        self.start = start
        self.end = end


class Circle(VMobject):
    """A circle."""

    def __init__(self, radius=1.0):
        """Create a circle with given radius."""
        super().__init__()
        self.radius = radius


class Square(VMobject):
    """A square."""

    def __init__(self, side_length=2.0):
        """Create a square with given side length."""
        super().__init__()
        self.side_length = side_length


class Dot(VMobject):
    """A small circle representing a point."""

    def __init__(self, point=None):
        """Create a dot at the given point."""
        super().__init__()
        self.point = point


class Arrow(Line):
    """An arrow from start to end."""

    def __init__(self, start, end):
        """Create an arrow from start to end point."""
        super().__init__(start, end)

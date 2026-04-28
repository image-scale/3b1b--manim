"""
Smoke tests for manimlib mobject creation and basic operations.
"""
import numpy as np
import pytest

from manimlib.constants import UP, DOWN, LEFT, RIGHT, ORIGIN


def test_mobject_creation():
    from manimlib.mobject.mobject import Mobject
    m = Mobject()
    assert m is not None


def test_vmobject_creation():
    from manimlib.mobject.types.vectorized_mobject import VMobject
    vm = VMobject()
    assert vm is not None


def test_line_creation():
    from manimlib.mobject.geometry import Line
    line = Line(LEFT, RIGHT)
    assert line is not None


def test_circle_creation():
    from manimlib.mobject.geometry import Circle
    c = Circle()
    assert c is not None


def test_square_creation():
    from manimlib.mobject.geometry import Square
    s = Square()
    assert s is not None


def test_dot_creation():
    from manimlib.mobject.geometry import Dot
    d = Dot()
    assert d is not None


def test_arrow_creation():
    from manimlib.mobject.geometry import Arrow
    a = Arrow(LEFT, RIGHT)
    assert a is not None


def test_value_tracker_default():
    from manimlib.mobject.value_tracker import ValueTracker
    vt = ValueTracker()
    assert vt.get_value() == pytest.approx(0.0)


def test_value_tracker_set():
    from manimlib.mobject.value_tracker import ValueTracker
    vt = ValueTracker(5.0)
    assert vt.get_value() == pytest.approx(5.0)


def test_mobject_move_to():
    from manimlib.mobject.mobject import Mobject
    m = Mobject()
    target = np.array([1.0, 2.0, 0.0])
    m.move_to(target)
    # Just verify no exception is raised


def test_constants_directions():
    assert UP[1] > 0
    assert DOWN[1] < 0
    assert LEFT[0] < 0
    assert RIGHT[0] > 0
    np.testing.assert_array_equal(ORIGIN, [0.0, 0.0, 0.0])

import numpy as np
import pytest
from animlib import (
    ORIGIN, UP, DOWN, LEFT, RIGHT, OUT, UL, UR, DL, DR,
    PI, TAU, DEG,
    RED, BLUE, GREEN, WHITE, BLACK, YELLOW,
    FRAME_X_RADIUS, FRAME_Y_RADIUS,
    DEFAULT_MOBJECT_TO_EDGE_BUFF, DEFAULT_MOBJECT_TO_MOBJECT_BUFF,
    SMALL_BUFF, MED_SMALL_BUFF,
)


class TestDirectionConstants:
    def test_up_is_unit_y(self):
        assert np.allclose(UP, [0, 1, 0])

    def test_down_is_negative_y(self):
        assert np.allclose(DOWN, [0, -1, 0])

    def test_right_is_unit_x(self):
        assert np.allclose(RIGHT, [1, 0, 0])

    def test_left_is_negative_x(self):
        assert np.allclose(LEFT, [-1, 0, 0])

    def test_origin_is_zero(self):
        assert np.allclose(ORIGIN, [0, 0, 0])

    def test_out_is_positive_z(self):
        assert np.allclose(OUT, [0, 0, 1])

    def test_diagonal_directions(self):
        assert np.allclose(UR, [1, 1, 0])
        assert np.allclose(UL, [-1, 1, 0])
        assert np.allclose(DR, [1, -1, 0])
        assert np.allclose(DL, [-1, -1, 0])

    def test_constants_are_3d(self):
        for v in [UP, DOWN, LEFT, RIGHT, ORIGIN, OUT]:
            assert len(v) == 3

    def test_pi_and_tau(self):
        assert abs(PI - 3.14159265) < 1e-5
        assert abs(TAU - 2 * PI) < 1e-10

    def test_colors_are_hex_strings(self):
        for c in [RED, BLUE, GREEN, WHITE, BLACK, YELLOW]:
            assert isinstance(c, str)
            assert c.startswith("#")


class TestMobjectCreation:
    def test_empty_mobject(self):
        from animlib import Mobject
        m = Mobject()
        assert m.get_num_points() == 0
        assert not m.has_points()

    def test_set_points(self):
        from animlib import Mobject
        m = Mobject()
        pts = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
        m.set_points(pts)
        assert m.get_num_points() == 3
        assert m.has_points()
        assert np.allclose(m.get_points()[0], [1, 0, 0])

    def test_get_start_end(self):
        from animlib import Mobject
        m = Mobject()
        m.set_points([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        assert np.allclose(m.get_start(), [1, 2, 3])
        assert np.allclose(m.get_end(), [7, 8, 9])

    def test_append_points(self):
        from animlib import Mobject
        m = Mobject()
        m.set_points([[0, 0, 0]])
        m.append_points([[1, 1, 1], [2, 2, 2]])
        assert m.get_num_points() == 3

    def test_clear_points(self):
        from animlib import Mobject
        m = Mobject()
        m.set_points([[1, 2, 3]])
        m.clear_points()
        assert m.get_num_points() == 0


class TestMobjectPositioning:
    def test_shift(self):
        from animlib import Mobject
        m = Mobject()
        m.set_points([[0, 0, 0], [1, 0, 0]])
        m.shift(UP)
        assert np.allclose(m.get_points()[0], [0, 1, 0])
        assert np.allclose(m.get_points()[1], [1, 1, 0])

    def test_shift_returns_self(self):
        from animlib import Mobject
        m = Mobject()
        m.set_points([[0, 0, 0]])
        result = m.shift(RIGHT)
        assert result is m

    def test_scale_uniform(self):
        from animlib import Mobject
        m = Mobject()
        m.set_points([[1, 0, 0], [-1, 0, 0]])
        m.scale(2)
        assert np.allclose(m.get_points()[0], [2, 0, 0])
        assert np.allclose(m.get_points()[1], [-2, 0, 0])

    def test_scale_about_point(self):
        from animlib import Mobject
        m = Mobject()
        m.set_points([[2, 0, 0]])
        m.scale(2, about_point=np.array([0, 0, 0]))
        assert np.allclose(m.get_points()[0], [4, 0, 0])

    def test_rotate_90_degrees(self):
        from animlib import Mobject
        m = Mobject()
        m.set_points([[1, 0, 0]])
        m.rotate(PI / 2, about_point=ORIGIN)
        assert np.allclose(m.get_points()[0], [0, 1, 0], atol=1e-10)

    def test_rotate_about_axis(self):
        from animlib import Mobject
        m = Mobject()
        m.set_points([[1, 0, 0]])
        m.rotate(PI / 2, axis=UP, about_point=ORIGIN)
        assert np.allclose(m.get_points()[0], [0, 0, -1], atol=1e-10)

    def test_move_to_point(self):
        from animlib import Mobject
        m = Mobject()
        m.set_points([[-1, -1, 0], [1, 1, 0]])
        m.move_to([3, 4, 0])
        center = m.get_center()
        assert np.allclose(center, [3, 4, 0], atol=1e-10)

    def test_move_to_mobject(self):
        from animlib import Mobject
        m1 = Mobject()
        m1.set_points([[-1, -1, 0], [1, 1, 0]])
        m2 = Mobject()
        m2.set_points([[5, 5, 0], [7, 7, 0]])
        m1.move_to(m2)
        assert np.allclose(m1.get_center(), m2.get_center(), atol=1e-10)

    def test_next_to(self):
        from animlib import Mobject
        m1 = Mobject()
        m1.set_points([[-1, -1, 0], [1, 1, 0]])
        m2 = Mobject()
        m2.set_points([[-0.5, -0.5, 0], [0.5, 0.5, 0]])
        m2.next_to(m1, RIGHT, buff=0.5)
        # m2 should be to the right of m1
        assert m2.get_left_edge()[0] > m1.get_right_edge()[0] - 0.01

    def test_to_edge(self):
        from animlib import Mobject
        m = Mobject()
        m.set_points([[-0.5, -0.5, 0], [0.5, 0.5, 0]])
        m.to_edge(UP)
        top = m.get_top()
        expected = FRAME_Y_RADIUS - DEFAULT_MOBJECT_TO_EDGE_BUFF
        assert abs(top[1] - expected) < 0.01

    def test_to_edge_left(self):
        from animlib import Mobject
        m = Mobject()
        m.set_points([[-0.5, -0.5, 0], [0.5, 0.5, 0]])
        m.to_edge(LEFT)
        left = m.get_left_edge()
        expected = -FRAME_X_RADIUS + DEFAULT_MOBJECT_TO_EDGE_BUFF
        assert abs(left[0] - expected) < 0.01

    def test_center(self):
        from animlib import Mobject
        m = Mobject()
        m.set_points([[5, 3, 0], [7, 5, 0]])
        m.center()
        assert np.allclose(m.get_center(), ORIGIN, atol=1e-10)

    def test_flip(self):
        from animlib import Mobject
        m = Mobject()
        m.set_points([[1, 0, 0], [2, 0, 0]])
        center = m.get_center().copy()
        m.flip(axis=UP)
        assert np.allclose(m.get_center(), center, atol=1e-10)

    def test_set_x(self):
        from animlib import Mobject
        m = Mobject()
        m.set_points([[0, 0, 0], [2, 0, 0]])
        m.set_x(5)
        assert abs(m.get_center()[0] - 5) < 1e-10

    def test_set_y(self):
        from animlib import Mobject
        m = Mobject()
        m.set_points([[0, 0, 0], [0, 2, 0]])
        m.set_y(3)
        assert abs(m.get_center()[1] - 3) < 1e-10


class TestBoundingBox:
    def test_bounding_box_center(self):
        from animlib import Mobject
        m = Mobject()
        m.set_points([[-2, -1, 0], [2, 1, 0]])
        assert np.allclose(m.get_center(), [0, 0, 0])

    def test_bounding_box_dimensions(self):
        from animlib import Mobject
        m = Mobject()
        m.set_points([[-3, -1, 0], [3, 1, 0]])
        assert abs(m.get_width() - 6) < 1e-10
        assert abs(m.get_height() - 2) < 1e-10

    def test_set_width(self):
        from animlib import Mobject
        m = Mobject()
        m.set_points([[-1, -1, 0], [1, 1, 0]])
        m.set_width(4)
        assert abs(m.get_width() - 4) < 0.01

    def test_set_height(self):
        from animlib import Mobject
        m = Mobject()
        m.set_points([[-1, -1, 0], [1, 1, 0]])
        m.set_height(6)
        assert abs(m.get_height() - 6) < 0.01

    def test_get_top_bottom_left_right(self):
        from animlib import Mobject
        m = Mobject()
        m.set_points([[-2, -3, 0], [4, 5, 0]])
        assert abs(m.get_top()[1] - 5) < 1e-10
        assert abs(m.get_bottom()[1] - (-3)) < 1e-10
        assert abs(m.get_right_edge()[0] - 4) < 1e-10
        assert abs(m.get_left_edge()[0] - (-2)) < 1e-10


class TestSubmobjects:
    def test_add_submobjects(self):
        from animlib import Mobject, Group
        parent = Group()
        child1 = Mobject()
        child2 = Mobject()
        parent.add(child1, child2)
        assert len(parent) == 2
        assert child1 in parent.submobjects
        assert child2 in parent.submobjects

    def test_cannot_add_self(self):
        from animlib import Mobject
        m = Mobject()
        with pytest.raises(ValueError):
            m.add(m)

    def test_remove_submobjects(self):
        from animlib import Group, Mobject
        parent = Group()
        child = Mobject()
        parent.add(child)
        parent.remove(child)
        assert len(parent) == 0

    def test_get_family(self):
        from animlib import Group, Mobject
        parent = Group()
        child1 = Mobject()
        child2 = Mobject()
        parent.add(child1, child2)
        family = parent.get_family()
        assert parent in family
        assert child1 in family
        assert child2 in family

    def test_group_bounding_box(self):
        from animlib import Group, Mobject
        m1 = Mobject()
        m1.set_points([[-1, 0, 0]])
        m2 = Mobject()
        m2.set_points([[1, 0, 0]])
        g = Group(m1, m2)
        assert abs(g.get_width() - 2) < 1e-10

    def test_group_shift_applies_to_children(self):
        from animlib import Group, Mobject
        m1 = Mobject()
        m1.set_points([[0, 0, 0]])
        m2 = Mobject()
        m2.set_points([[1, 0, 0]])
        g = Group(m1, m2)
        g.shift(UP)
        assert np.allclose(m1.get_points()[0], [0, 1, 0])
        assert np.allclose(m2.get_points()[0], [1, 1, 0])

    def test_indexing(self):
        from animlib import Group, Mobject
        m1 = Mobject()
        m2 = Mobject()
        g = Group(m1, m2)
        assert g[0] is m1
        assert g[1] is m2

    def test_iteration(self):
        from animlib import Group, Mobject
        children = [Mobject() for _ in range(3)]
        g = Group(*children)
        collected = list(g)
        assert collected == children

    def test_clear(self):
        from animlib import Group, Mobject
        g = Group(Mobject(), Mobject())
        g.clear()
        assert len(g) == 0


class TestCopyAndState:
    def test_copy_is_independent(self):
        from animlib import Mobject
        m = Mobject()
        m.set_points([[1, 2, 3]])
        c = m.copy()
        c.shift(RIGHT * 10)
        assert not np.allclose(m.get_points(), c.get_points())

    def test_copy_preserves_data(self):
        from animlib import Mobject
        m = Mobject()
        m.set_points([[1, 2, 3], [4, 5, 6]])
        c = m.copy()
        assert np.allclose(m.get_points(), c.get_points())

    def test_save_and_restore(self):
        from animlib import Mobject
        m = Mobject()
        m.set_points([[0, 0, 0]])
        m.save_state()
        m.shift(RIGHT * 5)
        assert not np.allclose(m.get_points()[0], [0, 0, 0])
        m.restore()
        assert np.allclose(m.get_points()[0], [0, 0, 0])

    def test_generate_target(self):
        from animlib import Mobject
        m = Mobject()
        m.set_points([[0, 0, 0]])
        target = m.generate_target()
        assert target is not m
        assert m.target is target
        assert np.allclose(target.get_points(), m.get_points())

    def test_become(self):
        from animlib import Mobject
        m1 = Mobject()
        m1.set_points([[0, 0, 0]])
        m2 = Mobject()
        m2.set_points([[5, 5, 5], [6, 6, 6]])
        m1.become(m2)
        assert np.allclose(m1.get_points(), m2.get_points())


class TestPoint:
    def test_point_creation(self):
        from animlib import Point
        p = Point([3, 4, 0])
        assert np.allclose(p.get_location(), [3, 4, 0])

    def test_point_default_origin(self):
        from animlib import Point
        p = Point()
        assert np.allclose(p.get_location(), ORIGIN)


class TestCircle:
    def test_circle_default(self):
        from animlib import Circle
        c = Circle()
        assert c.get_num_points() > 0
        assert abs(c.get_width() - 2.0) < 0.1

    def test_circle_radius(self):
        from animlib import Circle
        c = Circle(radius=3.0)
        assert abs(c.get_width() - 6.0) < 0.2

    def test_circle_centered_at_origin(self):
        from animlib import Circle
        c = Circle()
        assert np.allclose(c.get_center(), ORIGIN, atol=0.1)

    def test_circle_is_closed(self):
        from animlib import Circle
        c = Circle()
        start = c.get_start()
        end = c.get_end()
        assert np.allclose(start, end, atol=0.01)


class TestDot:
    def test_dot_at_origin(self):
        from animlib import Dot
        d = Dot()
        assert np.allclose(d.get_center(), ORIGIN, atol=0.01)

    def test_dot_at_point(self):
        from animlib import Dot
        d = Dot([3, 4, 0])
        assert np.allclose(d.get_center(), [3, 4, 0], atol=0.1)

    def test_dot_is_small(self):
        from animlib import Dot
        d = Dot()
        assert d.get_width() < 0.5


class TestArc:
    def test_quarter_arc(self):
        from animlib import Arc
        a = Arc(angle=PI / 2)
        assert a.get_num_points() > 0
        start = a.get_start()
        assert abs(start[0] - 1.0) < 0.1  # starts on positive x-axis

    def test_half_arc(self):
        from animlib import Arc
        a = Arc(angle=PI)
        end = a.get_end()
        assert abs(end[0] - (-1.0)) < 0.1  # ends on negative x-axis

    def test_arc_with_radius(self):
        from animlib import Arc
        a = Arc(angle=PI, radius=2.0)
        assert abs(a.get_width() - 4.0) < 0.3


class TestLine:
    def test_line_default(self):
        from animlib import Line
        l = Line()
        start = l.get_start()
        end = l.get_end()
        assert start[0] < end[0]

    def test_line_between_points(self):
        from animlib import Line
        l = Line([0, 0, 0], [3, 4, 0])
        length = l.get_length()
        assert abs(length - 5.0) < 0.1

    def test_line_angle(self):
        from animlib import Line
        l = Line([0, 0, 0], [1, 1, 0])
        assert abs(l.get_angle() - PI / 4) < 0.01

    def test_line_vector(self):
        from animlib import Line
        l = Line([1, 1, 0], [4, 5, 0])
        vec = l.get_vector()
        assert np.allclose(vec, [3, 4, 0], atol=0.1)

    def test_line_unit_vector(self):
        from animlib import Line
        l = Line([0, 0, 0], [3, 4, 0])
        uv = l.get_unit_vector()
        assert abs(np.linalg.norm(uv) - 1.0) < 0.01


class TestArrow:
    def test_arrow_creation(self):
        from animlib import Arrow
        a = Arrow([0, 0, 0], [3, 0, 0])
        assert a.has_points()

    def test_arrow_has_tip(self):
        from animlib import Arrow
        a = Arrow([0, 0, 0], [3, 0, 0])
        assert hasattr(a, 'tip')
        assert a.tip is not None


class TestRectangle:
    def test_rectangle_dimensions(self):
        from animlib import Rectangle
        r = Rectangle(width=6, height=3)
        assert abs(r.get_width() - 6) < 0.1
        assert abs(r.get_height() - 3) < 0.1

    def test_rectangle_centered(self):
        from animlib import Rectangle
        r = Rectangle()
        assert np.allclose(r.get_center(), ORIGIN, atol=0.01)

    def test_rectangle_is_closed(self):
        from animlib import Rectangle
        r = Rectangle()
        assert r.is_closed()


class TestSquare:
    def test_square_equal_sides(self):
        from animlib import Square
        s = Square(side_length=3)
        assert abs(s.get_width() - 3) < 0.1
        assert abs(s.get_height() - 3) < 0.1


class TestPolygon:
    def test_triangle_from_polygon(self):
        from animlib import Polygon
        p = Polygon([0, 0, 0], [1, 0, 0], [0.5, 1, 0])
        assert p.has_points()
        assert p.is_closed()

    def test_polygon_vertices(self):
        from animlib import Polygon
        verts = [[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]]
        p = Polygon(*verts)
        got = p.get_vertices()
        for v, expected in zip(got, verts):
            assert np.allclose(v, expected, atol=1e-10)


class TestRegularPolygon:
    def test_hexagon(self):
        from animlib import RegularPolygon
        h = RegularPolygon(n=6)
        assert h.has_points()
        assert h.is_closed()

    def test_hexagon_vertex_count(self):
        from animlib import RegularPolygon
        h = RegularPolygon(n=6)
        verts = h.get_vertices()
        assert len(verts) == 6

    def test_triangle(self):
        from animlib import Triangle
        t = Triangle()
        assert t.has_points()
        assert t.is_closed()


class TestUpdaters:
    def test_add_updater(self):
        from animlib import Mobject
        m = Mobject()
        m.set_points([[0, 0, 0]])
        m.add_updater(lambda mob: mob.shift(RIGHT * 0.1), call_func=False)
        assert m.has_updaters()

    def test_remove_updater(self):
        from animlib import Mobject
        m = Mobject()
        func = lambda mob: None
        m.add_updater(func, call_func=False)
        m.remove_updater(func)
        assert not m.has_updaters()

    def test_update_calls_updaters(self):
        from animlib import Mobject
        m = Mobject()
        m.set_points([[0, 0, 0]])
        call_count = [0]
        def updater(mob):
            call_count[0] += 1
        m.add_updater(updater, call_func=False)
        m.update()
        assert call_count[0] == 1

    def test_clear_updaters(self):
        from animlib import Mobject
        m = Mobject()
        m.add_updater(lambda mob: None, call_func=False)
        m.clear_updaters()
        assert not m.has_updaters()

    def test_suspend_updating(self):
        from animlib import Mobject
        m = Mobject()
        m.set_points([[0, 0, 0]])
        call_count = [0]
        def updater(mob):
            call_count[0] += 1
        m.add_updater(updater, call_func=False)
        m.suspend_updating()
        m.update()
        assert call_count[0] == 0
        m.resume_updating()
        m.update()
        assert call_count[0] == 1

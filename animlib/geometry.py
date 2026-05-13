import numpy as np
from animlib.vmobject import VMobject, VGroup
from animlib.mobject import Mobject
from animlib.constants import (
    ORIGIN, UP, DOWN, LEFT, RIGHT, OUT, UL, UR, DL, DR,
    PI, TAU, DEG,
    DEFAULT_STROKE_WIDTH, RED, WHITE, BLUE, YELLOW,
    SMALL_BUFF, MED_SMALL_BUFF, MED_LARGE_BUFF,
    DEFAULT_FILL_COLOR,
)
from animlib.math_utils import (
    normalize, get_norm, rotate_vector, angle_of_vector, rotation_matrix,
    compass_directions,
)
from animlib.bezier import quadratic_bezier_points_for_arc, interpolate


class Arc(VMobject):
    def __init__(
        self,
        start_angle=0,
        angle=TAU / 4,
        radius=1.0,
        n_components=None,
        arc_center=None,
        **kwargs,
    ):
        self.start_angle = start_angle
        self.arc_angle = angle
        self.arc_radius = radius
        self.arc_center_point = arc_center if arc_center is not None else ORIGIN.copy()
        if n_components is None:
            n_components = max(1, int(np.ceil(abs(angle) / (PI / 2)))) if abs(angle) > 1e-10 else 1
        self.n_components = n_components
        super().__init__(**kwargs)

    def init_points(self):
        arc_pts = quadratic_bezier_points_for_arc(
            self.arc_angle, self.n_components
        )
        arc_pts *= self.arc_radius
        if abs(self.start_angle) > 1e-10:
            cos_a = np.cos(self.start_angle)
            sin_a = np.sin(self.start_angle)
            rotated = arc_pts.copy()
            rotated[:, 0] = arc_pts[:, 0] * cos_a - arc_pts[:, 1] * sin_a
            rotated[:, 1] = arc_pts[:, 0] * sin_a + arc_pts[:, 1] * cos_a
            arc_pts = rotated
        arc_pts += self.arc_center_point
        self.set_points(arc_pts)

    def get_arc_center(self):
        return self.arc_center_point.copy()

    def get_start_angle(self):
        return self.start_angle

    def get_radius(self):
        return self.arc_radius

    def point_at_angle(self, angle):
        prop = (angle - self.start_angle) / self.arc_angle
        prop = max(0, min(1, prop))
        return self.point_from_proportion(prop)


class Circle(Arc):
    def __init__(self, radius=1.0, start_angle=0, stroke_color=None, **kwargs):
        if stroke_color is None:
            stroke_color = RED
        super().__init__(
            start_angle=start_angle,
            angle=TAU,
            radius=radius,
            stroke_color=stroke_color,
            **kwargs,
        )

    def get_radius(self):
        return self.get_width() / 2.0

    def point_at_angle(self, angle):
        prop = angle / TAU
        prop = prop % 1.0
        return self.point_from_proportion(prop)

    def surround(self, mobject, dim_to_match=0, stretch=False, buff=SMALL_BUFF):
        self.replace(mobject, dim_to_match=dim_to_match, stretch=stretch)
        w = self.get_width()
        h = self.get_height()
        max_dim = max(w, h) + 2 * buff
        self.set_width(max_dim)
        self.set_height(max_dim)
        self.move_to(mobject)
        return self


class Dot(Circle):
    def __init__(
        self,
        point=None,
        radius=0.08,
        fill_opacity=1.0,
        stroke_width=0,
        color=None,
        **kwargs,
    ):
        if color is None:
            color = WHITE
        super().__init__(
            radius=radius,
            fill_opacity=fill_opacity,
            fill_color=color,
            stroke_width=stroke_width,
            color=color,
            **kwargs,
        )
        if point is not None:
            self.move_to(point)


class SmallDot(Dot):
    def __init__(self, point=None, radius=0.04, **kwargs):
        super().__init__(point=point, radius=radius, **kwargs)


class Ellipse(Circle):
    def __init__(self, width=2.0, height=1.0, **kwargs):
        super().__init__(**kwargs)
        self.set_width(width, stretch=True)
        self.set_height(height, stretch=True)


class ArcBetweenPoints(Arc):
    def __init__(self, start, end, angle=TAU / 4, **kwargs):
        start = np.array(start, dtype=float)
        end = np.array(end, dtype=float)
        super().__init__(angle=angle, **kwargs)
        self.put_start_and_end_on(start, end)


class Line(VMobject):
    def __init__(self, start=None, end=None, buff=0.0, path_arc=0.0, **kwargs):
        if start is None:
            start = LEFT
        if end is None:
            end = RIGHT
        self.buff = buff
        self.path_arc = path_arc
        if isinstance(start, Mobject):
            start = start.get_center()
        if isinstance(end, Mobject):
            end = end.get_center()
        self._line_start = np.array(start, dtype=float)
        self._line_end = np.array(end, dtype=float)
        super().__init__(**kwargs)

    def init_points(self):
        start = self._line_start.copy()
        end = self._line_end.copy()
        if self.buff > 0:
            vec = end - start
            length = get_norm(vec)
            if length > 2 * self.buff:
                direction = vec / length
                start = start + direction * self.buff
                end = end - direction * self.buff
        if abs(self.path_arc) > 1e-6:
            self._set_arc_path(start, end)
        else:
            self.start_new_path(start)
            self.add_line_to(end)

    def _set_arc_path(self, start, end):
        n_components = max(1, int(np.ceil(abs(self.path_arc) / (PI / 2))))
        arc_pts = quadratic_bezier_points_for_arc(self.path_arc, n_components)
        arc_start = arc_pts[0]
        arc_end = arc_pts[-1]
        vec = end - start
        arc_vec = arc_end - arc_start
        arc_len = get_norm(arc_vec)
        target_len = get_norm(vec)
        if arc_len < 1e-10:
            self.start_new_path(start)
            self.add_line_to(end)
            return
        scale = target_len / arc_len
        arc_angle = np.arctan2(arc_vec[1], arc_vec[0])
        target_angle = np.arctan2(vec[1], vec[0])
        rot = target_angle - arc_angle
        cos_r, sin_r = np.cos(rot), np.sin(rot)
        transformed = arc_pts - arc_start
        x_new = transformed[:, 0] * cos_r - transformed[:, 1] * sin_r
        y_new = transformed[:, 0] * sin_r + transformed[:, 1] * cos_r
        transformed[:, 0] = x_new
        transformed[:, 1] = y_new
        transformed *= scale
        transformed += start
        self.set_points(transformed)

    def get_vector(self):
        return self.get_end() - self.get_start()

    def get_unit_vector(self):
        return normalize(self.get_vector())

    def get_angle(self):
        vec = self.get_vector()
        return angle_of_vector(vec)

    def get_length(self):
        return get_norm(self.get_vector())

    def get_slope(self):
        vec = self.get_vector()
        if abs(vec[0]) < 1e-10:
            return float('inf')
        return vec[1] / vec[0]

    def set_angle(self, angle, about_point=None):
        if about_point is None:
            about_point = self.get_start()
        current_angle = self.get_angle()
        self.rotate(angle - current_angle, about_point=about_point)
        return self

    def set_length(self, length, about_point=None):
        current = self.get_length()
        if current < 1e-10:
            return self
        self.scale(length / current, about_point=about_point or self.get_start())
        return self

    def set_start_and_end(self, start, end):
        self._line_start = np.array(start, dtype=float)
        self._line_end = np.array(end, dtype=float)
        self.clear_points()
        self.init_points()
        return self

    def put_start_and_end_on(self, start, end):
        return self.set_start_and_end(start, end)


class DashedLine(Line):
    def __init__(self, start=None, end=None, num_dashes=15, dash_ratio=0.5, **kwargs):
        self.num_dashes = num_dashes
        self.dash_ratio = dash_ratio
        super().__init__(start=start, end=end, **kwargs)
        self._create_dashes()

    def _create_dashes(self):
        if self.get_num_curves() == 0:
            return
        full = 1.0 / self.num_dashes if self.num_dashes > 0 else 1.0
        dash_len = full * self.dash_ratio
        dashes = []
        for i in range(self.num_dashes):
            a = i * full
            b = a + dash_len
            dash = VMobject()
            dash.pointwise_become_partial(self, a, min(b, 1.0))
            dash.match_style(self)
            if dash.has_points():
                dashes.append(dash)
        self.clear()
        for d in dashes:
            self.add(d)


class Arrow(Line):
    def __init__(
        self,
        start=None,
        end=None,
        buff=MED_SMALL_BUFF,
        tip_length=0.25,
        tip_width=0.25,
        fill_opacity=1.0,
        stroke_width=0,
        color=None,
        **kwargs,
    ):
        self.tip_length = tip_length
        self.tip_width = tip_width
        if color is None:
            color = WHITE
        super().__init__(
            start=start,
            end=end,
            buff=buff,
            color=color,
            fill_opacity=fill_opacity,
            stroke_width=stroke_width if stroke_width else DEFAULT_STROKE_WIDTH,
            **kwargs,
        )
        self._add_tip()

    def _add_tip(self):
        tip = ArrowTip(
            length=self.tip_length,
            width=self.tip_width,
        )
        tip.match_style(self)
        end = self.get_end()
        vec = self.get_unit_vector()
        angle = angle_of_vector(vec)
        tip.rotate(angle - PI / 2)
        tip.move_to(end, aligned_edge=UP)
        tip.shift(vec * 0.01)
        self.tip = tip
        self.add(tip)

    def get_tip(self):
        return self.tip


class Vector(Arrow):
    def __init__(self, direction=RIGHT, **kwargs):
        direction = np.array(direction, dtype=float)
        super().__init__(start=ORIGIN, end=direction, buff=0, **kwargs)


class ArrowTip(VMobject):
    def __init__(self, length=0.25, width=0.25, **kwargs):
        self.tip_length = length
        self.tip_width = width
        super().__init__(
            fill_opacity=1.0,
            stroke_width=0,
            **kwargs,
        )

    def init_points(self):
        top = np.array([0, self.tip_length / 2, 0])
        bl = np.array([-self.tip_width / 2, -self.tip_length / 2, 0])
        br = np.array([self.tip_width / 2, -self.tip_length / 2, 0])
        self.start_new_path(top)
        self.add_line_to(bl)
        self.add_line_to(br)
        self.add_line_to(top)


class Polygon(VMobject):
    def __init__(self, *vertices, **kwargs):
        if len(vertices) == 0:
            self._vertices = np.zeros((0, 3))
        else:
            self._vertices = np.array([
                np.array(v, dtype=float) if len(np.array(v)) == 3
                else np.array([*np.array(v, dtype=float), 0.0])
                for v in vertices
            ], dtype=np.float64)
        super().__init__(**kwargs)

    def init_points(self):
        if len(self._vertices) < 2:
            return
        verts = list(self._vertices)
        verts.append(verts[0])
        self.set_points_as_corners(verts)

    def get_vertices(self):
        return self._vertices.copy()


class RegularPolygon(Polygon):
    def __init__(self, n=6, radius=1.0, start_angle=None, **kwargs):
        if start_angle is None:
            start_angle = PI / 2
        angles = np.linspace(start_angle, start_angle + TAU, n, endpoint=False)
        vertices = np.array([
            [radius * np.cos(a), radius * np.sin(a), 0.0]
            for a in angles
        ])
        super().__init__(*vertices, **kwargs)


class Triangle(RegularPolygon):
    def __init__(self, **kwargs):
        super().__init__(n=3, **kwargs)


class Rectangle(VMobject):
    def __init__(self, width=4.0, height=2.0, **kwargs):
        self.rect_width = width
        self.rect_height = height
        super().__init__(**kwargs)

    def init_points(self):
        w = self.rect_width / 2
        h = self.rect_height / 2
        corners = [
            np.array([w, h, 0.0]),
            np.array([-w, h, 0.0]),
            np.array([-w, -h, 0.0]),
            np.array([w, -h, 0.0]),
            np.array([w, h, 0.0]),
        ]
        self.set_points_as_corners(corners)

    def get_vertices(self):
        return self.get_anchors()[:4]

    def surround(self, mobject, buff=SMALL_BUFF, stretch=False):
        w = mobject.get_width() + 2 * buff
        h = mobject.get_height() + 2 * buff
        self.rect_width = w
        self.rect_height = h
        self.clear_points()
        self.init_points()
        self.move_to(mobject)
        return self


class Square(Rectangle):
    def __init__(self, side_length=2.0, **kwargs):
        super().__init__(width=side_length, height=side_length, **kwargs)


class RoundedRectangle(Rectangle):
    def __init__(self, corner_radius=0.5, **kwargs):
        self.corner_radius = corner_radius
        super().__init__(**kwargs)
        self.round_corners(self.corner_radius)


class Polyline(VMobject):
    def __init__(self, *vertices, **kwargs):
        self._polyline_vertices = np.array([
            np.array(v, dtype=float) if len(np.array(v)) == 3
            else np.array([*np.array(v, dtype=float), 0.0])
            for v in vertices
        ], dtype=np.float64) if len(vertices) > 0 else np.zeros((0, 3))
        super().__init__(**kwargs)

    def init_points(self):
        if len(self._polyline_vertices) < 2:
            return
        self.set_points_as_corners(self._polyline_vertices)


class Elbow(VMobject):
    def __init__(self, width=0.2, angle=0, **kwargs):
        self.elbow_width = width
        self.elbow_angle = angle
        super().__init__(**kwargs)

    def init_points(self):
        w = self.elbow_width
        pts = [
            np.array([0, w, 0.0]),
            np.array([0, 0, 0.0]),
            np.array([w, 0, 0.0]),
        ]
        self.set_points_as_corners(pts)
        if abs(self.elbow_angle) > 1e-10:
            self.rotate(self.elbow_angle, about_point=ORIGIN)


class Annulus(VMobject):
    def __init__(self, inner_radius=1.0, outer_radius=2.0, **kwargs):
        self.inner_radius = inner_radius
        self.outer_radius = outer_radius
        super().__init__(**kwargs)

    def init_points(self):
        outer = Circle(radius=self.outer_radius)
        inner = Circle(radius=self.inner_radius)
        inner.flip()
        self.append_points(outer.get_points())
        self.start_new_path(inner.get_start())
        self.append_points(inner.get_points()[1:])

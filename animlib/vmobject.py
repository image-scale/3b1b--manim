import numpy as np
from animlib.mobject import Mobject, Group
from animlib.constants import (
    ORIGIN, OUT, DEFAULT_STROKE_WIDTH, DEFAULT_FILL_COLOR, DEFAULT_STROKE_COLOR,
    WHITE, PI,
)
from animlib.math_utils import get_norm, normalize, cross, get_unit_normal
from animlib.bezier import (
    interpolate, quadratic_bezier_points_for_arc,
    approx_smooth_quadratic_bezier_handles, partial_bezier_points,
)


class VMobject(Mobject):
    def __init__(
        self,
        fill_color=None,
        fill_opacity=0.0,
        stroke_color=None,
        stroke_opacity=1.0,
        stroke_width=DEFAULT_STROKE_WIDTH,
        stroke_behind=False,
        color=None,
        **kwargs,
    ):
        self._fill_color = fill_color
        self._fill_opacity = fill_opacity
        self._stroke_color = stroke_color
        self._stroke_opacity = stroke_opacity
        self._stroke_width = stroke_width
        self._stroke_behind = stroke_behind
        if color is not None:
            if fill_color is None:
                self._fill_color = color
            if stroke_color is None:
                self._stroke_color = color
        if self._fill_color is None:
            self._fill_color = DEFAULT_FILL_COLOR
        if self._stroke_color is None:
            self._stroke_color = DEFAULT_STROKE_COLOR
        super().__init__(
            color=self._stroke_color if self._stroke_opacity > 0 else self._fill_color,
            **kwargs,
        )

    # --- Style ---

    def set_fill(self, color=None, opacity=None, recurse=True):
        if color is not None:
            self._fill_color = color
        if opacity is not None:
            self._fill_opacity = opacity
        if recurse:
            for sub in self.submobjects:
                if isinstance(sub, VMobject):
                    sub.set_fill(color=color, opacity=opacity, recurse=True)
        return self

    def set_stroke(self, color=None, width=None, opacity=None, behind=None, recurse=True):
        if color is not None:
            self._stroke_color = color
        if width is not None:
            self._stroke_width = width
        if opacity is not None:
            self._stroke_opacity = opacity
        if behind is not None:
            self._stroke_behind = behind
        if recurse:
            for sub in self.submobjects:
                if isinstance(sub, VMobject):
                    sub.set_stroke(color=color, width=width, opacity=opacity, behind=behind, recurse=True)
        return self

    def set_style(
        self,
        fill_color=None,
        fill_opacity=None,
        stroke_color=None,
        stroke_width=None,
        stroke_opacity=None,
        recurse=True,
    ):
        self.set_fill(color=fill_color, opacity=fill_opacity, recurse=recurse)
        self.set_stroke(color=stroke_color, width=stroke_width, opacity=stroke_opacity, recurse=recurse)
        return self

    def set_backstroke(self, color=None, width=3):
        if color is None:
            color = "#000000"
        return self.set_stroke(color=color, width=width, behind=True)

    def set_color(self, color, opacity=None, recurse=True):
        self._fill_color = color
        self._stroke_color = color
        self.color = color
        if opacity is not None:
            self._fill_opacity = opacity
            self._stroke_opacity = opacity
            self.opacity = opacity
        if recurse:
            for sub in self.submobjects:
                sub.set_color(color, opacity=opacity, recurse=True)
        return self

    def set_opacity(self, opacity, recurse=True):
        self._fill_opacity = opacity
        self._stroke_opacity = opacity
        self.opacity = opacity
        if recurse:
            for sub in self.submobjects:
                sub.set_opacity(opacity, recurse=True)
        return self

    def get_fill_color(self):
        return self._fill_color

    def get_fill_opacity(self):
        return self._fill_opacity

    def get_stroke_color(self):
        return self._stroke_color

    def get_stroke_width(self):
        return self._stroke_width

    def get_stroke_opacity(self):
        return self._stroke_opacity

    def has_fill(self):
        return self._fill_opacity > 0

    def has_stroke(self):
        return self._stroke_opacity > 0 and self._stroke_width > 0

    def get_color(self):
        if self.has_fill():
            return self._fill_color
        return self._stroke_color

    def match_style(self, vmobject):
        self.set_fill(color=vmobject.get_fill_color(), opacity=vmobject.get_fill_opacity())
        self.set_stroke(
            color=vmobject.get_stroke_color(),
            width=vmobject.get_stroke_width(),
            opacity=vmobject.get_stroke_opacity(),
        )
        return self

    # --- Path building ---

    def start_new_path(self, point):
        point = np.array(point, dtype=np.float64).reshape(3)
        if self.has_points():
            last = self._points[-1]
            self.append_points([last, point])
        else:
            self.set_points([point])
        return self

    def add_line_to(self, point):
        point = np.array(point, dtype=np.float64).reshape(3)
        if not self.has_points():
            self.start_new_path(ORIGIN)
        last = self._points[-1]
        handle = (last + point) / 2.0
        self.append_points([handle, point])
        return self

    def add_quadratic_bezier_curve_to(self, handle, anchor):
        handle = np.array(handle, dtype=np.float64).reshape(3)
        anchor = np.array(anchor, dtype=np.float64).reshape(3)
        if not self.has_points():
            raise ValueError("Must start a path before adding curves")
        self.append_points([handle, anchor])
        return self

    def add_cubic_bezier_curve_to(self, h1, h2, anchor):
        h1 = np.array(h1, dtype=np.float64).reshape(3)
        h2 = np.array(h2, dtype=np.float64).reshape(3)
        anchor = np.array(anchor, dtype=np.float64).reshape(3)
        if not self.has_points():
            raise ValueError("Must start a path before adding curves")
        last = self._points[-1]
        quad_handle = 0.5 * (h1 + h2)
        mid_anchor = 0.25 * last + 0.5 * quad_handle + 0.25 * anchor
        self.append_points([
            0.5 * (last + h1), mid_anchor,
            0.5 * (h2 + anchor), anchor,
        ])
        return self

    def add_smooth_curve_to(self, point):
        point = np.array(point, dtype=np.float64).reshape(3)
        if self.get_num_points() < 2:
            return self.add_line_to(point)
        last = self._points[-1]
        second_last = self._points[-2]
        handle = 2 * last - second_last
        self.append_points([handle, point])
        return self

    def add_arc_to(self, point, angle, n_components=None):
        point = np.array(point, dtype=np.float64).reshape(3)
        if not self.has_points():
            self.start_new_path(ORIGIN)
        if n_components is None:
            n_components = max(1, int(np.ceil(abs(angle) / (PI / 2))))
        arc_pts = quadratic_bezier_points_for_arc(angle, n_components)
        start = self._points[-1]
        vec = point - start
        arc_start = arc_pts[0]
        arc_end = arc_pts[-1]
        arc_vec = arc_end - arc_start
        arc_len = get_norm(arc_vec)
        target_len = get_norm(vec)
        if arc_len < 1e-10 or target_len < 1e-10:
            return self.add_line_to(point)
        scale_factor = target_len / arc_len
        arc_angle = np.arctan2(arc_vec[1], arc_vec[0])
        target_angle = np.arctan2(vec[1], vec[0])
        rot_angle = target_angle - arc_angle
        cos_a, sin_a = np.cos(rot_angle), np.sin(rot_angle)
        transformed = arc_pts.copy()
        transformed -= arc_start
        x_new = transformed[:, 0] * cos_a - transformed[:, 1] * sin_a
        y_new = transformed[:, 0] * sin_a + transformed[:, 1] * cos_a
        transformed[:, 0] = x_new
        transformed[:, 1] = y_new
        transformed *= scale_factor
        transformed += start
        self.append_points(transformed[1:])
        return self

    def close_path(self):
        if not self.has_points():
            return self
        subpaths = self.get_subpaths()
        if len(subpaths) > 0:
            last_subpath = subpaths[-1]
            first_point = last_subpath[0]
            last_point = self._points[-1]
            if not np.allclose(first_point, last_point, atol=1e-6):
                self.add_line_to(first_point)
        return self

    def set_points_as_corners(self, points):
        points = np.array(points, dtype=np.float64)
        if len(points) < 2:
            self.set_points(points)
            return self
        self.clear_points()
        self.start_new_path(points[0])
        for p in points[1:]:
            self.add_line_to(p)
        return self

    def set_points_smoothly(self, points, approx=True):
        points = np.array(points, dtype=np.float64)
        if len(points) < 2:
            self.set_points(points)
            return self
        self.set_points_as_corners(points)
        self.make_smooth(approx=approx)
        return self

    def round_corners(self, radius=0.5):
        if self.get_num_points() < 3:
            return self
        anchors = self.get_anchors()
        if len(anchors) < 3:
            return self
        new_vm = VMobject()
        for i in range(len(anchors)):
            prev_anchor = anchors[i - 1]
            curr_anchor = anchors[i]
            next_anchor = anchors[(i + 1) % len(anchors)]
            vec_to_prev = prev_anchor - curr_anchor
            vec_to_next = next_anchor - curr_anchor
            dist_prev = get_norm(vec_to_prev)
            dist_next = get_norm(vec_to_next)
            if dist_prev < 1e-10 or dist_next < 1e-10:
                continue
            r = min(radius, dist_prev / 2, dist_next / 2)
            unit_prev = vec_to_prev / dist_prev
            unit_next = vec_to_next / dist_next
            arc_start = curr_anchor + r * unit_prev
            arc_end = curr_anchor + r * unit_next
            if not new_vm.has_points():
                new_vm.start_new_path(arc_start)
            else:
                new_vm.add_line_to(arc_start)
            angle = np.arccos(np.clip(np.dot(unit_prev, unit_next), -1, 1))
            cross_val = np.cross(unit_prev[:2], unit_next[:2]) if len(unit_prev) >= 2 else 0
            if cross_val > 0:
                angle = -angle
            new_vm.add_arc_to(arc_end, angle)
        self._points = new_vm._points.copy()
        self._invalidate_bounding_box()
        return self

    # --- Curve queries ---

    def get_num_curves(self):
        n = self.get_num_points()
        if n < 3:
            return 0
        return (n - 1) // 2

    def get_bezier_tuples(self):
        n = self.get_num_curves()
        pts = self._points
        for i in range(n):
            yield pts[2 * i:2 * i + 3]

    def get_anchors(self):
        if self.get_num_points() == 0:
            return np.zeros((0, 3))
        return self._points[::2].copy()

    def get_start_anchors(self):
        if self.get_num_points() == 0:
            return np.zeros((0, 3))
        return self._points[0:-1:2].copy()

    def get_end_anchors(self):
        if self.get_num_points() < 3:
            return np.zeros((0, 3))
        return self._points[2::2].copy()

    def get_subpaths(self):
        if not self.has_points():
            return []
        pts = self._points
        subpath_starts = [0]
        for i in range(1, len(pts) - 1, 2):
            if i + 1 < len(pts):
                handle = pts[i]
                prev_anchor = pts[i - 1]
                next_anchor = pts[i + 1]
                if np.allclose(handle, prev_anchor, atol=1e-6) and not np.allclose(prev_anchor, next_anchor, atol=1e-6):
                    subpath_starts.append(i + 1)
        subpaths = []
        for i, start in enumerate(subpath_starts):
            end = subpath_starts[i + 1] if i + 1 < len(subpath_starts) else len(pts)
            subpaths.append(pts[start:end].copy())
        return subpaths

    def get_arc_length(self, n_sample_points=20):
        pts = self._points
        if len(pts) < 2:
            return 0.0
        alphas = np.linspace(0, 1, n_sample_points)
        samples = np.array([self.point_from_proportion(a) for a in alphas])
        diffs = np.diff(samples, axis=0)
        return float(np.sum(np.linalg.norm(diffs, axis=1)))

    def get_subcurve(self, a, b):
        result = self.copy()
        result.pointwise_become_partial(self, a, b)
        return result

    def is_closed(self):
        if self.get_num_points() < 3:
            return False
        subpaths = self.get_subpaths()
        if len(subpaths) == 0:
            return False
        last_subpath = subpaths[-1]
        return np.allclose(last_subpath[0], last_subpath[-1], atol=1e-6)

    def make_smooth(self, approx=True):
        anchors = self.get_anchors()
        if len(anchors) < 3:
            return self
        handles = approx_smooth_quadratic_bezier_handles(anchors)
        all_points = np.zeros((2 * len(handles) + 1, 3), dtype=np.float64)
        all_points[::2] = anchors[:len(handles) + 1]
        all_points[1::2] = handles
        self.set_points(all_points)
        return self

    def make_jagged(self):
        anchors = self.get_anchors()
        if len(anchors) < 2:
            return self
        self.set_points_as_corners(anchors)
        return self

    def insert_n_curves(self, n):
        if self.get_num_curves() == 0:
            return self
        total_curves = self.get_num_curves()
        curves_to_add = n
        new_total = total_curves + curves_to_add
        new_points = np.zeros((2 * new_total + 1, 3), dtype=np.float64)
        old_curves = list(self.get_bezier_tuples())
        per_curve = curves_to_add // total_curves
        extra = curves_to_add % total_curves
        idx = 0
        for i, curve in enumerate(old_curves):
            subdivisions = 1 + per_curve + (1 if i < extra else 0)
            for j in range(subdivisions):
                a = j / subdivisions
                b = (j + 1) / subdivisions
                sub_pts = partial_bezier_points(curve, a, b)
                new_points[idx] = sub_pts[0]
                new_points[idx + 1] = sub_pts[1]
                idx += 2
        new_points[idx] = old_curves[-1][-1]
        self.set_points(new_points[:idx + 1])
        return self

    def pointwise_become_partial(self, vmobject, a, b):
        if not isinstance(vmobject, VMobject) or vmobject.get_num_curves() == 0:
            return self
        if a >= b:
            self.clear_points()
            return self
        num_curves = vmobject.get_num_curves()
        lower = int(a * num_curves)
        upper = int(np.ceil(b * num_curves))
        lower = min(lower, num_curves - 1)
        upper = min(upper, num_curves)
        new_points = []
        for i in range(lower, upper):
            curve = vmobject._points[2 * i:2 * i + 3]
            if len(curve) < 3:
                continue
            curve_a = max(0, (a * num_curves - i))
            curve_b = min(1, (b * num_curves - i))
            partial = partial_bezier_points(curve, curve_a, curve_b)
            if len(new_points) == 0:
                new_points.extend(partial)
            else:
                new_points.extend(partial[1:])
        if new_points:
            self.set_points(np.array(new_points, dtype=np.float64))
        else:
            self.clear_points()
        return self

    # --- Overrides ---

    def align_points(self, target):
        if not isinstance(target, VMobject):
            super().align_points(target)
            return
        n1 = self.get_num_curves()
        n2 = target.get_num_curves()
        if n1 == n2:
            return
        if n1 == 0 and n2 > 0:
            self.set_points(np.zeros_like(target.get_points()))
            return
        if n2 == 0 and n1 > 0:
            target.set_points(np.zeros_like(self.get_points()))
            return
        if n1 < n2:
            self.insert_n_curves(n2 - n1)
        else:
            target.insert_n_curves(n1 - n2)

    def _interpolate_color(self, mob1, mob2, alpha):
        if isinstance(mob1, VMobject) and isinstance(mob2, VMobject):
            self._fill_color = mob2._fill_color if alpha > 0.5 else mob1._fill_color
            self._stroke_color = mob2._stroke_color if alpha > 0.5 else mob1._stroke_color
            self._fill_opacity = interpolate(mob1._fill_opacity, mob2._fill_opacity, alpha)
            self._stroke_opacity = interpolate(mob1._stroke_opacity, mob2._stroke_opacity, alpha)
            self._stroke_width = interpolate(mob1._stroke_width, mob2._stroke_width, alpha)

    def copy(self):
        result = super().copy()
        result._fill_color = self._fill_color
        result._fill_opacity = self._fill_opacity
        result._stroke_color = self._stroke_color
        result._stroke_opacity = self._stroke_opacity
        result._stroke_width = self._stroke_width
        result._stroke_behind = self._stroke_behind
        return result

    def become(self, target):
        super().become(target)
        if isinstance(target, VMobject):
            self._fill_color = target._fill_color
            self._fill_opacity = target._fill_opacity
            self._stroke_color = target._stroke_color
            self._stroke_opacity = target._stroke_opacity
            self._stroke_width = target._stroke_width
            self._stroke_behind = target._stroke_behind
        return self


class VGroup(Group, VMobject):
    def __init__(self, *vmobjects, **kwargs):
        VMobject.__init__(self, **kwargs)
        self.add(*vmobjects)

    def add(self, *mobjects):
        for mob in mobjects:
            if not isinstance(mob, (VMobject, VGroup)):
                raise TypeError(f"VGroup only accepts VMobject instances, got {type(mob)}")
        return super().add(*mobjects)


class DashedVMobject(VMobject):
    def __init__(self, vmobject, num_dashes=15, dash_ratio=0.5, **kwargs):
        super().__init__(**kwargs)
        if not isinstance(vmobject, VMobject) or vmobject.get_num_curves() == 0:
            return
        self.match_style(vmobject)
        full = 1.0 / num_dashes if num_dashes > 0 else 1.0
        dash_len = full * dash_ratio
        dashes = []
        for i in range(num_dashes):
            a = i * full
            b = a + dash_len
            if b > 1:
                b = 1.0
            dash = vmobject.copy()
            dash.pointwise_become_partial(vmobject, a, b)
            if dash.has_points():
                dashes.append(dash)
        for d in dashes:
            self.add(d)

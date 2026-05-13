import numpy as np
import copy
from animlib.constants import (
    ORIGIN, UP, DOWN, LEFT, RIGHT, OUT,
    DEFAULT_STROKE_WIDTH, DEFAULT_FILL_COLOR, WHITE,
    FRAME_X_RADIUS, FRAME_Y_RADIUS,
    DEFAULT_MOBJECT_TO_EDGE_BUFF, DEFAULT_MOBJECT_TO_MOBJECT_BUFF,
    MED_SMALL_BUFF, SMALL_BUFF, PI,
)
from animlib.math_utils import (
    normalize, get_norm, rotation_matrix, rotate_vector,
    center_of_mass, angle_of_vector,
)
from animlib.bezier import interpolate


class Mobject:
    def __init__(self, color=WHITE, opacity=1.0, z_index=0, **kwargs):
        self.color = color
        self.opacity = opacity
        self.z_index = z_index
        self.submobjects = []
        self.parents = []
        self.updaters = []
        self.updating_suspended = False
        self.target = None
        self.saved_state = None
        self._points = np.zeros((0, 3), dtype=np.float64)
        self._bounding_box = None
        self._needs_new_bounding_box = True
        self.init_points()
        self.init_colors()

    def init_points(self):
        pass

    def init_colors(self):
        pass

    # --- Point data ---

    def set_points(self, points):
        self._points = np.array(points, dtype=np.float64).reshape(-1, 3)
        self._invalidate_bounding_box()
        return self

    def get_points(self):
        return self._points

    def get_num_points(self):
        return len(self._points)

    def has_points(self):
        return self.get_num_points() > 0

    def clear_points(self):
        self._points = np.zeros((0, 3), dtype=np.float64)
        self._invalidate_bounding_box()
        return self

    def append_points(self, new_points):
        new_points = np.array(new_points, dtype=np.float64).reshape(-1, 3)
        if len(self._points) == 0:
            self._points = new_points
        else:
            self._points = np.vstack([self._points, new_points])
        self._invalidate_bounding_box()
        return self

    def get_start(self):
        if not self.has_points():
            raise ValueError("Mobject has no points")
        return self._points[0].copy()

    def get_end(self):
        if not self.has_points():
            raise ValueError("Mobject has no points")
        return self._points[-1].copy()

    def get_all_points(self):
        all_pts = [self.get_points()]
        for sub in self.get_family()[1:]:
            if sub.has_points():
                all_pts.append(sub.get_points())
        if len(all_pts) == 0:
            return np.zeros((0, 3), dtype=np.float64)
        return np.vstack(all_pts)

    def point_from_proportion(self, alpha):
        points = self.get_points()
        if len(points) == 0:
            raise ValueError("Mobject has no points")
        idx = alpha * (len(points) - 1)
        lower = int(idx)
        upper = min(lower + 1, len(points) - 1)
        frac = idx - lower
        return interpolate(points[lower], points[upper], frac)

    # --- Bounding box ---

    def _invalidate_bounding_box(self):
        self._needs_new_bounding_box = True
        for p in self.parents:
            p._invalidate_bounding_box()

    def get_bounding_box(self):
        if self._needs_new_bounding_box:
            self._bounding_box = self._compute_bounding_box()
            self._needs_new_bounding_box = False
        return self._bounding_box

    def _compute_bounding_box(self):
        all_points = self.get_all_points()
        if len(all_points) == 0:
            return np.zeros((3, 3), dtype=np.float64)
        mins = all_points.min(axis=0)
        maxs = all_points.max(axis=0)
        mids = (mins + maxs) / 2.0
        return np.array([mins, mids, maxs], dtype=np.float64)

    def get_bounding_box_point(self, direction):
        bb = self.get_bounding_box()
        direction = np.array(direction, dtype=float)
        result = bb[1].copy()  # start from center
        for dim in range(3):
            if direction[dim] > 0:
                result[dim] = bb[2][dim]
            elif direction[dim] < 0:
                result[dim] = bb[0][dim]
        return result

    def get_center(self):
        return self.get_bounding_box()[1].copy()

    def get_top(self):
        return self.get_bounding_box_point(UP)

    def get_bottom(self):
        return self.get_bounding_box_point(DOWN)

    def get_right_edge(self):
        return self.get_bounding_box_point(RIGHT)

    def get_left_edge(self):
        return self.get_bounding_box_point(LEFT)

    def get_width(self):
        bb = self.get_bounding_box()
        return bb[2][0] - bb[0][0]

    def get_height(self):
        bb = self.get_bounding_box()
        return bb[2][1] - bb[0][1]

    def get_depth(self):
        bb = self.get_bounding_box()
        return bb[2][2] - bb[0][2]

    def get_x(self, direction=ORIGIN):
        return self.get_bounding_box_point(direction)[0]

    def get_y(self, direction=ORIGIN):
        return self.get_bounding_box_point(direction)[1]

    def get_z(self, direction=ORIGIN):
        return self.get_bounding_box_point(direction)[2]

    # --- Transforms ---

    def apply_points_function(self, func, about_point=None, about_edge=None):
        if about_point is None and about_edge is not None:
            about_point = self.get_bounding_box_point(about_edge)

        for mob in self.get_family():
            if not mob.has_points():
                continue
            if about_point is not None:
                mob._points = mob._points - about_point
            mob._points = func(mob._points)
            if about_point is not None:
                mob._points = mob._points + about_point
            mob._invalidate_bounding_box()
        return self

    def shift(self, vector):
        vector = np.array(vector, dtype=float)
        for mob in self.get_family():
            if mob.has_points():
                mob._points = mob._points + vector
            mob._invalidate_bounding_box()
        return self

    def scale(self, factor, about_point=None, about_edge=None, **kwargs):
        if about_point is None and about_edge is None:
            about_point = self.get_center()
        elif about_point is None and about_edge is not None:
            about_point = self.get_bounding_box_point(about_edge)

        if isinstance(factor, (int, float)):
            scale_vec = np.array([factor, factor, factor], dtype=float)
        else:
            scale_vec = np.array(factor, dtype=float)

        def scale_func(points):
            return points * scale_vec

        return self.apply_points_function(scale_func, about_point=about_point)

    def rotate(self, angle, axis=None, about_point=None, **kwargs):
        if axis is None:
            axis = OUT
        if about_point is None:
            about_point = self.get_center()
        rot_mat = rotation_matrix(angle, axis)

        def rotate_func(points):
            return (rot_mat @ points.T).T

        return self.apply_points_function(rotate_func, about_point=about_point)

    def flip(self, axis=UP, about_point=None, **kwargs):
        return self.rotate(PI, axis=axis, about_point=about_point)

    def stretch(self, factor, dim, about_point=None, about_edge=None):
        if about_point is None and about_edge is None:
            about_point = self.get_center()
        elif about_point is None:
            about_point = self.get_bounding_box_point(about_edge)

        def stretch_func(points):
            pts = points.copy()
            pts[:, dim] *= factor
            return pts

        return self.apply_points_function(stretch_func, about_point=about_point)

    def move_to(self, target, aligned_edge=None, coor_mask=None):
        if isinstance(target, Mobject):
            target_point = target.get_bounding_box_point(
                aligned_edge if aligned_edge is not None else ORIGIN
            )
        else:
            target_point = np.array(target, dtype=float)

        if aligned_edge is not None:
            current_point = self.get_bounding_box_point(aligned_edge)
        else:
            current_point = self.get_center()

        shift_vec = target_point - current_point
        if coor_mask is not None:
            shift_vec = shift_vec * np.array(coor_mask, dtype=float)
        return self.shift(shift_vec)

    def next_to(self, target, direction=RIGHT, buff=None, aligned_edge=None, **kwargs):
        if buff is None:
            buff = DEFAULT_MOBJECT_TO_MOBJECT_BUFF
        direction = np.array(direction, dtype=float)

        if isinstance(target, Mobject):
            target_point = target.get_bounding_box_point(direction)
        else:
            target_point = np.array(target, dtype=float)

        if aligned_edge is not None:
            anchor = self.get_bounding_box_point(aligned_edge - direction)
        else:
            anchor = self.get_bounding_box_point(-direction)

        dir_norm = get_norm(direction)
        if dir_norm > 0:
            buff_vec = (direction / dir_norm) * buff
        else:
            buff_vec = np.zeros(3)

        shift_vec = target_point - anchor + buff_vec
        return self.shift(shift_vec)

    def to_edge(self, edge=LEFT, buff=None):
        if buff is None:
            buff = DEFAULT_MOBJECT_TO_EDGE_BUFF
        edge = np.array(edge, dtype=float)
        target = np.zeros(3)
        for dim in range(3):
            if edge[dim] > 0:
                target[dim] = FRAME_X_RADIUS if dim == 0 else FRAME_Y_RADIUS
            elif edge[dim] < 0:
                target[dim] = -FRAME_X_RADIUS if dim == 0 else -FRAME_Y_RADIUS

        current = self.get_bounding_box_point(edge)
        edge_norm = get_norm(edge)
        if edge_norm > 0:
            buff_vec = (edge / edge_norm) * (-buff)
        else:
            buff_vec = np.zeros(3)

        shift_vec = target - current + buff_vec
        # Only shift along dimensions where edge is nonzero
        for dim in range(3):
            if edge[dim] == 0:
                shift_vec[dim] = 0
        return self.shift(shift_vec)

    def to_corner(self, corner=None, buff=None):
        if corner is None:
            corner = DOWN + LEFT
        if buff is None:
            buff = DEFAULT_MOBJECT_TO_EDGE_BUFF
        self.to_edge(UP * corner[1] if corner[1] != 0 else ORIGIN, buff=buff)
        self.to_edge(RIGHT * corner[0] if corner[0] != 0 else ORIGIN, buff=buff)
        return self

    def center(self):
        return self.shift(-self.get_center())

    def align_to(self, target, direction):
        direction = np.array(direction, dtype=float)
        if isinstance(target, Mobject):
            target_point = target.get_bounding_box_point(direction)
        else:
            target_point = np.array(target, dtype=float)
        current_point = self.get_bounding_box_point(direction)
        shift_vec = np.zeros(3)
        for dim in range(3):
            if direction[dim] != 0:
                shift_vec[dim] = target_point[dim] - current_point[dim]
        return self.shift(shift_vec)

    def set_x(self, value, direction=None):
        if direction is None:
            direction = ORIGIN
        return self.shift(np.array([
            value - self.get_bounding_box_point(direction)[0], 0, 0
        ]))

    def set_y(self, value, direction=None):
        if direction is None:
            direction = ORIGIN
        return self.shift(np.array([
            0, value - self.get_bounding_box_point(direction)[1], 0
        ]))

    def set_z(self, value, direction=None):
        if direction is None:
            direction = ORIGIN
        return self.shift(np.array([
            0, 0, value - self.get_bounding_box_point(direction)[2]
        ]))

    def set_width(self, width, stretch=False, about_point=None, about_edge=None):
        current = self.get_width()
        if current == 0:
            return self
        if stretch:
            return self.stretch(width / current, 0, about_point=about_point, about_edge=about_edge)
        return self.scale(width / current, about_point=about_point, about_edge=about_edge)

    def set_height(self, height, stretch=False, about_point=None, about_edge=None):
        current = self.get_height()
        if current == 0:
            return self
        if stretch:
            return self.stretch(height / current, 1, about_point=about_point, about_edge=about_edge)
        return self.scale(height / current, about_point=about_point, about_edge=about_edge)

    def set_depth(self, depth, stretch=False, about_point=None, about_edge=None):
        current = self.get_depth()
        if current == 0:
            return self
        if stretch:
            return self.stretch(depth / current, 2, about_point=about_point, about_edge=about_edge)
        return self.scale(depth / current, about_point=about_point, about_edge=about_edge)

    def replace(self, target, dim_to_match=0, stretch=False):
        if not isinstance(target, Mobject):
            raise TypeError("replace requires a Mobject target")
        if stretch:
            for dim in range(3):
                target_dim = [target.get_width(), target.get_height(), target.get_depth()][dim]
                self_dim = [self.get_width(), self.get_height(), self.get_depth()][dim]
                if self_dim > 0 and target_dim > 0:
                    self.stretch(target_dim / self_dim, dim)
        else:
            dims = [target.get_width(), target.get_height(), target.get_depth()]
            self_dims = [self.get_width(), self.get_height(), self.get_depth()]
            if self_dims[dim_to_match] > 0 and dims[dim_to_match] > 0:
                self.scale(dims[dim_to_match] / self_dims[dim_to_match])
        self.move_to(target)
        return self

    def surround(self, target, dim_to_match=0, stretch=False, buff=SMALL_BUFF):
        self.replace(target, dim_to_match=dim_to_match, stretch=stretch)
        if buff > 0:
            factor_w = (self.get_width() + 2 * buff) / max(self.get_width(), 1e-8)
            factor_h = (self.get_height() + 2 * buff) / max(self.get_height(), 1e-8)
            self.scale(np.array([factor_w, factor_h, 1.0]))
        return self

    def put_start_and_end_on(self, start, end):
        start = np.array(start, dtype=float)
        end = np.array(end, dtype=float)
        current_start = self.get_start()
        current_end = self.get_end()
        current_vec = current_end - current_start
        target_vec = end - start
        current_len = get_norm(current_vec)
        target_len = get_norm(target_vec)
        if current_len < 1e-10 or target_len < 1e-10:
            return self
        self.scale(target_len / current_len)
        current_angle = angle_of_vector(current_vec)
        target_angle = angle_of_vector(target_vec)
        self.rotate(target_angle - current_angle)
        self.shift(start - self.get_start())
        return self

    # --- Colors ---

    def set_color(self, color, opacity=None, recurse=True):
        self.color = color
        if opacity is not None:
            self.opacity = opacity
        if recurse:
            for sub in self.submobjects:
                sub.set_color(color, opacity=opacity, recurse=True)
        return self

    def get_color(self):
        return self.color

    def set_opacity(self, opacity, recurse=True):
        self.opacity = opacity
        if recurse:
            for sub in self.submobjects:
                sub.set_opacity(opacity, recurse=True)
        return self

    def get_opacity(self):
        return self.opacity

    # --- Submobject management ---

    def add(self, *mobjects):
        for mob in mobjects:
            if mob is self:
                raise ValueError("Cannot add a Mobject to itself")
            if not isinstance(mob, Mobject):
                raise TypeError(f"Expected Mobject, got {type(mob)}")
            if mob not in self.submobjects:
                self.submobjects.append(mob)
            if self not in mob.parents:
                mob.parents.append(self)
        self._invalidate_bounding_box()
        return self

    def remove(self, *mobjects, recurse=True):
        for mob in mobjects:
            if mob in self.submobjects:
                self.submobjects.remove(mob)
                if self in mob.parents:
                    mob.parents.remove(self)
            elif recurse:
                for sub in self.submobjects:
                    sub.remove(mob, recurse=True)
        self._invalidate_bounding_box()
        return self

    def clear(self):
        for mob in self.submobjects:
            if self in mob.parents:
                mob.parents.remove(self)
        self.submobjects = []
        self._invalidate_bounding_box()
        return self

    def add_to_back(self, *mobjects):
        for mob in mobjects:
            if mob in self.submobjects:
                self.submobjects.remove(mob)
        self.submobjects = list(mobjects) + self.submobjects
        for mob in mobjects:
            if self not in mob.parents:
                mob.parents.append(self)
        self._invalidate_bounding_box()
        return self

    def get_family(self, recurse=True):
        family = [self]
        if recurse:
            for sub in self.submobjects:
                family.extend(sub.get_family(recurse=True))
        return family

    def family_members_with_points(self):
        return [m for m in self.get_family() if m.has_points()]

    def __getitem__(self, index):
        return self.submobjects[index]

    def __iter__(self):
        return iter(self.submobjects)

    def __len__(self):
        return len(self.submobjects)

    # --- Copy & State ---

    def copy(self):
        result = copy.copy(self)
        result._points = self._points.copy()
        result.submobjects = [sub.copy() for sub in self.submobjects]
        result.parents = []
        result.updaters = list(self.updaters)
        result._needs_new_bounding_box = True
        for sub in result.submobjects:
            sub.parents.append(result)
        return result

    def deepcopy(self):
        return copy.deepcopy(self)

    def generate_target(self):
        self.target = self.copy()
        return self.target

    @property
    def animate(self):
        return _AnimationBuilder(self)

    def save_state(self):
        self.saved_state = self.copy()
        return self

    def restore(self):
        if self.saved_state is not None:
            self.become(self.saved_state)
        return self

    def become(self, target):
        self._points = target._points.copy()
        self.color = target.color
        self.opacity = target.opacity
        old_subs = list(self.submobjects)
        self.clear()
        for i, sub in enumerate(target.submobjects):
            if i < len(old_subs):
                old_subs[i].become(sub)
                self.add(old_subs[i])
            else:
                self.add(sub.copy())
        self._invalidate_bounding_box()
        return self

    def match_points(self, target):
        self.set_points(target.get_points().copy())
        return self

    # --- Updaters ---

    def add_updater(self, func, call_func=True):
        self.updaters.append(func)
        if call_func:
            func(self)
        return self

    def remove_updater(self, func):
        if func in self.updaters:
            self.updaters.remove(func)
        return self

    def clear_updaters(self, recurse=True):
        self.updaters = []
        if recurse:
            for sub in self.submobjects:
                sub.clear_updaters(recurse=True)
        return self

    def has_updaters(self):
        if self.updaters:
            return True
        return any(sub.has_updaters() for sub in self.submobjects)

    def update(self, dt=0, recurse=True):
        if self.updating_suspended:
            return self
        for updater in self.updaters:
            import inspect
            params = inspect.signature(updater).parameters
            if len(params) > 1:
                updater(self, dt)
            else:
                updater(self)
        if recurse:
            for sub in self.submobjects:
                sub.update(dt=dt, recurse=True)
        return self

    def suspend_updating(self):
        self.updating_suspended = True
        return self

    def resume_updating(self):
        self.updating_suspended = False
        return self

    # --- Interpolation (for animations) ---

    def interpolate(self, mob1, mob2, alpha, path_func=None):
        if path_func is None:
            path_func = interpolate
        if mob1.has_points() and mob2.has_points():
            self._points = path_func(mob1._points, mob2._points, alpha)
        self._interpolate_color(mob1, mob2, alpha)
        self._invalidate_bounding_box()
        return self

    def _interpolate_color(self, mob1, mob2, alpha):
        pass

    # --- Alignment (for animations) ---

    def align_data_and_family(self, target):
        self.align_family(target)
        for m1, m2 in zip(self.get_family(), target.get_family()):
            m1.align_points(m2)

    def align_family(self, target):
        my_family_size = len(self.submobjects)
        target_family_size = len(target.submobjects)
        diff = target_family_size - my_family_size
        if diff > 0:
            for _ in range(diff):
                sub = self.copy() if my_family_size == 0 else self.submobjects[-1].copy()
                sub.clear_points()
                self.add(sub)
        elif diff < 0:
            for _ in range(-diff):
                sub = target.copy() if target_family_size == 0 else target.submobjects[-1].copy()
                sub.clear_points()
                target.add(sub)

    def align_points(self, target):
        n1 = self.get_num_points()
        n2 = target.get_num_points()
        if n1 == n2:
            return
        if n1 == 0:
            self.set_points(np.zeros((n2, 3), dtype=np.float64))
        elif n2 == 0:
            target.set_points(np.zeros((n1, 3), dtype=np.float64))
        elif n1 < n2:
            self._resize_points(n2)
        else:
            target._resize_points(n1)

    def _resize_points(self, new_count):
        pts = self._points
        if len(pts) == 0:
            self._points = np.zeros((new_count, 3), dtype=np.float64)
            return
        indices = np.linspace(0, len(pts) - 1, new_count).astype(int)
        self._points = pts[indices]
        self._invalidate_bounding_box()

    def __repr__(self):
        return f"{self.__class__.__name__}(num_points={self.get_num_points()})"


class Group(Mobject):
    def __init__(self, *mobjects, **kwargs):
        super().__init__(**kwargs)
        self.add(*mobjects)


class Point(Mobject):
    def __init__(self, location=None, **kwargs):
        super().__init__(**kwargs)
        if location is None:
            location = ORIGIN
        self.set_points([np.array(location, dtype=float)])

    def get_location(self):
        return self.get_points()[0].copy()

    def set_location(self, point):
        self.set_points([np.array(point, dtype=float)])
        return self


class _AnimationBuilder:
    def __init__(self, mobject):
        self.mobject = mobject
        self.methods = []
        self.anim_kwargs = {}

    def __getattr__(self, name):
        method = getattr(self.mobject, name, None)
        if method is None:
            raise AttributeError(f"{self.mobject.__class__.__name__} has no attribute '{name}'")
        if not callable(method):
            raise AttributeError(f"'{name}' is not a method")

        def method_recorder(*args, **kwargs):
            self.methods.append((name, args, kwargs))
            return self
        return method_recorder

    def set_anim_args(self, **kwargs):
        self.anim_kwargs.update(kwargs)
        return self

    def build(self):
        from animlib.transform import MoveToTarget
        target = self.mobject.generate_target()
        for method_name, args, kwargs in self.methods:
            getattr(target, method_name)(*args, **kwargs)
        return MoveToTarget(self.mobject, **self.anim_kwargs)

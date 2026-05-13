# Acceptance Criteria

## Task 1: Core Mobject with positioning and geometric shapes
(Completed — 27/27 criteria met)

## Task 2: VMobject styling and Bezier path building

### Acceptance Criteria
- [ ] VMobject.set_fill(color, opacity) sets fill color and opacity independently
- [ ] VMobject.set_stroke(color, width, opacity) sets stroke properties independently
- [ ] VMobject.get_fill_color() returns the current fill color
- [ ] VMobject.get_fill_opacity() returns the current fill opacity (default 0.0)
- [ ] VMobject.get_stroke_color() returns the current stroke color
- [ ] VMobject.get_stroke_width() returns the current stroke width
- [ ] VMobject.has_fill() returns True only when fill_opacity > 0
- [ ] VMobject.has_stroke() returns True when stroke_opacity > 0 and width > 0
- [ ] VMobject.set_color() sets both fill and stroke color
- [ ] VMobject.match_style() copies all style from another VMobject
- [ ] VMobject.start_new_path(point) begins a new subpath at the given point
- [ ] VMobject.add_line_to(point) adds a straight line segment
- [ ] VMobject.add_quadratic_bezier_curve_to(handle, anchor) adds a quadratic curve
- [ ] VMobject.add_smooth_curve_to(point) adds a smooth continuation curve
- [ ] VMobject.close_path() closes the current subpath back to start
- [ ] VMobject.set_points_as_corners(points) creates straight-line path through points
- [ ] VMobject.make_smooth() adjusts handles for smooth curves through anchors
- [ ] VMobject.make_jagged() converts smooth curves back to straight segments
- [ ] VMobject.get_anchors() returns all anchor points (every other point)
- [ ] VMobject.get_num_curves() returns the number of Bezier curve segments
- [ ] VMobject.is_closed() returns True when start and end points coincide
- [ ] VMobject.get_arc_length() returns approximate length of the curve
- [ ] DashedVMobject creates a dashed version of any VMobject
- [ ] Ellipse(width, height) creates an ellipse with the given dimensions
- [ ] VGroup only accepts VMobject instances and raises TypeError for non-VMobjects
- [ ] VMobject.set_backstroke() sets a behind-stroke
- [ ] VMobject.pointwise_become_partial(vmobject, a, b) becomes portion a to b of a curve

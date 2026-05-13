# Acceptance Criteria

## Task 1: Core Mobject with positioning and geometric shapes

### Acceptance Criteria
- [ ] Mobject can be created and stores 3D point data as numpy arrays
- [ ] Mobject.shift(vector) translates all points by the given vector and returns self
- [ ] Mobject.scale(factor) scales uniformly about center, scale(factor, about_point=p) scales about p
- [ ] Mobject.rotate(angle) rotates about z-axis, rotate(angle, axis=UP) rotates about given axis
- [ ] Mobject.move_to(point) centers the mobject at the given point
- [ ] Mobject.next_to(target, direction, buff) places the mobject adjacent to target with buffer
- [ ] Mobject.to_edge(direction, buff) moves the mobject to the screen edge
- [ ] Mobject.get_center() returns the center of the bounding box
- [ ] Mobject.get_width/get_height() returns the width/height of the bounding box
- [ ] Mobject.set_width/set_height(value) resizes to target dimension
- [ ] Mobject.get_top/get_bottom/get_left/get_right() returns edge center points
- [ ] Group can hold multiple Mobjects as submobjects and operations apply to all
- [ ] Mobject.copy() returns an independent copy with the same point data
- [ ] Mobject.add/remove manage submobject hierarchy
- [ ] Mobject.get_start/get_end return first/last points
- [ ] Circle(radius=r) creates a circle with correct radius, centered at origin
- [ ] Dot(point) creates a small filled circle at the given point
- [ ] Arc(start_angle, angle, radius) creates a circular arc
- [ ] Line(start, end) creates a line segment between two points
- [ ] Arrow(start, end) creates a line with an arrowhead
- [ ] Rectangle(width, height) creates a rectangle of given dimensions
- [ ] Square(side_length) creates a square
- [ ] Polygon(*vertices) creates a closed polygon through the vertices
- [ ] RegularPolygon(n) creates a regular n-gon
- [ ] Triangle() creates an equilateral triangle
- [ ] Direction constants (UP, DOWN, LEFT, RIGHT, ORIGIN) are 3D numpy arrays
- [ ] Color constants (RED, BLUE, GREEN, etc.) are defined as hex strings

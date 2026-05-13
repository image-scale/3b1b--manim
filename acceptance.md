# Acceptance Criteria

## Tasks 1-4: (Completed)

## Task 5: Value tracking, .animate, color utilities, and path functions

### Acceptance Criteria
- [ ] ValueTracker(value=0) creates a tracker storing a numeric value
- [ ] ValueTracker.get_value() returns the current value
- [ ] ValueTracker.set_value(v) changes the stored value
- [ ] ValueTracker.increment_value(dv) adds to the current value
- [ ] ValueTracker works with animations (interpolation changes the value smoothly)
- [ ] ExponentialValueTracker stores log(value), making interpolation multiplicative
- [ ] mob.animate.shift(RIGHT) returns an animation builder that creates a MoveToTarget
- [ ] mob.animate.scale(2).set_color(RED) chains multiple operations
- [ ] color_to_rgb(hex) converts a hex color string "#RRGGBB" to RGB array [0,1]
- [ ] color_to_rgba(hex, alpha) converts to RGBA array with alpha channel
- [ ] rgb_to_hex(rgb) converts RGB array [0,1] to hex string "#RRGGBB"
- [ ] hex_to_rgb(hex) converts hex string to RGB numpy array
- [ ] interpolate_color(c1, c2, alpha) blends two colors at given ratio
- [ ] color_gradient(colors, n) generates n colors interpolated between reference colors
- [ ] average_color averages multiple colors
- [ ] random_color() returns a valid random hex color
- [ ] straight_path(start, end, alpha) returns linear interpolation
- [ ] path_along_arc(angle) returns a function that moves along a circular arc
- [ ] clockwise_path() returns path_along_arc(-PI)
- [ ] counterclockwise_path() returns path_along_arc(PI)

# Todo

## Plan
Build the animation engine bottom-up by dependency, but each task delivers a self-contained user-facing capability. Start with the core Mobject system and shapes (what users create), then add the animation engine (how users animate), then Scene management (how users orchestrate), and finally value tracking and color utilities.

## Tasks
- [x] Task 1: Implement the core Mobject with positioning, submobject hierarchy, and basic geometric shapes (Circle, Rectangle, Line, Dot, Arrow, Polygon, Arc, Square, RegularPolygon, Triangle). Users can create shapes, position them with shift/scale/rotate/move_to/next_to/to_edge, manage groups, and query geometric properties like width/height/center/bounding_box.
- [x] Task 2: Implement VMobject styling with fill/stroke colors and opacity, Bezier path building (add_line_to, add_curve_to, set_points_as_corners, close_path, make_smooth), DashedVMobject, and Ellipse. Users can style shapes with colors, build custom vector paths, and create dashed outlines.
- [>] Task 3: Implement the animation engine with rate/easing functions (smooth, linear, rush_into, rush_from, there_and_back, etc.), Animation base class, Transform, ReplacementTransform, MoveToTarget, ApplyMethod, FadeIn, FadeOut, FadeTransform, ShowCreation, and Write. Users can animate objects transforming, appearing, disappearing, and being drawn.
- [ ] Task 4: Implement animation composition (AnimationGroup, Succession, LaggedStart, LaggedStartMap) and the Scene class with add/remove/play/wait, auto-add of animated mobjects, and updater execution during playback. Users can compose animations in parallel or sequence and build complete animation scenes.
- [ ] Task 5: Implement ValueTracker for animating numeric values, the .animate property for fluent animation building, color format conversion utilities (hex/RGB/RGBA), color gradients, color interpolation, and path functions (straight, arc, clockwise, counterclockwise) for animation interpolation. Users can track values, build animations fluently, manipulate colors, and control animation motion paths.

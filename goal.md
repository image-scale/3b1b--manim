# Goal

## Project
animlib — a python project.

## Description
A mathematical animation engine for creating precise programmatic animations. Users define Scene subclasses with a `construct()` method, create mathematical objects (Mobjects) like circles, lines, rectangles, and arrows, position them in 2D/3D space, and animate them with transforms, fades, and creation effects. The engine provides a rich set of geometric primitives, Bezier curve-based vector graphics, easing functions, color utilities, and a composable animation system.

## Scope
- ~15 production source files to implement
- ~6 test files to write
- Reproduce core source code, tests, and configuration

## Core Capabilities
1. **Mobject system** — base mathematical object with point data, positioning (shift, scale, rotate, move_to, next_to, to_edge), submobject hierarchy (Group), bounding box queries, copy/state management
2. **VMobject system** — vectorized mobjects using quadratic Bezier curves, fill/stroke styling, path building (lines, arcs, smooth curves, corners), VGroup
3. **Geometric shapes** — Circle, Arc, Dot, Line, Arrow, Rectangle, Square, Polygon, RegularPolygon, Triangle, Ellipse, DashedVMobject
4. **Animation engine** — Animation base with rate functions (smooth, linear, rush_into, etc.), Transform, ReplacementTransform, MoveToTarget, ApplyMethod, FadeIn, FadeOut, ShowCreation, Write, AnimationGroup, Succession, LaggedStart
5. **Scene management** — Scene class that orchestrates mobjects and animations with add/remove/play/wait, auto-add mobjects, updater execution
6. **Value tracking & updaters** — ValueTracker for animating numeric values, updater system for dynamic relationships between mobjects
7. **Color utilities** — Color format conversion (hex, RGB, RGBA), gradients, interpolation, color manipulation
8. **Path functions** — straight path, arc path, clockwise/counterclockwise paths for animation interpolation

# Acceptance Criteria

## Task 1: Core Mobject with positioning and geometric shapes
(Completed — 27/27 criteria met)

## Task 2: VMobject styling and Bezier path building
(Completed — 27/27 criteria met)

## Task 3: Animation engine with transforms, fading, and creation

### Acceptance Criteria
- [ ] smooth(0) returns 0, smooth(1) returns 1, smooth(0.5) returns 0.5
- [ ] linear(t) returns t for all t in [0, 1]
- [ ] rush_into(0) returns 0, rush_into(1) returns 1, accelerates at end
- [ ] rush_from(0) returns 0, rush_from(1) returns 1, decelerates at end
- [ ] there_and_back(0) returns 0, there_and_back(0.5) returns ~1, there_and_back(1) returns 0
- [ ] double_smooth gives S-curve on each half
- [ ] squish_rate_func maps a function to a sub-interval of [0,1]
- [ ] Animation(mobject) stores the mobject and default run_time=1.0
- [ ] Animation.begin() creates starting_mobject as copy
- [ ] Animation.interpolate(alpha) calls interpolate_submobject with rate_func applied
- [ ] Animation.finish() calls interpolate(final_alpha_value)
- [ ] Transform(m1, m2) morphs m1 into m2 over the animation duration
- [ ] Transform aligns point data between source and target
- [ ] ReplacementTransform replaces source with target in scene after animation
- [ ] MoveToTarget uses mobject.target as the transform target
- [ ] ApplyMethod(mob.method, args) applies the method as a transform
- [ ] FadeIn(mob) starts with opacity 0 and interpolates to full opacity
- [ ] FadeIn(mob, shift=UP) also shifts upward during fade
- [ ] FadeOut(mob) ends with opacity 0 and is a remover animation
- [ ] FadeOut(mob, shift=DOWN) shifts downward during fade
- [ ] FadeTransform cross-fades between source and target mobjects
- [ ] ShowCreation progressively draws a VMobject from 0% to 100%
- [ ] Write draws the outline first, then fills in the VMobject
- [ ] ShowCreation with lag_ratio=1 draws submobjects one after another

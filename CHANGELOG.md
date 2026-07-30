# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

This project uses [towncrier](https://towncrier.readthedocs.io) to generate release notes.

<!-- towncrier release notes start -->

## [0.4.0] - 2026-07-30

### Added

- Added property `Coord2.mutable` (#6)
- Added property `Rect.mutable` (#6)
- Added property `Grid2.mutable` (#6)
- Added optional parameter `mut` to `Coord2.__init__()` (#6)
- Added optional parameter `mut` to `Rect.__init__()` (#6)
- Added optional parameter `mut` to `Grid2.__init__()` (#6)
- Added override method `Grid2.from_size()`
  - Allows setting the `step` and `origin` of the resulting instance
- Added function `util.partition()` (#6)

### Changed

- `Coord2`, `Rect`, and `Grid2` are now "immutable" by default, and must be
  initialized with `mut=True` to modify their attributes
- `Coord2` attributes `x` and `y` are now properties
  - Values can only be set if `Coord2` was initialized with `mut=True` (#6)
- `Rect` attributes `x1`, `y1`, `x2`, and `y2` are now properties
  - Values can only be set if `Rect` was initialized with `mut=True` (#6)
- `Grid2` attributes `step` and `origin` are now properties
  - Values can only be set if `Grid2` was initialized with `mut=True` (#6)
- `Grid2.step` and `Grid2.origin` are now properties, value is automatically
  coerced to `Coord2` when setting

## [0.3.0]

### Added

- Added parameter `inf` to method `Grid2.steps_x()`
- Added parameter `inf` to method `Grid2.steps_y()`
- Added method `Coord2.snap_to_grid()`
- Implemented `__copy__` for `Coord2` (#1)
- Implemented `__str__` for `Coord2`
- Implemented `__copy__` for `Rect` (#1)
- Implemented `__copy__` for `Grid2` (#1)
- Implemented `__deepcopy__` for `Grid2` (#1)
- Added function `util.take_n()`

### Changed

- `Grid2` is now a subclass of `Rect`
- `Grid2.__str__()` now includes step and origin values instead of just the rectangle coordiantes
- `Grid2.steps()` now yields coordinates even if the X or Y of the step value is 0, in which case
  the corresponding value of the grid's origin coordinate is used for that value of the yielded
  coordinates
- `util.snap_num()` parameter `mult` is now typed as `float`
- `util.snap_num()` return type is now `float`
- `util.snap_num()` parameter `snap_fn` is now optional (defaults to the built-in `round` function)

## [0.2.0] - 2026-07-22

### Added

- Added method `Coord2.distance()`
  - Calculates euclidean or taxicab distance between two coordinates depending on the `mode` parameter
- Added method `Grid2.project()`
  - Returns a coordinate in the same relative position to the `other` grid as it was to `self`
  - Can be useful for plotting points from a grid with a negative x1 or y1 value onto an image which
    requires using a grid whose top-left is 0, 0
- Added property `Rect.bottom_left`
- Added property `Rect.bottom_right`
- Added property `Rect.top_left`
- Added property `Rect.top_right`

## [0.1.0] - 2026-07-21

Initial beta release.

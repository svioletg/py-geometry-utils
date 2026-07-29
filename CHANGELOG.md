# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
- `util.snap_num()` parameter `mult` is now typed as `float`
- `util.snap_num()` return type is now `float`
- `util.snap_num()` parameter `snap_fn` is now optional (defaults to the built-in `round` function)

### Deprecated

### Removed

### Fixed

### Security

## [0.2.0]

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

## [0.1.0]

Initial beta release.

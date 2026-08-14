# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a
Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

This project uses [towncrier](https://towncrier.readthedocs.io) to generate
release notes.

---

<!-- towncrier release notes start -->

## [0.7.0] - 2026-08-14

### Added

- Added methods `ceil()`, `floor()`, and `round()` to `Rect`

## [0.6.0] - 2026-08-08

### Added

- Added function `assert_yields()` to `tests/__init__.py`
- Added function `util.lerp()` (#16)
- Added method `Coord2.ceil()` (#17)
- Added method `Coord2.floor()` (#17)
- Added method `Coord2.intersects()` (#15)
- Added method `Coord2.lerp()` (#16)
- Added method `Coord2.lerp_iter()` (#16)
- Added method `Coord2.round()` (#17)
- Method `Coord2.distance()` now supports chebyshev distance (#14)

### Changed

- Method `Coord2.snap_to_grid()` parameter `snap_fn` now defaults to `None`,
  set to `round` in method body instead (#17)
  - Done to avoid shadowing the built-in `round` with the addition of the
    `Coord2.round()` method
- `Coord2` and `Rect`'s `__getitem__` implementations now do if/elif checks
  instead of constructing a tuple, improving its performance by a small amount
  (#19)

### Removed

- Remove docstrings from `Coord2` methods `__ge__`, `__gt__`, `__le__`, and
  `__lt__`

### Fixed

- Fixed an incorrect description in `Coord2.in_bounds()` docstring

## [0.5.0] - 2026-08-02

### Added

- Added method `Coord2._compare()` to handle all comparisons except `==`
- Added method `Coord2.zip_with()`
- Added method `Grid2.zip_with()`
- Added method `Rect.zip_with()`
- Added support for `# testcheck: ignore` comments on class definitions
- Added type alias `Tuple2`
- Added type alias `Tuple4`

### Changed

- Initializing `Grid2` with an out-of-bounds `origin` value no longer raises an
  error (#7)
  - "steps" methods will yield no steps when `Grid2.origin` is out of bounds
- Attribute `tests.check.FunctionFinder.functions` now uses `ast.ClassDef`
  nodes for keys instead of class name strings
- Rename `tests.check.FUNC_IGNORE_REGEX` to `IGNORE_REGEX`
- Renamed parameter `value` to `other` in `Coord2` methods `__eq__`, `__ge__`,
  `__gt__`, `__le__`, and `__lt__` for consistency with other methods
- `Coord2` comparison methods `__ge__`, `__gt__`, `__le__`, and `__lt__` all
  now `Coord2._compare()` instead of implementing the logic in themselves
- `Coord2` objects are now always truthy, removed `__bool__` implementation
- `tests.check.make_test_name()` now adds a prefix for private (and not magic)
  methods

### Removed

- Removed method `Coord2.binop()`
- Removed type alias `BinaryOp`

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
- `Grid2.__str__()` now includes step and origin values instead of just the
  rectangle coordiantes
- `Grid2.steps()` now yields coordinates even if the X or Y of the step value
  is 0, in which case the corresponding value of the grid's origin coordinate
  is used for that value of the yielded coordinates
- `util.snap_num()` parameter `mult` is now typed as `float`
- `util.snap_num()` return type is now `float`
- `util.snap_num()` parameter `snap_fn` is now optional (defaults to the
  built-in `round` function)

## [0.2.0] - 2026-07-22

### Added

- Added method `Coord2.distance()`
  - Calculates euclidean or taxicab distance between two coordinates depending
    on the `mode` parameter
- Added method `Grid2.project()`
  - Returns a coordinate in the same relative position to the `other` grid as
    it was to `self`
  - Can be useful for plotting points from a grid with a negative x1 or y1
    value onto an image which requires using a grid whose top-left is 0, 0
- Added property `Rect.bottom_left`
- Added property `Rect.bottom_right`
- Added property `Rect.top_left`
- Added property `Rect.top_right`

## [0.1.0] - 2026-07-21

Initial beta release.

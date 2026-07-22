# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Added method `Coord2.distance()`
  - Calculates euclidean or taxicab distance between two coordinates depending on the `mode` parameter
- Added method `Grid2.project()`
  - Returns a coordinate in the same relative position to the `other` grid as it was to `self`
  - Can be useful for plotting points from a grid with a negative x1 or y1 value onto an image which
    requires using a grid whose top-left is 0, 0

### Changed

### Deprecated

### Removed

### Fixed

### Security

## [0.1.0]

Initial beta release.

# py-geometry-utils <!-- omit in toc -->

Provides utilities for working with coordinates, rectangles, and grids.

> [!WARNING]
> This library is still in beta, breaking changes between releases are likely for 0.x versions.

Initially [part of a different project](https://github.com/svioletg/py-squaremap-combiner/blob/47f30bffb5de121fbf5ce17621ce3b8127cd36c3/src/squaremap_combine/geo.py),
I wanted to use it in a few other projects so I decided to separate it out into its own package.

PyPI: <https://pypi.org/project/py-geometry-utils/>

Documentation: <https://py-geometry-utils.readthedocs.io/en/latest/>

Changelog: <https://github.com/svioletg/py-geometry-utils/blob/main/CHANGELOG.md>

- [Usage](#usage)
- [Features](#features)
  - [Immutability](#immutability)
  - [Type coercion](#type-coercion)
  - [Math \& other combining operations](#math--other-combining-operations)
  - [Copying](#copying)
  - [Iteration \& other magic method implementations](#iteration--other-magic-method-implementations)
  - [Comparing](#comparing)

## Usage

Install with pip or include as a dependency as `py-geometry-utils`, the package will be available as
the `geometry` module.

Construct a 2D coordinate: `Coord2(1, 2)`

Construct a rectangle: `Rect(0, 0, 10, 10)`

Construct a 2D grid: `Grid2(-10, -10, 10, 10, step=(1, 1), origin=(0, 0))` (`step` and `origin`
optional, defaults to `Coord2(1, 1)` and the center coordinate of the rectangle respectively)

## Features

### Immutability

All geometry classes are immutable by default, meaning their attributes (such as `x` and `y`) cannot
be reassigned after constructing the instance.

```py
p = Coord2(0, 0)
p.x = 1
# TypeError: Cannot modify attribute of immutable Coord2 instance

r = Rect(0, 0, 10, 10)
r.x1 = 1
# TypeError: Cannot modify attribute of immutable Rect instance

g = Grid2(-10, -10, 10, 10, step=(1, 1), origin=(0, 0))
g.step = Coord2(2, 2)
# TypeError: Cannot modify attribute of immutable Coord2 instance
```

To make them mutable, `mut=True` must be passed to their constructors:

```py
p = Coord2(0, 0, mut=True)
p.x = 1
assert p.x == 1

r = Rect(0, 0, 10, 10, mut=True)
r.x1 = 1
assert r.x1 == 1

g = Grid2(-10, -10, 10, 10, step=(1, 1), origin=(0, 0), mut=True)
g.step = Coord2(2, 2)
assert g.step == Coord2(2, 2)
```

When `Grid2` is constructed with `mut=False`, the passed `step` and `origin` values are *always*
copied as new immutable `Coord2` instances. Otherwise, the objects are used as-is if they are
already `Coord2` instances (meaning in `Grid2(..., step=Coord2(1, 1, mut=False), mut=True)`
the `step` value will maintain its immutability); if they're tuples, they are converted to
new mutable `Coord2` objects.

### Type coercion

All `Coord2` and `Rect` methods which take a second coordinate or rectangle as an argument will
also accept their respective tuple of values. If a method's argument takes `Coord2`, it will also
accept `tuple[float, float]`; if it takes `Rect`, it will accept
`tuple[float, float, float, float]`.

```py
assert Coord2(0, 0).distance(Coord2(10, 10)) == 20
assert Coord2(0, 0).distance((10, 10)) == 20
```

`Grid2.step` and `Grid2.origin`'s setters will accept a plain tuple of two numbers in addition to a
`Coord2` instance, those values being converted to `Coord2` implicitly:

```py
g = Grid2(-10, -10, 10, 10, mut=True)
g.step = (10, 10)
# g.step == Coord2(10, 10)
```

### Math & other combining operations

`Coord2` supports the operators `+`, `-`, `*`, `/`, `//`, `%`, and `**` between either other
`Coord2` instances, `tuple[float, float]`, or single numbers (which gets treated as `(n, n)`).

```py
assert Coord2(1, 1) + 1 == Coord2(2, 2)
assert Coord2(1, 1) + (1, 2) == Coord2(2, 4)
assert Coord2(1, 1) + Coord2(1, 2) == Coord2(2, 4)

assert Coord2(1, 1) - 1 == Coord2(0, 0)
assert Coord2(1, 1) - (1, 2) == Coord2(0, -1)
assert Coord2(1, 1) - Coord2(1, 2) == Coord2(0, -1)

# and so on...
```

You can also use the [`Coord2.zip_with()`](https://py-geometry-utils.readthedocs.io/en/latest/reference/index.html#geometry.Coord2.zip_with)
method to combine two coordinates together using a given function, where a new `Coord2` instance is
constructed using the result of applying `fn` to both original coordinates' `x` and `y` values
individually:

```py
assert Coord2(0, 1).zip_with(max, (1, 0)) == Coord2(1, 1)
```

[`Coord2.map()`](https://py-geometry-utils.readthedocs.io/en/latest/reference/index.html#geometry.Coord2.zip_with)
returns a new `Coord2` applying a function to the original coordinates' values:

```py
assert Coord2(1, 2).map(lambda n: (n * 10) if n % 2 == 0 else (n / 10)) == Coord2(0.1, 20)
```

[`Coord2.as_tuple()`](https://py-geometry-utils.readthedocs.io/en/latest/reference/index.html#geometry.Coord2.zip_with)
by default returns the `x` and `y` values of a coordinate as a simple tuple, but can optionally
take a function argument to transform those values before returning it:

```py
assert Coord2(1, 2).as_tuple() == (1, 2)
assert Coord2(1, 2).as_tuple(str) == ('1', '2')
```

`Rect` and `Grid2` also have `as_tuple`, `map`, and `zip_with` methods that behave the same way with
their respective classes. `Grid2` is a subclass of `Rect` and so simply inherits the former two
methods, but has its own implementation of [`zip_with`](https://py-geometry-utils.readthedocs.io/en/latest/reference/index.html#geometry.Grid2.zip_with)
which allows specifying the `step` and `origin` values to set for the returned new instance.

### Copying

`Coord2`, `Rect`, and `Grid2` all implement `__copy__` by having it return a new instance with the
same coordinate values, with `Grid2.__copy__()` also copying the `step` and `origin` values (which
are `Coord2` instances, so `Coord2.__copy__()` is invoked for them).

### Iteration & other magic method implementations

`Coord2`, `Rect`, and `Grid2` all support both `__iter__` and `__getitem__`. `__iter__` yields the
coordinate values for the class, meaning `x` and `y` for `Coord2`, and `x1`, `y1`, `x2`, and `y2`
for `Rect` and `Grid2`. This is also the order of attributes returned for `as_tuple()` on each of
these classes. `__getitem__` acts as a shortcut for `.as_tuple()[n]`.

### Comparing

All classes support `==`, comparing each instance's coordinate values. They can also be compared
with tuples:

```python
assert Coord2(1, 2) == Coord2(1, 2)
assert Coord2(1, 2) == (1, 2)

assert Rect(0, 0, 10, 10) == Rect(0, 0, 10, 10)
assert Rect(0, 0, 10, 10) == (0, 0, 10, 10)
```

> [!NOTE]
> Comparing two `Grid2` instances will not take into account their `step` and `origin` values.

`Coord2` additionally supports the `>=`, `>`, `<=`, and `<` operators, comparing it and another
coordinate's values the same way that tuples are compared (e.g. `Coord2(x, y) > Coord2(x, y)` will
always equal the outcome of `(x, y) > (x, y)`).

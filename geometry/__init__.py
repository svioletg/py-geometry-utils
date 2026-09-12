"""Utilities for working with coordinates and rectangles/grids."""
import math
import operator
from collections.abc import Callable, Generator, Iterable
from copy import copy
from itertools import product
from typing import Literal, Self, cast, overload, override

from geometry.util import snap_num

__version__ = '0.7.0'

type Tuple2[T] = tuple[T, T]
"""A tuple of 2 values of the same type."""
type CoordOrTuple2 = Coord2 | tuple[float, float]
"""A :class:`Coord2` instance or a tuple of two ``float`` types as X and Y coordinates."""
type Tuple4[T] = tuple[T, T, T, T]
"""A tuple of 4 values of the same type."""
type RectOrTuple = Rect | tuple[float, float, float, float]
"""A :class:`Rect` instance or a tuple of four ``float`` types as X1, Y1, X2, and Y2 coordinates."""

class Coord2:
    """Represents a 2D coordinate.

    Properties :data:`x` and :data:`y` are immutable by default; initialize the instance with ``mut=True`` to allow
    setting their values.
    """

    def __init__(self, x: float, y: float, *, mut: bool = False) -> None:
        """
        :param mut: Whether this instance's attributes can be modified or not. If ``False``, ``TypeError`` is raised
            when attempting to reassign them.
        """  # noqa: D205, D212
        if not isinstance(x, int | float):
            raise TypeError(f"{self.__class__.__name__}.__init__() parameter 'x' must be 'int' or 'float': {x!r}")
        if not isinstance(y, int | float):
            raise TypeError(f"{self.__class__.__name__}.__init__() parameter 'y' must be 'int' or 'float': {y!r}")

        self._mut = mut

        self._x = x
        self._y = y

    @property
    def x(self) -> float:  # testcheck: ignore
        """X coordinate."""
        return self._x

    @x.setter
    def x(self, value: float) -> None:
        if not self._mut:
            raise TypeError(f'Cannot modify attribute of immutable {self.__class__.__name__} instance')
        self._x = value

    @property
    def y(self) -> float: # testcheck: ignore
        """Y coordinate."""
        return self._y

    @y.setter
    def y(self, value: float) -> None:
        if not self._mut:
            raise TypeError(f'Cannot modify attribute of immutable {self.__class__.__name__} instance')
        self._y = value

    @property
    def mutable(self) -> bool:
        """Whether this instance's attributes can be modified."""
        return self._mut

    def __repr__(self) -> str:  # noqa: D105
        return f'{self.__class__.__name__}(x={self.x}, y={self.y})'

    def __str__(self) -> str:
        """Returns this coordinate in the format ``(x, y)``."""
        return f'({self.x}, {self.y})'

    def __iter__(self) -> Generator[float]:
        """Yields the X and Y values of this coordinate."""
        yield from self.as_tuple()

    def __getitem__(self, idx: int) -> float:
        """Returns the item at ``idx`` as if from a tuple of this coordinate's values.

        .. note::
            A tuple of this coordinate is not actually constructed, a basic ``if`` block is used instead since it's
            faster than making the tuple and accessing it; ``IndexError`` is still raised when out of range.
        """
        if idx == 0:
            return self.x
        elif idx == 1:
            return self.y

        raise IndexError(idx)

    def __hash__(self) -> int:
        """Returns the hash of a tuple of this coordinate's values."""
        return hash(self.as_tuple())

    def __copy__(self, *, mut: bool | None = None) -> Self:
        """Returns a new instance with the same values as this instance, optionally changing its mutability.

        :param mut: Sets the mutability of the copied instance. If ``None``, the current value for the instance being
            copied is used.
        """
        return self.__class__(self.x, self.y, mut=mut if mut is not None else self.mutable)

    def __eq__(self, other: object) -> bool:
        """Compares the X and Y values of two coordinates, returns ``False`` for other objects."""
        if isinstance(other, tuple):
            return self.as_tuple() == other
        if isinstance(other, self.__class__):
            return self.as_tuple() == other.as_tuple()

        return False

    def _compare(self, op: Callable[[Tuple2[float], Tuple2[float]], bool], other: Self | Tuple2[float]) -> bool:
        if isinstance(other, tuple):
            return op(self.as_tuple(), cast('Tuple2[float]', other))
        if isinstance(other, Coord2):
            return op(self.as_tuple(), other.as_tuple())

        return NotImplemented

    def __ge__(self, other: Self | tuple[float, float]) -> bool:  # noqa: D105
        return self._compare(operator.ge, other)

    def __gt__(self, other: Self | tuple[float, float]) -> bool:  # noqa: D105
        return self._compare(operator.gt, other)

    def __le__(self, other: Self | tuple[float, float]) -> bool:  # noqa: D105
        return self._compare(operator.le, other)

    def __lt__(self, other: Self | tuple[float, float]) -> bool:  # noqa: D105
        return self._compare(operator.lt, other)

    def __add__(self, other: Self | tuple[float, float] | float) -> Self:
        """Returns a new coordinate with this and another coordinate's X and Y values added together.

        If given a single value, it is added to the X and Y values of this coordinate.

        >>> assert Coord2(1, 2) + Coord2(1, 2) == Coord2(2, 4)
        >>> assert Coord2(1, 2) + (1, 2) == Coord2(2, 4)
        >>> assert Coord2(1, 2) + 1 == Coord2(2, 3)
        """
        return self.zip_with(operator.add, other)

    def __sub__(self, other: Self | tuple[float, float] | float) -> Self:
        """Returns a new coordinate with this and another coordinate's X and Y values subtracted from eachother.

        If given a single value, it is subtracted from the X and Y values of this coordinate.

        >>> assert Coord2(1, 2) - Coord2(1, 2) == Coord2(0, 0)
        >>> assert Coord2(1, 2) - (1, 2) == Coord2(0, 0)
        >>> assert Coord2(1, 2) - 1 == Coord2(0, 1)
        """
        return self.zip_with(operator.sub, other)

    def __mul__(self, other: Self | tuple[float, float] | float) -> Self:
        """Returns a new coordinate with this and another coordinate's X and Y multiplied together.

        If given a single value, the X and Y values of this coordinate are multiplied by it.

        >>> assert Coord2(1, 2) * Coord2(2, 4) == Coord2(2, 8)
        >>> assert Coord2(1, 2) * (2, 4) == Coord2(2, 8)
        >>> assert Coord2(1, 2) * 2 == Coord2(2, 4)
        """
        return self.zip_with(operator.mul, other)

    def __truediv__(self, other: Self | tuple[float, float] | float) -> Self:
        """Returns a new coordinate with this and another coordinate's X and Y divided by eachother.

        If given a single value, the X and Y values of this coordinate are divided by it.

        >>> assert Coord2(1, 2) / Coord2(2, 8) == Coord2(0.5, 0.25)
        >>> assert Coord2(1, 2) / (2, 8) == Coord2(0.5, 0.25)
        >>> assert Coord2(1, 2) / 2 == Coord2(0.5, 1.0)
        """
        other = (other, other) if isinstance(other, int | float) else other

        return self.zip_with(operator.truediv, other)

    def __floordiv__(self, other: Self | tuple[float, float] | float) -> Self:
        """Returns a new coordinate with this and another coordinate's X and Y values divided by eachother and floored.

        If given a single value, the X and Y values of this coordinate are divided by it and floored.

        >>> assert Coord2(1, 2) // Coord2(2, 8) == Coord2(0, 0)
        >>> assert Coord2(1, 2) // (2, 8) == Coord2(0, 0)
        >>> assert Coord2(1, 2) // 2 == Coord2(0, 1)
        """
        return self.zip_with(operator.floordiv, other)

    def __mod__(self, other: Self | tuple[float, float] | float) -> Self:
        """Returns a new coordinate with this and another coordinate's X and Y values added together.

        If given a single value, it is added to the X and Y values of this coordinate.

        >>> assert Coord2(1, 2) % Coord2(2, 8) == Coord2(1, 2)
        >>> assert Coord2(1, 2) % (2, 8) == Coord2(1, 2)
        >>> assert Coord2(1, 2) % 2 == Coord2(1, 0)
        """
        return self.zip_with(operator.mod, other)

    def __pow__(self, other: Self | tuple[float, float] | float) -> Self:
        """Returns a new coordinate with this and another coordinate's X and Y values added together.

        If given a single value, it is added to the X and Y values of this coordinate.

        >>> assert Coord2(1, 2) ** Coord2(2, 4) == Coord2(1, 16)
        >>> assert Coord2(1, 2) ** (2, 4) == Coord2(1, 16)
        >>> assert Coord2(1, 2) ** 2 == Coord2(1, 4)
        """
        return self.zip_with(operator.pow, other)

    @overload
    def as_tuple(self, map_fn: None = None) -> tuple[float, float]: ...
    @overload
    def as_tuple[U](self, map_fn: Callable[[float], U]) -> tuple[U, U]: ...
    def as_tuple[U](self, map_fn: Callable[[float], U] | None = None) -> tuple[object, object]:
        """Returns the coordinate as a tuple, optionally mapping the values.

        It is recommended to use this instead of the tuple constructor (``tuple(self)``) since that requires iterating
        over the coordinate, where this method constructs the tuple from direct attribute access and is much faster.
        """
        if map_fn:
            return (map_fn(self.x), map_fn(self.y))

        return (self.x, self.y)

    def ceil(self) -> Self:
        """Rounds up both values of this coordinate."""
        return self.__class__(math.ceil(self.x), math.ceil(self.y))

    def copy(self, *, mut: bool | None = None) -> Self:
        """Returns a copy of this instance, optionally changing its mutability.

        See :meth:`__copy__`.
        """
        return self.__copy__(mut=mut)

    def distance(self, other: CoordOrTuple2, mode: Literal['chebyshev', 'euclid', 'taxi'] = 'taxi') -> float:
        """Returns the distance from this coordinate to ``other`` based on ``mode``.

        :param mode: How to calculate the distance; either chebyshev distance, euclidean (``'euclid'``) distance, or
            taxicab (``'taxi'``) distance.
        """
        match mode:
            case 'chebyshev':
                return max(abs(other[0] - self.x), abs(other[1] - self.y))
            case 'euclid':
                return math.sqrt(((self[0] - other[0]) ** 2) + ((self[1] - other[1]) ** 2))
            case 'taxi':
                return sum((self - other).as_tuple(abs))
            case _:
                raise ValueError(f'Unexpected mode: {mode!r}')

    def format(self, s: str) -> str:
        """Returns ``s`` formatted with this coordinate's ``x`` and ``y`` values."""
        return s.format(x=self.x, y=self.y)

    def floor(self) -> Self:
        """Floors both values of this coordinate."""
        return self.__class__(math.floor(self.x), math.floor(self.y))

    def intersects(self, a: CoordOrTuple2, b: CoordOrTuple2, *, rel_tol: float = 1e-09, abs_tol: float = 0.0) -> bool:
        """Returns whether this coordinate intersects the line drawn from ``a`` to ``b``.

        ``rel_tol`` and ``abs_tol`` values will be passed to the :func:`math.isclose` call to fine tune how close the
        point needs to be to the line; see the documentation for ``isclose`` for details.
        """
        ax, ay = (a[0], a[1]) if isinstance(a, tuple) else (a.x, a.y)
        bx, by = (b[0], b[1]) if isinstance(b, tuple) else (b.x, b.y)

        # If the line is straight, we can just do a comparison check; *much* faster than using `.distance()`
        if ax == bx:
            return False if not math.isclose(self.x, ax) else (min(ay, by) <= self.y <= max(ay, by))
        if ay == by:
            return False if not math.isclose(self.y, ay) else (min(ax, bx) <= self.x <= max(ax, bx))

        return math.isclose(
            self.distance(a, 'euclid') + self.distance(b, 'euclid'),
            Coord2(ax, ay).distance(b, 'euclid'),
            rel_tol=rel_tol,
            abs_tol=abs_tol,
        )

    def in_bounds(self, rect: RectOrTuple, *, edge_ok: bool = True) -> bool:
        """Returns whether this coordinate is within a rectangle's bounds.

        :param edge_ok: Whether the coordinate being on the rectangle's edge counts as in bounds or not.

        >>> assert Coord2(1, 1).in_bounds((0, 0, 2, 2))
        >>> assert Coord2(0, 0).in_bounds((0, 0, 2, 2))
        >>> assert not Coord2(0, 0).in_bounds((0, 0, 2, 2), edge_ok=False)
        >>> assert Coord2(2, 2).in_bounds((0, 0, 2, 2))
        >>> assert not Coord2(2, 2).in_bounds((0, 0, 2, 2), edge_ok=False)
        >>> assert not Coord2(3, 3).in_bounds((0, 0, 2, 2))
        """
        return (rect[0] <= self.x <= rect[2]) and (rect[1] <= self.y <= rect[3]) \
            if edge_ok else (rect[0] < self.x < rect[2]) and (rect[1] < self.y < rect[3])

    def lerp(self, other: CoordOrTuple2, factor: float) -> Self:
        """Returns a new coordinate from this coordinate moved straight toward another by ``factor``.

        >>> assert Coord2(0, 0).lerp((1, 1), 0.5) == Coord2(0.5, 0.5)
        >>> assert Coord2(1, 2).lerp((2, 4), 0.5) == Coord2(1.5, 3)
        """
        return self.__class__((self.x + factor * (other[0] - self.x)), (self.y + factor * (other[1] - self.y)))

    def lerp_iter(self, other: CoordOrTuple2, step: float = 0.1, *, start: float = 0, end: float = 1) \
        -> Generator[Self]:
        """Yields coordinates moving from ``self`` toward ``other`` by ``step``.

        Yields ``self.lerp(other, factor)``, with the initial factor value being ``start``. The lerp factor is then
        increased by ``step`` each iteration while ``factor <= end`` if ``step`` is positive, or if ``factor >= end`` if
        ``step`` is negative.

        :param start: The lerp factor to start from.
        :param end: The lerp factor to end at.

        :raises ValueError:
            ``step`` is 0, or ``step``, ``start``, and ``end`` are set to values such that this generator would yield
            infinitely.
        """
        if step == 0:
            raise ValueError("lerp_iter() parameter 'step' cannot be 0")

        if (end < start) and (step > 0):
            raise ValueError(f"'end' must be greater than 'start' if 'step' is positive: {step!r}")
        if (end > start) and (step < 0):
            raise ValueError(f"'end' must be less than 'start' if 'step' is negative: {step!r}")

        factor: float = start

        while (factor <= end) if step > 0 else (factor >= end):
            yield self.lerp(other, factor)
            factor += step

    def map(self, fn: Callable[[float], float]) -> Self:
        """Returns a new instance of this class with ``fn`` applied to its ``x`` and ``y`` attributes."""
        return self.__class__(fn(self.x), fn(self.y))

    def on_edge(self, rect: RectOrTuple) -> bool:
        """Returns whether this coordinate sits on the edge of a rectangle."""
        return ((rect[0] <= self.x <= rect[2]) and (self.y in (rect[1], rect[3]))) \
            or ((rect[1] <= self.y <= rect[3]) and (self.x in (rect[0], rect[2])))

    def round(self, ndigits: int | None = None) -> Self:
        """Rounds this coordinate to a given number of places.

        Both coordinate values will be converted to ``int`` if ``ndigits`` is ``None``.
        """
        return self.__class__(round(self.x, ndigits), round(self.y, ndigits))

    def snap_to_grid(self, grid: 'Grid2', snap_fn: Callable[[float], int] | None = None) -> Self:
        """Returns a new instance whose X and Y values have been aligned to ``grid``.

        Snapping is done based on ``grid``'s ``step`` and ``origin`` values. If either value of ``grid.step`` is 0,
        that part of the coordinate is set to the corresponding value of the grid's origin, e.g. if ``grid.step.x`` is
        0, ``grid.origin.x`` is used for the ``x`` value of the returned instance.

        :param snap_fn: Refer to :func:`geometry.util.snap_num`. Defaults to the built-in ``round``.
        """
        snap_fn = snap_fn or round

        return self.__class__(
            grid.origin.x if not grid.step.x \
                else snap_num(self.x - grid.origin.x, grid.step.x, snap_fn) + grid.origin.x,
            grid.origin.y if not grid.step.y \
                else snap_num(self.y - grid.origin.y, grid.step.y, snap_fn) + grid.origin.y,
        )

    def zip_with(self, fn: Callable[[float, float], float], other: Self | tuple[float, float] | float) -> Self:
        """Combines this and another instance or tuple's values using ``fn``.

        The values used are those returned by iterating over the instance—for :class:`Coord2`, that would be ``x`` and
        ``y``. If a single number is given for ``other``, it is used for both values.
        """
        if not isinstance(other, Coord2 | tuple):
            other = (other, other)

        return self.__class__(fn(self.x, other[0]), fn(self.y, other[1]))

class Rect:
    """Represents a rectangle using its top-left and bottom-right coordinates.

    Properties :data:`x1`, :data:`y1`, :data:`x2`, and :data:`y2` are immutable by default; initialize the instance with
    ``mut=True`` to allow setting their values.
    """

    def __init__(self, x1: float, y1: float, x2: float, y2: float, *, mut: bool = False) -> None:
        """
        :param mut: Whether this instance's attributes can be modified or not. If ``False``, ``TypeError`` is raised
            when attempting to reassign them.
        """  # noqa: D205, D212
        self._mut = mut

        self._x1 = x1
        self._y1 = y1
        self._x2 = x2
        self._y2 = y2

    @property
    def x1(self) -> float:  # testcheck: ignore
        """Top-left X coordinate."""
        return self._x1

    @x1.setter
    def x1(self, value: float) -> None:
        if not self._mut:
            raise TypeError(f'Cannot modify attribute of immutable {self.__class__.__name__} instance')
        self._x1 = value

    @property
    def y1(self) -> float:  # testcheck: ignore
        """Top-left Y coordinate."""
        return self._y1

    @y1.setter
    def y1(self, value: float) -> None:
        if not self._mut:
            raise TypeError(f'Cannot modify attribute of immutable {self.__class__.__name__} instance')
        self._y1 = value

    @property
    def x2(self) -> float:  # testcheck: ignore
        """Bottom-right X coordinate."""
        return self._x2

    @x2.setter
    def x2(self, value: float) -> None:
        if not self._mut:
            raise TypeError(f'Cannot modify attribute of immutable {self.__class__.__name__} instance')
        self._x2 = value

    @property
    def y2(self) -> float:  # testcheck: ignore
        """Bottom-right Y coordinate."""
        return self._y2

    @y2.setter
    def y2(self, value: float) -> None:
        if not self._mut:
            raise TypeError(f'Cannot modify attribute of immutable {self.__class__.__name__} instance')
        self._y2 = value

    @property
    def mutable(self) -> bool:
        """Whether this instance's attributes can be modified."""
        return self._mut

    def __repr__(self) -> str:  # noqa: D105
        return f'{self.__class__.__name__}(x1={self.x1!r}, y1={self.y1!r}, x2={self.x2!r}, y2={self.y2!r})'

    def __str__(self) -> str:
        """Returns this rectangle in the format ``'(x1, y1, x2, y2)'``."""
        return str(self.as_tuple())

    def __iter__(self) -> Generator[float]:
        """Returns a generator yielding from :meth:`as_tuple`."""
        yield from self.as_tuple()

    def __getitem__(self, idx: int) -> float:
        """Returns the item at ``idx`` as if from a tuple of this rectangle's values.

        .. note::
            A tuple of this rectangle is not actually constructed, a basic ``if`` block is used instead since it's
            faster than making the tuple and accessing it; ``IndexError`` is still raised when out of range.
        """
        if idx == 0:  # noqa: SIM116 ; doing the check like this is faster than tuple or dictionary access
            return self.x1
        elif idx == 1:
            return self.y1
        elif idx == 2:  # noqa: PLR2004
            return self.x2
        elif idx == 3:  # noqa: PLR2004
            return self.y2

        raise IndexError(idx)

    def __hash__(self) -> int:
        """Returns the hash of a :meth:`as_tuple`."""
        return hash(self.as_tuple())

    def __copy__(self, *, mut: bool | None = None) -> Self:
        """Returns a new instance with the same values as this instance, optionally changing its mutability.

        :param mut: Sets the mutability of the copied instance. If ``None``, the current value for the instance being
            copied is used.
        """
        return self.__class__(self.x1, self.y1, self.x2, self.y2, mut=mut if mut is not None else self.mutable)

    def __eq__(self, value: object) -> bool:
        """Compares coordinate values if ``value`` is a tuple or ``Rect`` object, otherwise returns ``False``."""
        if isinstance(value, tuple):
            return self.as_tuple() == value
        if isinstance(value, self.__class__):
            return self.as_tuple() == value.as_tuple()

        return False

    # These are properties since the coordinate attributes could be changed, though I'm reconsidering
    # whether Rects should be mutable at all

    @property
    def area(self) -> float:
        """Total area of this rectangle."""
        return self.width * self.height

    @property
    def bottom_left(self) -> Coord2:
        """Bottom left corner coordinate."""
        return Coord2(self.x1, self.y2)

    @property
    def bottom_right(self) -> Coord2:
        """Bottom right corner coordinate."""
        return Coord2(self.x2, self.y2)

    @property
    def center(self) -> Coord2:
        """Center coordinate of this rectangle."""
        return Coord2(self.x1 + (self.width / 2), self.y1 + (self.height / 2))

    @property
    def corners(self) -> tuple[Coord2, Coord2, Coord2, Coord2]:
        """The four corner coordinates of this rectangle.

        The order is top-left, top-right, bottom-left, bottom-right.
        """
        return (
            self.top_left,
            self.top_right,
            self.bottom_left,
            self.bottom_right,
        )

    @property
    def height(self) -> float:
        """Height of this rectangle."""
        return self.y2 - self.y1

    @property
    def perimeter(self) -> float:
        """Perimeter of this rectangle."""
        return (self.width * 2) + (self.height * 2)

    @property
    def size(self) -> tuple[float, float]:
        """A tuple of the width and height of this rectangle."""
        return (self.width, self.height)

    @property
    def top_left(self) -> Coord2:
        """Top left corner coordinate."""
        return Coord2(self.x1, self.y1)

    @property
    def top_right(self) -> Coord2:
        """Top right corner coordinate."""
        return Coord2(self.x2, self.y1)

    @property
    def width(self) -> float:
        """Width of this rectangle."""
        return self.x2 - self.x1

    @classmethod
    def from_points(cls, points: Iterable[CoordOrTuple2], *, mut: bool = False) -> Self:
        """Returns a new rectangle sized by the minimum and maximum values of a sequence of coordinates."""
        x1: float = math.inf
        y1: float = math.inf
        x2: float = -math.inf
        y2: float = -math.inf

        for (x, y) in points:
            if x < x1:
                x1 = x
            elif x > x2:
                x2 = x
            if y < y1:
                y1 = y
            elif y > y2:
                y2 = y

        return cls(x1, y1, x2, y2, mut=mut)

    @classmethod
    def from_size(cls, size: CoordOrTuple2, center: CoordOrTuple2 | None = None) -> Self:
        """Returns a new rectangle of the given size.

        Created with its top left coordinate at ``0, 0`` by default unless ``center`` is specified, where it will be
        sized out from that coordinate as the origin.
        """
        rad_x, rad_y = size[0] / 2, size[1] / 2
        center_x, center_y = center if center is not None else (rad_x, rad_y)

        return cls(
            center_x - rad_x,
            center_y - rad_y,
            center_x + rad_x,
            center_y + rad_y,
        )

    @overload
    def as_tuple(self, map_fn: None = None) -> Tuple4[float]: ...
    @overload
    def as_tuple[U](self, map_fn: Callable[[float], U]) -> Tuple4[U]: ...
    def as_tuple[U](self, map_fn: Callable[[float], U] | None = None) -> Tuple4[object]:
        """Returns the X1, Y1, X2, and Y2 values as a tuple."""
        if map_fn:
            return (map_fn(self.x1), map_fn(self.y1), map_fn(self.x2), map_fn(self.y2))

        return (self.x1, self.y1, self.x2, self.y2)

    def ceil(self) -> Self:
        """Rounds up the coordinates of this rectangle."""
        return self.__class__(
            math.ceil(self.x1),
            math.ceil(self.y1),
            math.ceil(self.x2),
            math.ceil(self.y2),
        )

    def copy(self, *, mut: bool | None = None) -> Self:
        """Returns a copy of this instance, optionally changing its mutability.

        See :meth:`__copy__`.
        """
        return self.__copy__(mut=mut)

    def floor(self) -> Self:
        """Rounds down the coordinates of this rectangle."""
        return self.__class__(
            math.floor(self.x1),
            math.floor(self.y1),
            math.floor(self.x2),
            math.floor(self.y2),
        )

    def map(self, fn: Callable[[float], float]) -> Self:
        """Returns a new rectangle with ``fn`` applied to all coordinate values."""
        return self.__class__(fn(self.x1), fn(self.y1), fn(self.x2), fn(self.y2))

    def resize(self, xy: CoordOrTuple2, *, from_center: bool = False) -> Self:
        """Returns a new rectangle of this instance's size added to by ``xy``.

        By default, the rectangle is resized from the top-left corner, keeping its coordinate intact and only adding to
        the bottom-right coordinate. If ``from_center`` is ``True``, it will be resized outward in all directions from
        the center coordinate.
        """
        size_x, size_y = xy
        if from_center:
            size_x, size_y = size_x / 2, size_y / 2

        return self.__class__(
            self.x1 - (size_x if from_center else 0),
            self.y1 - (size_y if from_center else 0),
            self.x2 + size_x,
            self.y2 + size_y,
        )

    def round(self, ndigits: int | None = None) -> Self:
        """Rounds the coordinates of this rectangle to a given number of places.

        Values will be converted to ``int`` if ``ndigits`` is ``None``.
        """
        return self.__class__(
            round(self.x1, ndigits),
            round(self.y1, ndigits),
            round(self.x2, ndigits),
            round(self.y2, ndigits),
        )

    def translate_by(self, xy: CoordOrTuple2) -> Self:
        """Returns a new rectangle with this instance's coordinates shifted by ``xy``."""
        tr_x, tr_y = xy

        return self.__class__(self.x1 + tr_x, self.y1 + tr_y, self.x2 + tr_x, self.y2 + tr_y)

    def translate_to(self, xy: CoordOrTuple2) -> Self:
        """Returns a new rectangle with this instance's coordinates shifted such that its top left coordinate
        equals ``xy``.
        """  # noqa: D205
        return self.translate_by(Coord2(*xy) - self.top_left)

    def zip_with(self,
            fn: Callable[[float, float], float],
            other: Self | Tuple4[float] | float,
        ) -> Self:
        """Combines this and another instance or tuple's values using ``fn``.

        The values used are those returned by iterating over the instance—for :class:`Rect`, that would be :data:`x1`,
        :data:`y1`, :data:`x2`, and :data:`y2`.
        """
        if not isinstance(other, Rect | tuple):
            other = (other, other, other, other)

        return self.__class__(
            fn(self.x1, other[0]),
            fn(self.y1, other[1]),
            fn(self.x2, other[2]),
            fn(self.y2, other[3]),
        )

class Grid2(Rect):
    """Represents a 2D grid, with methods for iterating over its steps.

    Subclass of :class:`Rect`.

    Properties :data:`step` and :data:`origin` are immutable by default; initialize the instance with ``mut=True`` to
    allow setting their values. When initialized as immutable, if :class:`Coord2` objects are given for the ``step`` and
    ``origin`` parameters of :meth:`__init__`, they will be copied as immutable.
    """

    def __init__(self,
            x1: float,
            y1: float,
            x2: float,
            y2: float,
            *,
            step: CoordOrTuple2 = (1, 1),
            origin: CoordOrTuple2 | None = None,
            mut: bool = False,
        ) -> None:
        """Initializes a ``Grid2`` instance.

        :param step: Default step used for :meth:`steps_x`, :meth:`steps_y`, and :meth:`steps`.
        :param origin: Default origin used for :meth:`steps_x`, :meth:`steps_y`, and :meth:`steps`.
            If ``None``, the origin is set to the center coordinate of ``rect``.
        :param mut: Whether this instance's attributes can be modified or not. If ``False``, ``TypeError`` is raised
            when attempting to reassign them, and ``step`` and ``origin`` will be made immutable as well.
        """
        super().__init__(x1, y1, x2, y2, mut=mut)

        self._step = step if isinstance(step, Coord2) and mut \
            else Coord2(*step, mut=mut)
        self._origin = origin if isinstance(origin, Coord2) and mut \
            else Coord2(*self.center if origin is None else origin, mut=mut)

    @property
    def step(self) -> Coord2:
        """Default step used for :meth:`steps_x`, :meth:`steps_y`, and :meth:`steps`."""
        return self._step

    @step.setter
    def step(self, value: CoordOrTuple2) -> None:
        if not self._mut:
            raise TypeError(f'Cannot modify attribute of immutable {self.__class__.__name__} instance')
        self._step = value if isinstance(value, Coord2) else Coord2(*value)

    @property
    def origin(self) -> Coord2:
        """Default origin used for :meth:`steps_x`, :meth:`steps_y`, and :meth:`steps`."""
        return self._origin

    @origin.setter
    def origin(self, value: CoordOrTuple2) -> None:
        if not self._mut:
            raise TypeError(f'Cannot modify attribute of immutable {self.__class__.__name__} instance')
        self._origin = value if isinstance(value, Coord2) else Coord2(*value)

    @property
    def mutable(self) -> bool:
        """Whether this instance's attributes can be modified."""
        return self._mut

    def __repr__(self) -> str:  # noqa: D105
        return f'{self.__class__.__name__}(x1={self.x1!r}, y1={self.y1!r}, x2={self.x2!r}, y2={self.y2!r},' \
            + f' step={self.step!r}, origin={self.origin!r})'

    def __str__(self) -> str:
        """Returns this grid in the format ``(x1, y1, x2, y2)[step=str(step), origin=str(origin)]``."""
        return f'{self.as_tuple()}[step={self.step}, origin={self.origin}]'

    def __copy__(self, *, mut: bool | None = None) -> Self:
        """Returns a new instance with the same values as this instance, optionally changing its mutability.

        The resulting copy's ``step`` and ``origin`` are references to this instance's respective objects. Use
        ``Grid2``'s :meth:`__deepcopy__` implementation to ensure these values are copies as well.

        :param mut: Sets the mutability of the copied instance. If ``None``, the current value for the instance being
            copied is used.
        """
        return self.__class__(
            self.x1,
            self.y1,
            self.x2,
            self.y2,
            step=self.step,
            origin=self.origin,
            mut=mut if mut is not None else self.mutable,
        )

    def __deepcopy__(self, memo: dict) -> Self:
        """Returns a new instance with the same values as this instance.

        In contrast to :meth:`__copy__`, a ``Grid2`` deepcopy will also make copies of the ``step`` and ``origin``
        values.
        """
        return self.__class__(
            self.x1,
            self.y1,
            self.x2,
            self.y2,
            step=copy(self.step),
            origin=copy(self.origin),
            mut=self.mutable,
        )

    @classmethod
    @override
    def from_points(cls,
            points: Iterable[CoordOrTuple2],
            *,
            step: CoordOrTuple2 = (1, 1),
            origin: CoordOrTuple2 | None = None,
            mut: bool = False,
        ) -> Self:
        return cls(*super().from_points(points), step=step, origin=origin, mut=mut)

    @classmethod
    @override
    def from_size(cls,
            size: CoordOrTuple2,
            center: CoordOrTuple2 | None = None,
            *,
            step: CoordOrTuple2 | None = None,
            origin: CoordOrTuple2 | None = None,
        ) -> Self:
        """Returns a new grid of the given size.

        Created with its top left coordinate at ``0, 0`` by default unless ``center`` is specified, where it will be
        sized out from that coordinate as the origin of the rectangle. Note that this is separate from ``origin``, which
        has nothing to do with the grid's physical bounds and is be used to set the ``origin`` attribute of the grid
        instance.
        """
        rad_x, rad_y = size[0] / 2, size[1] / 2
        center_x, center_y = center if center is not None else (rad_x, rad_y)

        return cls(
            center_x - rad_x,
            center_y - rad_y,
            center_x + rad_x,
            center_y + rad_y,
            step=step if step is not None else (1, 1),
            origin=origin,
        )

    @override
    def ceil(self,
            *,
            step: CoordOrTuple2 | None = None,
            origin: CoordOrTuple2 | None = None,
        ) -> Self:
        """Rounds up the coordinates of this grid.

        New ``step`` and ``origin`` values can be optionally specified, otherwise the values for this instance are
        used.
        """
        return self.__class__(
            math.ceil(self.x1),
            math.ceil(self.y1),
            math.ceil(self.x2),
            math.ceil(self.y2),
            step=step or self.step,
            origin=origin or self.origin,
        )

    @override
    def copy(self, *, mut: bool | None = None) -> Self:
        """Returns a copy of this instance, optionally changing its mutability.

        See :meth:`__copy__`.
        """
        return self.__copy__(mut=mut)

    @override
    def floor(self,
            *,
            step: CoordOrTuple2 | None = None,
            origin: CoordOrTuple2 | None = None,
        ) -> Self:
        """Rounds down the coordinates of this grid.

        New ``step`` and ``origin`` values can be optionally specified, otherwise the values for this instance are
        used.
        """
        return self.__class__(
            math.floor(self.x1),
            math.floor(self.y1),
            math.floor(self.x2),
            math.floor(self.y2),
            step=step or self.step,
            origin=origin or self.origin,
        )

    @override
    def map(self,
            fn: Callable[[float], float],
            *,
            step: CoordOrTuple2 | None = None,
            origin: CoordOrTuple2 | None = None,
        ) -> Self:
        """Returns a new rectangle with ``fn`` applied to all coordinate values.

        New ``step`` and ``origin`` values can be optionally specified, otherwise the values for this instance are
        used.
        """
        return self.__class__(
            fn(self.x1),
            fn(self.y1),
            fn(self.x2),
            fn(self.y2),
            step=step or self.step,
            origin=origin or self.origin,
        )

    @override
    def resize(self,
            xy: CoordOrTuple2,
            *,
            step: CoordOrTuple2 | None = None,
            origin: CoordOrTuple2 | None = None,
            from_center: bool = False,
        ) -> Self:
        """Returns a new grid of this instance's size added to by ``xy``.

        By default, the grid is resized from the top-left corner, keeping its coordinate intact and only adding to the
        bottom-right coordinate. If ``from_center`` is ``True``, it will be resized outward in all directions from the
        center coordinate.

        New ``step`` and ``origin`` values can be optionally specified, otherwise the values for this instance are used.
        """
        size_x, size_y = xy
        if from_center:
            size_x, size_y = size_x / 2, size_y / 2

        return self.__class__(
            self.x1 - (size_x if from_center else 0),
            self.y1 - (size_y if from_center else 0),
            self.x2 + size_x,
            self.y2 + size_y,
            step=step or self.step,
            origin=origin or self.origin,
        )

    @override
    def round(self,
            ndigits: int | None = None,
            *,
            step: CoordOrTuple2 | None = None,
            origin: CoordOrTuple2 | None = None,
        ) -> Self:
        """Rounds the coordinates of this rectangle to a given number of places.

        Values will be converted to ``int`` if ``ndigits`` is ``None``.

        New ``step`` and ``origin`` values can be optionally specified, otherwise the values for this instance are used.
        """
        return self.__class__(
            round(self.x1, ndigits),
            round(self.y1, ndigits),
            round(self.x2, ndigits),
            round(self.y2, ndigits),
            step=step or self.step,
            origin=origin or self.origin,
        )

    @override
    def translate_by(self,
            xy: CoordOrTuple2,
            *,
            step: CoordOrTuple2 | None = None,
            origin: CoordOrTuple2 | Literal['auto'] | None = 'auto',
        ) -> Self:
        """Returns a new rectangle with this instance's coordinates shifted by ``xy``.

        New ``step`` and ``origin`` values can be optionally specified, otherwise the values for this instance are used.
        ``origin`` may also be ``'auto'`` (default), which will shift the origin point by ``xy``. Setting it to ``None``
        keeps this instance's origin value unchanged.
        """
        tr_x, tr_y = xy

        if origin == 'auto':
            origin = self.origin + xy

        return self.__class__(
            self.x1 + tr_x,
            self.y1 + tr_y,
            self.x2 + tr_x,
            self.y2 + tr_y,
            step=step or self.step,
            origin=origin or self.origin,
        )

    @override
    def translate_to(self,
            xy: CoordOrTuple2,
            *,
            step: CoordOrTuple2 | None = None,
            origin: CoordOrTuple2 | Literal['auto'] | None = 'auto',
        ) -> Self:
        """Returns a new rectangle with this instance's coordinates shifted such that its top left coordinate
        equals ``xy``.

        New ``step`` and ``origin`` values can be optionally specified, otherwise the values for this instance are used.
        ``origin`` may also be ``'auto'`` (default), which will shift the origin point by ``xy``. Setting it to ``None``
        keeps this instance's origin value unchanged.
        """  # noqa: D205
        return self.translate_by(Coord2(*xy) - self.top_left, step=step, origin=origin)

    def steps_x(self, *, step: float | None = None, origin: float | None = None, inf: bool = False) -> Generator[float]:
        """Yields X coordinates starting at ``origin`` and adding ``step`` while in range of the grid.

        .. note::
            Yields no items if the step value is 0, or if ``origin`` is out of bounds.

        :param step: If ``None``, defaults to ``self.step.x``. If this value is 0, no values are yielded.
        :param origin: If ``None``, defaults to ``self.origin.y``.
        :param inf: Whether to continue yielding steps infinitely, beyond the grid's defined boundaries.
        """
        step = step if step is not None else self.step.x
        if step == 0:
            return

        origin = origin if origin is not None else self.origin.x

        pos = origin
        while inf or (self.x1 <= pos <= self.x2):
            yield pos
            pos += step

    def steps_y(self, *, step: float | None = None, origin: float | None = None, inf: bool = False) -> Generator[float]:
        """Yields Y coordinates starting at ``origin`` and adding ``step`` while in range of the grid.

        .. note::
            Yields no items if the step value is 0, or if ``origin`` is out of bounds.

        :param step: If ``None``, defaults to ``self.step.y``. If this value is 0, no values are yielded.
        :param origin: If ``None``, defaults to ``self.origin.y``.
        :param inf: Whether to continue yielding steps infinitely, beyond the grid's defined boundaries.
        """
        step = step if step is not None else self.step.y
        if step == 0:
            return

        origin = origin if origin is not None else self.origin.y

        pos = origin
        while inf or (self.y1 <= pos <= self.y2):
            yield pos
            pos += step

    def steps(self,
            *,
            step: CoordOrTuple2 | None = None,
            origin: CoordOrTuple2 | None = None,
        ) -> Generator[Coord2]:
        """Yields coordinates from the product of :meth:`steps_x` and :meth:`steps_y`.

        Coordinates are yielded going vertically first, e.g. ``(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2), ...``.

        .. note::
            Yields no items if both values of ``step`` are 0, or if ``origin`` is out of bounds.

        :param step: If ``None``, defaults to ``self.step``.
        :param origin: If ``None``, defaults to ``self.origin``.
        """
        step = step if step is not None else self.step
        step = step if isinstance(step, Coord2) else Coord2(*step)
        if step == (0, 0):
            return

        origin = origin if origin is not None else self.origin
        origin = origin if isinstance(origin, Coord2) else Coord2(*origin)

        steps_x = self.steps_x(origin=origin.x, step=step.x) if step.x else (0,)
        steps_y = self.steps_y(origin=origin.y, step=step.y) if step.y else (0,)

        yield from (Coord2(x, y) for x, y in product(steps_x, steps_y))

    def project(self, coord: CoordOrTuple2, other_grid: 'Grid2') -> Coord2:
        """Returns a :class:`Coord2` as if it were at the same relative position on another grid as this one.

        >>> g1 = Grid2(-100, -100, 100, 100)
        >>> g2 = Grid2(0, 0, 100, 100)
        >>> assert g1.project(Coord2(0, 0), g2) == Coord2(50, 50)
        """
        coord = coord if isinstance(coord, Coord2) else Coord2(*coord)

        tl_a, br_a = self.top_left, self.bottom_right
        tl_b, br_b = other_grid.top_left, other_grid.bottom_right

        offset_factor: Coord2 = (coord - tl_a) / (br_a - tl_a)

        return ((br_b - tl_b) * offset_factor) + tl_b

    @override
    def zip_with(self,
            fn: Callable[[float, float], float],
            other: Rect | Tuple4[float] | float,
            *,
            step: CoordOrTuple2 | None = None,
            origin: CoordOrTuple2 | None = None,
        ) -> Self:
        """Combines this and another instance or tuple's values using ``fn``.

        The values used are those returned by iterating over the instance—for :class:`Grid2`, that would be :data:`x1`,
        :data:`y1`, :data:`x2`, and :data:`y2`.

        :param step: What to set :data:`step` to for the returned instance. If ``None``, this instance's value is used.
        :param origin: What to set :data:`origin` to for the returned instance.
            If ``None``, this instance's value is used.
        """
        if not isinstance(other, Rect | tuple):
            other = (other, other, other, other)

        step = self.step if step is None else step
        origin = self.origin if origin is None else origin

        return self.__class__(
            fn(self.x1, other[0]),
            fn(self.y1, other[1]),
            fn(self.x2, other[2]),
            fn(self.y2, other[3]),
            step=step,
            origin=origin,
        )

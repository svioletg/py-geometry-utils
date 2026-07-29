"""Utilities for working with coordinates and rectangles/grids."""
import math
import operator
from collections.abc import Callable, Generator
from copy import copy
from itertools import product
from typing import Literal, Self, overload

from geometry.util import snap_num

__version__ = '0.2.0'

type BinaryOp[T, U] = Callable[[T, T], U]
type CoordOrTuple2 = Coord2 | tuple[float, float]
type RectOrTuple = Rect | tuple[float, float, float, float]

class Coord2:
    """Represents a 2D coordinate."""

    x: float
    y: float

    def __init__(self, x: float, y: float) -> None:
        if not isinstance(x, int | float):
            raise TypeError(f"{self.__class__.__name__}.__init__() parameter 'x' must be 'int' or 'float': {x!r}")
        if not isinstance(y, int | float):
            raise TypeError(f"{self.__class__.__name__}.__init__() parameter 'y' must be 'int' or 'float': {y!r}")

        self.x = x
        self.y = y

    def __repr__(self) -> str:  # noqa: D105
        return f'{self.__class__.__name__}(x={self.x}, y={self.y})'

    def __str__(self) -> str:
        """Returns this coordinate in the format ``(x, y)``."""
        return f'({self.x}, {self.y})'

    def __bool__(self) -> bool:
        """Returns ``False`` if both X and Y values equal 0, otherwise returns ``True``."""
        return not (self.x == self.y == 0)

    def __iter__(self) -> Generator[float]:
        """Yields the X and Y values of this coordinate."""
        yield from self.as_tuple()

    def __getitem__(self, idx: int) -> float:
        """Returns the item at ``idx`` from a tuple of this coordinate's values."""
        return self.as_tuple()[idx]

    def __hash__(self) -> int:
        """Returns the hash of a tuple of this coordinate's values."""
        return hash(self.as_tuple())

    def __copy__(self) -> Self:
        """Returns a new instance with the same values as this instance."""
        return self.__class__(self.x, self.y)

    def __eq__(self, value: object) -> bool:
        """Compares the X and Y values of two coordinates, returns ``False`` for other objects."""
        if isinstance(value, tuple):
            return self.as_tuple() == value
        if isinstance(value, self.__class__):
            return self.as_tuple() == value.as_tuple()

        return False

    def __ge__(self, value: Self | tuple[float, float]) -> bool:
        """Compares the X and Y values of two coordinates, returns ``False`` for other objects."""
        if isinstance(value, Coord2 | tuple):
            return (self.x >= value[0]) and (self.y >= value[1])

        return NotImplemented

    def __gt__(self, value: Self | tuple[float, float]) -> bool:
        """Compares the X and Y values of two coordinates, returns ``False`` for other objects."""
        if isinstance(value, Coord2 | tuple):
            return (self.x > value[0]) and (self.y > value[1])

        return NotImplemented

    def __le__(self, value: Self | tuple[float, float]) -> bool:
        """Compares the X and Y values of two coordinates, returns ``False`` for other objects."""
        if isinstance(value, Coord2 | tuple):
            return (self.x <= value[0]) and (self.y <= value[1])

        return NotImplemented

    def __lt__(self, value: Self | tuple[float, float]) -> bool:
        """Compares the X and Y values of two coordinates, returns ``False`` for other objects."""
        if isinstance(value, Coord2 | tuple):
            return (self.x < value[0]) and (self.y < value[1])

        return NotImplemented

    def __add__(self, other: Self | tuple[float, float] | float) -> Self:
        """Returns a new coordinate with this and another coordinate's X and Y values added together.

        If given a single value, it is added to the X and Y values of this coordinate.

        >>> assert Coord2(1, 2) + Coord2(1, 2) == Coord2(2, 4)
        >>> assert Coord2(1, 2) + (1, 2) == Coord2(2, 4)
        >>> assert Coord2(1, 2) + 1 == Coord2(2, 3)
        """
        return self.binop(operator.add, other)

    def __sub__(self, other: Self | tuple[float, float] | float) -> Self:
        """Returns a new coordinate with this and another coordinate's X and Y values subtracted from eachother.

        If given a single value, it is subtracted from the X and Y values of this coordinate.

        >>> assert Coord2(1, 2) - Coord2(1, 2) == Coord2(0, 0)
        >>> assert Coord2(1, 2) - (1, 2) == Coord2(0, 0)
        >>> assert Coord2(1, 2) - 1 == Coord2(0, 1)
        """
        return self.binop(operator.sub, other)

    def __mul__(self, other: Self | tuple[float, float] | float) -> Self:
        """Returns a new coordinate with this and another coordinate's X and Y multiplied together.

        If given a single value, the X and Y values of this coordinate are multiplied by it.

        >>> assert Coord2(1, 2) * Coord2(2, 4) == Coord2(2, 8)
        >>> assert Coord2(1, 2) * (2, 4) == Coord2(2, 8)
        >>> assert Coord2(1, 2) * 2 == Coord2(2, 4)
        """
        return self.binop(operator.mul, other)

    def __truediv__(self, other: Self | tuple[float, float] | float) -> Self:
        """Returns a new coordinate with this and another coordinate's X and Y divided by eachother.

        If given a single value, the X and Y values of this coordinate are divided by it.

        >>> assert Coord2(1, 2) / Coord2(2, 8) == Coord2(0.5, 0.25)
        >>> assert Coord2(1, 2) / (2, 8) == Coord2(0.5, 0.25)
        >>> assert Coord2(1, 2) / 2 == Coord2(0.5, 1.0)
        """
        other = (other, other) if isinstance(other, int | float) else other

        return self.binop(operator.truediv, other)

    def __floordiv__(self, other: Self | tuple[float, float] | float) -> Self:
        """Returns a new coordinate with this and another coordinate's X and Y values divided by eachother and floored.

        If given a single value, the X and Y values of this coordinate are divided by it and floored.

        >>> assert Coord2(1, 2) // Coord2(2, 8) == Coord2(0, 0)
        >>> assert Coord2(1, 2) // (2, 8) == Coord2(0, 0)
        >>> assert Coord2(1, 2) // 2 == Coord2(0, 1)
        """
        return self.binop(operator.floordiv, other)

    def __mod__(self, other: Self | tuple[float, float] | float) -> Self:
        """Returns a new coordinate with this and another coordinate's X and Y values added together.

        If given a single value, it is added to the X and Y values of this coordinate.

        >>> assert Coord2(1, 2) % Coord2(2, 8) == Coord2(1, 2)
        >>> assert Coord2(1, 2) % (2, 8) == Coord2(1, 2)
        >>> assert Coord2(1, 2) % 2 == Coord2(1, 0)
        """
        return self.binop(operator.mod, other)

    def __pow__(self, other: Self | tuple[float, float] | float) -> Self:
        """Returns a new coordinate with this and another coordinate's X and Y values added together.

        If given a single value, it is added to the X and Y values of this coordinate.

        >>> assert Coord2(1, 2) ** Coord2(2, 4) == Coord2(1, 16)
        >>> assert Coord2(1, 2) ** (2, 4) == Coord2(1, 16)
        >>> assert Coord2(1, 2) ** 2 == Coord2(1, 4)
        """
        return self.binop(operator.pow, other)

    @overload
    def as_tuple(self, map_fn: None = None) -> tuple[float, float]: ...
    @overload
    def as_tuple[U](self, map_fn: Callable[[float], U]) -> tuple[U, U]: ...
    def as_tuple[U](self, map_fn: Callable[[float], U] | None = None) -> tuple[object, object]:
        """Returns the coordinate as a tuple, optionally mapping the values."""
        if map_fn:
            return (map_fn(self.x), map_fn(self.y))

        return (self.x, self.y)

    def binop(self, op: BinaryOp[float, float], other: Self | tuple[float, float] | float) -> Self:
        """Calls a binary function using this coordinate's values and another's, returning a new ``Coord2`` instance.

        This is equivalent to ``Coord2(op(self.x, other[0]), op(self.y, other[1]))``. If a single number value is given
        for ``other``, it is turned into a two-tuple of itself, i.e. ``(other, other)``.
        """
        if not isinstance(other, Coord2 | tuple):
            other = (other, other)

        return self.__class__(op(self.x, other[0]), op(self.y, other[1]))

    def distance(self, other: CoordOrTuple2, mode: Literal['euclid', 'taxi'] = 'taxi') -> float:
        """Returns the euclidean or taxicab distance from this coordinate to ``other`` based on ``mode``.

        :param mode: ``'euclid'`` will return the euclidean distance from ``self`` to ``other``, ``'taxi'`` returns the
            taxicab distance.
        """
        match mode:
            case 'euclid':
                return math.sqrt(((self[0] - other[0]) ** 2) + ((self[1] - other[1]) ** 2))
            case 'taxi':
                return sum((self - other).as_tuple(abs))
            case _:
                raise ValueError(f'Unexpected mode: {mode!r}')

    def format(self, s: str) -> str:
        """Returns ``s`` formatted with this coordinate's ``x`` and ``y`` values."""
        return s.format(x=self.x, y=self.y)

    def in_bounds(self, rect: RectOrTuple, *, edge_ok: bool = True) -> bool:
        """Returns whether this coordinate is within a rectangle's bounds, not counting the edge.

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

    def map(self, fn: Callable[[float], float]) -> Self:
        """Returns a new instance of this class with ``fn`` applied to its ``x`` and ``y`` attributes."""
        return self.__class__(fn(self.x), fn(self.y))

    def on_edge(self, rect: RectOrTuple) -> bool:
        """Returns whether this coordinate sits on the edge of a rectangle."""
        return ((rect[0] <= self.x <= rect[2]) and (self.y in (rect[1], rect[3]))) \
            or ((rect[1] <= self.y <= rect[3]) and (self.x in (rect[0], rect[2])))

    def snap_to_grid(self, grid: 'Grid2', snap_fn: Callable[[float], int] = round) -> Self:
        """Returns a new instance whose X and Y values have been aligned to ``grid``.

        Snapping is done based on ``grid``'s ``step`` and ``origin`` values.

        :param snap_fn: Refer to :func:`geometry.util.snap_num`.
        """
        return self.__class__(
            snap_num(self.x - grid.origin.x, grid.step.x, snap_fn) + grid.origin.x,
            snap_num(self.y - grid.origin.y, grid.step.y, snap_fn) + grid.origin.y,
        )

class Rect:
    """Represents a rectangle using its top-left and bottom-right coordinates."""

    x1: float
    """Top-left X coordinate."""
    y1: float
    """Top-left Y coordinate."""
    x2: float
    """Bottom-right X coordinate."""
    y2: float
    """Bottom-right Y coordinate."""

    def __init__(self, x1: float, y1: float, x2: float, y2: float) -> None:
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

    def __repr__(self) -> str:  # noqa: D105
        return f'{self.__class__.__name__}(x1={self.x1!r}, y1={self.y1!r}, x2={self.x2!r}, y2={self.y2!r})'

    def __str__(self) -> str:
        """Returns this rectangle in the format ``'(x1, y1, x2, y2)'``."""
        return str(self.as_tuple())

    def __iter__(self) -> Generator[float]:
        """Returns a generator yielding from :py:meth:`as_tuple`."""
        yield from self.as_tuple()

    def __getitem__(self, idx: int) -> float:
        """Returns the item at ``idx`` from :py:meth:`as_tuple`."""
        return self.as_tuple()[idx]

    def __hash__(self) -> int:
        """Returns the hash of a :py:meth:`as_tuple`."""
        return hash(self.as_tuple())

    def __copy__(self) -> Self:
        """Returns a new instance with the same values as this instance."""
        return self.__class__(self.x1, self.y1, self.x2, self.y2)

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
    def as_tuple(self, map_fn: None = None) -> tuple[float, float, float, float]: ...
    @overload
    def as_tuple[U](self, map_fn: Callable[[float], U]) -> tuple[U, U, U, U]: ...
    def as_tuple[U](self, map_fn: Callable[[float], U] | None = None) -> tuple[object, object, object, object]:
        """Returns the X1, Y1, X2, and Y2 values as a tuple."""
        if map_fn:
            return (map_fn(self.x1), map_fn(self.y1), map_fn(self.x2), map_fn(self.y2))

        return (self.x1, self.y1, self.x2, self.y2)

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

    def translate_by(self, xy: CoordOrTuple2) -> Self:
        """Returns a new rectangle with this instance's coordinates shifted by ``xy``."""
        tr_x, tr_y = xy

        return self.__class__(self.x1 + tr_x, self.y1 + tr_y, self.x2 + tr_x, self.y2 + tr_y)

    def translate_to(self, xy: CoordOrTuple2) -> Self:
        """Returns a new rectangle with this instance's coordinates shifted such that its top left coordinate
        equals ``xy``.
        """  # noqa: D205
        return self.translate_by(Coord2(*xy) - self.top_left)

class Grid2(Rect):
    """Represents a 2D grid, with methods for iterating over steps."""

    step: Coord2
    """Default step used for :py:meth:`steps_x`, :py:meth:`steps_y`, and :py:meth:`steps`."""
    origin: Coord2
    """Default origin used for :py:meth:`steps_x`, :py:meth:`steps_y`, and :py:meth:`steps`."""

    def __init__(self,
            x1: float,
            y1: float,
            x2: float,
            y2: float,
            *,
            step: CoordOrTuple2 = (1, 1),
            origin: CoordOrTuple2 | None = None,
        ) -> None:
        """Initializes a ``Grid2`` instance.

        :param step: Default step used for :py:meth:`steps_x`, :py:meth:`steps_y`, and :py:meth:`steps`.
        :param origin: Default origin used for :py:meth:`steps_x`, :py:meth:`steps_y`, and :py:meth:`steps`.
            If ``None``, the origin is set to the center coordinate of ``rect``.
            If this coordinate is not within the bounds of ``rect``, ``ValueError`` is raised.
        """
        super().__init__(x1, y1, x2, y2)

        self.step = step if isinstance(step, Coord2) else Coord2(*step)
        self.origin = origin if isinstance(origin, Coord2) else Coord2(*self.center if origin is None else origin)
        if not self.origin.in_bounds(self):
            raise ValueError(
                f"{self.__class__.__name__} origin coordinate {origin} is outside the grid's bounds: {self}",
            )

    def __repr__(self) -> str:  # noqa: D105
        return f'{self.__class__.__name__}(x1={self.x1!r}, y1={self.y1!r}, x2={self.x2!r}, y2={self.y2!r},' \
            + f' step={self.step!r}, origin={self.origin!r})'

    def __str__(self) -> str:  # noqa: D105
        return f'{self.__class__.__name__}({', '.join(map(str, self))})'

    def __copy__(self) -> Self:
        """Returns a new instance with the same values as this instance.

        The resulting copy's ``step`` and ``origin`` are references to this instance's respective objects. Use
        ``Grid2``'s :meth:`__deepcopy__` implementation to ensure these values are copies as well.
        """
        return self.__class__(
            self.x1,
            self.y1,
            self.x2,
            self.y2,
            step=self.step,
            origin=self.origin,
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
        )

    def steps_x(self, *, step: float | None = None, origin: float | None = None, inf: bool = False) -> Generator[float]:
        """Yields X coordinates starting at ``origin`` and adding ``step`` while in range of the grid.

        .. note::
            Yields no items if the step value is 0.

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
            Yields no items if the step value is 0.

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
        """Yields coordinates from the product of :py:meth:`steps_x` and :py:meth:`steps_y`.

        Coordinates are yielded going vertically first, e.g. ``(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2), ...``.

        .. note::
            Yields no items if either step value is 0.

        :param step: If ``None``, defaults to ``self.step``. If this value is equal to ``(0, 0)``, no values are
            yielded.
        :param origin: If ``None``, defaults to ``self.origin``.
        """
        step = step if step is not None else self.step
        step = step if isinstance(step, Coord2) else Coord2(*step)
        if step == (0, 0):
            return

        origin = origin if origin is not None else self.origin
        origin = origin if isinstance(origin, Coord2) else Coord2(*origin)

        steps_x = self.steps_x(origin=origin.x, step=step.x)
        steps_y = self.steps_y(origin=origin.y, step=step.y)

        yield from (Coord2(x, y) for x, y in product(steps_x, steps_y))

    def project(self, coord: CoordOrTuple2, other_grid: 'Grid2') -> Coord2:
        """Returns a :py:class:`Coord2` as if it were at the same relative position on another grid as this one.

        >>> g1 = Grid2(-100, -100, 100, 100)
        >>> g2 = Grid2(0, 0, 100, 100)
        >>> assert g1.project(Coord2(0, 0), g2) == Coord2(50, 50)
        """
        coord = coord if isinstance(coord, Coord2) else Coord2(*coord)

        tl_a, br_a = self.top_left, self.bottom_right
        tl_b, br_b = other_grid.top_left, other_grid.bottom_right

        offset_factor: Coord2 = (coord - tl_a) / (br_a - tl_a)

        return ((br_b - tl_b) * offset_factor) + tl_b

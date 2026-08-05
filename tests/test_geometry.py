import math
import operator
from copy import copy, deepcopy

import pytest

from geometry import Coord2, Grid2, Rect, Tuple2
from geometry.util import take_n
from tests import assert_all, assert_attrs, assert_yields


def double(n: float) -> float:
    return n * 2

def test_coord2_mag_init() -> None:
    assert_attrs(Coord2(1, 2), x=1, y=2)

    mut_inst = Coord2(1, 2, mut=True)
    assert mut_inst.mutable
    mut_inst.x = 2
    assert mut_inst.x == 2  # noqa: PLR2004
    mut_inst.y = 2
    assert mut_inst.y == 2  # noqa: PLR2004

    inst = Coord2(1, 2)
    assert not inst.mutable
    with pytest.raises(TypeError, match='Cannot modify attribute of immutable Coord2 instance'):
        inst.x = 2
    with pytest.raises(TypeError, match='Cannot modify attribute of immutable Coord2 instance'):
        inst.y = 2

def test_coord2_mutable() -> None:
    assert not Coord2(1, 2).mutable
    assert not Coord2(1, 2, mut=False).mutable
    assert Coord2(1, 2, mut=True).mutable

def test_coord2_mag_repr() -> None:
    assert repr(Coord2(1, 2)) == 'Coord2(x=1, y=2)'

def test_coord2_mag_str() -> None:
    assert str(Coord2(1, 2)) == '(1, 2)'

def test_coord2_mag_bool() -> None:
    assert Coord2(0, 0)
    assert Coord2(0, 1)
    assert Coord2(1, 0)
    assert Coord2(1, 1)

def test_coord2_mag_iter() -> None:
    assert list(Coord2(1, 2)) == [1, 2]

def test_coord2_mag_getitem() -> None:
    inst = Coord2(1, 2)
    assert inst[0] == 1
    assert inst[1] == 2  # noqa: PLR2004

def test_coord2_mag_hash() -> None:
    assert hash(Coord2(1, 2)) == hash(Coord2(1, 2))

def test_coord2_mag_eq() -> None:
    assert Coord2(1, 2) == Coord2(1, 2) == (1, 2)
    assert Coord2(1, 2) != Coord2(1, 0)
    assert Coord2(1, 2) != (1, 0)

def test_coord2_priv_compare() -> None:
    assert Coord2(1, 2)._compare(operator.ge, Coord2(0, 0))  # noqa: SLF001

@pytest.mark.parametrize(('left', 'right', 'expected'),
    params := [
        ((1, 1), (0, 0), True),
        ((1, 1), (0, 1), True),
        ((1, 1), (1, 0), True),
        ((1, 1), (1, 1), True),
        ((1, 1), (1, 2), False),
        ((1, 1), (2, 1), False),
        ((1, 1), (2, 2), False),
    ],
    ids=['-'.join(str(p) for p in pset) for pset in params],
)
def test_coord2_mag_ge(left: Tuple2[float], right: Tuple2[float], expected: bool) -> None:
    assert (left >= right) is expected
    assert (Coord2(*left) >= right) is expected
    assert (left >= Coord2(*right)) is expected
    assert (Coord2(*left) >= Coord2(*right)) is expected

@pytest.mark.parametrize(('left', 'right', 'expected'),
    params := [
        ((1, 1), (0, 0), True),
        ((1, 1), (0, 1), True),
        ((1, 1), (1, 0), True),
        ((1, 1), (1, 1), False),
        ((1, 1), (1, 2), False),
        ((1, 1), (2, 1), False),
        ((1, 1), (2, 2), False),
    ],
    ids=['-'.join(str(p) for p in pset) for pset in params],
)
def test_coord2_mag_gt(left: Tuple2[float], right: Tuple2[float], expected: bool) -> None:
    assert (left > right) is expected
    assert (Coord2(*left) > right) is expected
    assert (left > Coord2(*right)) is expected
    assert (Coord2(*left) > Coord2(*right)) is expected

@pytest.mark.parametrize(('left', 'right', 'expected'),
    params := [
        ((1, 1), (2, 2), True),
        ((1, 1), (2, 1), True),
        ((1, 1), (1, 2), True),
        ((1, 1), (1, 1), True),
        ((1, 1), (1, 0), False),
        ((1, 1), (0, 1), False),
        ((1, 1), (0, 0), False),
    ],
    ids=['-'.join(str(p) for p in pset) for pset in params],
)
def test_coord2_mag_le(left: Tuple2[float], right: Tuple2[float], expected: bool) -> None:
    assert (left <= right) is expected
    assert (Coord2(*left) <= right) is expected
    assert (left <= Coord2(*right)) is expected
    assert (Coord2(*left) <= Coord2(*right)) is expected

@pytest.mark.parametrize(('left', 'right', 'expected'),
    params := [
        ((1, 1), (2, 2), True),
        ((1, 1), (2, 1), True),
        ((1, 1), (1, 2), True),
        ((1, 1), (1, 1), False),
        ((1, 1), (1, 0), False),
        ((1, 1), (0, 1), False),
        ((1, 1), (0, 0), False),
    ],
    ids=['-'.join(str(p) for p in pset) for pset in params],
)
def test_coord2_mag_lt(left: Tuple2[float], right: Tuple2[float], expected: bool) -> None:
    assert (left < right) is expected
    assert (Coord2(*left) < right) is expected
    assert (left < Coord2(*right)) is expected
    assert (Coord2(*left) < Coord2(*right)) is expected

def test_coord2_mag_add() -> None:
    assert Coord2(1, 2) + Coord2(3, 4) == Coord2(4, 6)
    assert Coord2(1, 2) + (3, 4) == Coord2(4, 6)  # noqa: RUF005
    assert Coord2(1, 2) + 2 == Coord2(3, 4)

    with pytest.raises(TypeError, match=r"(unsupported operand|must be 'int' or 'float')"):
        Coord2(1, 2) + '2'  # ty:ignore[unsupported-operator]

def test_coord2_mag_sub() -> None:
    assert Coord2(3, 4) - Coord2(1, 2) == Coord2(2, 2)
    assert Coord2(3, 4) - (1, 2) == Coord2(2, 2)
    assert Coord2(3, 4) - 2 == Coord2(1, 2)

    with pytest.raises(TypeError, match=r"(unsupported operand|must be 'int' or 'float')"):
        Coord2(3, 4) - '2'  # ty:ignore[unsupported-operator]

def test_coord2_mag_mul() -> None:
    assert Coord2(1, 2) * Coord2(3, 4) == Coord2(3, 8)
    assert Coord2(1, 2) * (3, 4) == Coord2(3, 8)
    assert Coord2(1, 2) * 2 == Coord2(2, 4)

    with pytest.raises(TypeError, match=r"(unsupported operand|must be 'int' or 'float')"):
        Coord2(1, 2) * '2'  # ty:ignore[unsupported-operator]

def test_coord2_mag_truediv() -> None:
    assert Coord2(3, 4) / Coord2(1, 2) == Coord2(3, 2)
    assert Coord2(3, 4) / (1, 2) == Coord2(3, 2)
    assert Coord2(3, 4) / 2 == Coord2(1.5, 2)

    with pytest.raises(TypeError, match=r"(unsupported operand|must be 'int' or 'float')"):
        Coord2(3, 4) / '2'  # ty:ignore[unsupported-operator]

def test_coord2_mag_floordiv() -> None:
    assert Coord2(3, 4) // Coord2(1, 2) == Coord2(3, 2)
    assert Coord2(3, 4) // (1, 2) == Coord2(3, 2)
    assert Coord2(3, 4) // 2 == Coord2(1, 2)

    with pytest.raises(TypeError, match=r"(unsupported operand|must be 'int' or 'float')"):
        Coord2(3, 4) // '2'  # ty:ignore[unsupported-operator]

def test_coord2_mag_mod() -> None:
    assert Coord2(3.5, 4.25) % Coord2(2, 3) == Coord2(1.5, 1.25)
    assert Coord2(3.5, 4.25) % (2, 3) == Coord2(1.5, 1.25)
    assert Coord2(3.5, 4.25) % 2 == Coord2(1.5, 0.25)

    with pytest.raises(TypeError, match=r"(unsupported operand|must be 'int' or 'float')"):
        Coord2(3.5, 4.25) % '2'  # ty:ignore[unsupported-operator]

def test_coord2_mag_pow() -> None:
    assert Coord2(1, 2) ** Coord2(3, 4) == Coord2(1, 16)
    assert Coord2(1, 2) ** (3, 4) == Coord2(1, 16)
    assert Coord2(1, 2) ** 2 == Coord2(1, 4)

    with pytest.raises(TypeError, match=r"(unsupported operand|must be 'int' or 'float')"):
        Coord2(1, 2) ** '2'  # ty:ignore[unsupported-operator]

def test_coord2_mag_copy() -> None:
    inst = Coord2(1, 2)
    copied = copy(inst)

    assert copied is not inst
    assert copied == inst

def test_coord2_as_tuple() -> None:
    assert Coord2(1.0, 2.0).as_tuple() == (1.0, 2.0)
    assert Coord2(1.0, 2.0).as_tuple(int) == (1, 2)
    assert Coord2(1.0, 2.0).as_tuple(str) == ('1.0', '2.0')

@pytest.mark.parametrize(('a', 'b', 'chebyshev', 'euclid', 'taxi'),
    params := [
        ((0, 0), (0, 0), 0, 0, 0),
        ((0, 0), (0, 1), 1, 1, 1),
        ((0, 0), (1, 0), 1, 1, 1),
        ((0, 0), (1, 1), 1, 1.41, 2),
        ((0, 0), (1, 2), 2, 2.24, 3),
        ((0, 0), (2, 1), 2, 2.24, 3),
        ((0, 0), (2, 2), 2, 2.83, 4),
    ],
    ids=['-'.join(str(p) for p in pset) for pset in params],
)
def test_coord2_distance(a: Tuple2[float], b: Tuple2[float], chebyshev: float, euclid: float, taxi: float) -> None:
    assert round(Coord2(*a).distance(Coord2(*b), 'chebyshev'), 2) == chebyshev
    assert round(Coord2(*a).distance(b, 'chebyshev'), 2) == chebyshev
    assert round(Coord2(*a).distance(Coord2(*b), 'euclid'), 2) == euclid
    assert round(Coord2(*a).distance(b, 'euclid'), 2) == euclid
    assert round(Coord2(*a).distance(Coord2(*b), 'taxi'), 2) == taxi
    assert round(Coord2(*a).distance(b, 'taxi'), 2) == taxi

    assert round(Coord2(*b).distance(Coord2(*a), 'chebyshev'), 2) == chebyshev
    assert round(Coord2(*b).distance(a, 'chebyshev'), 2) == chebyshev
    assert round(Coord2(*b).distance(Coord2(*a), 'euclid'), 2) == euclid
    assert round(Coord2(*b).distance(a, 'euclid'), 2) == euclid
    assert round(Coord2(*b).distance(Coord2(*a), 'taxi'), 2) == taxi
    assert round(Coord2(*b).distance(a, 'taxi'), 2) == taxi

def test_coord2_format() -> None:
    assert Coord2(1, 2).format('{x},{y}') == '1,2'
    assert Coord2(1.125, 2.5).format('{x:.2f},{y:.2f}') == '1.12,2.50'

def test_coord2_in_bounds() -> None:
    # If it works with Rect() and tuple() each once then we dont need to keep checking that
    assert Coord2(1, 1).in_bounds(Rect(0, 0, 2, 2))
    assert Coord2(1, 1).in_bounds((0, 0, 2, 2))
    assert Coord2(0, 0).in_bounds((0, 0, 2, 2))
    assert not Coord2(0, 0).in_bounds((0, 0, 2, 2), edge_ok=False)
    assert Coord2(0, 0).in_bounds((0, 0, 2, 2))
    assert not Coord2(0, 0).in_bounds((0, 0, 2, 2), edge_ok=False)
    assert Coord2(2, 2).in_bounds((0, 0, 2, 2))
    assert not Coord2(2, 2).in_bounds((0, 0, 2, 2), edge_ok=False)
    assert not Coord2(-1, -1).in_bounds((0, 0, 2, 2))
    assert not Coord2(3, 3).in_bounds((0, 0, 2, 2))

def test_coord2_lerp() -> None:
    assert Coord2(0, 0).lerp(Coord2(1, 1), 0) == Coord2(0, 0)
    assert Coord2(0, 0).lerp(Coord2(1, 1), 1) == Coord2(1, 1)
    assert Coord2(0, 0).lerp(Coord2(1, 1), 0.5) == Coord2(0.5, 0.5)
    assert Coord2(0, 0).lerp(Coord2(-1, -1), 0.5) == Coord2(-0.5, -0.5)
    assert Coord2(1, 2).lerp(Coord2(2, 4), 0) == Coord2(1, 2)
    assert Coord2(1, 2).lerp(Coord2(2, 4), 1) == Coord2(2, 4)
    assert Coord2(1, 2).lerp(Coord2(2, 4), 0.5) == Coord2(1.5, 3.0)
    assert Coord2(-1, -2).lerp(Coord2(-2, -4), 0.5) == Coord2(-1.5, -3.0)

def test_coord2_lerp_iter() -> None:
    assert_yields(Coord2(0, 0).lerp_iter(Coord2(0, 0)), [(0, 0)] * 11)
    assert_yields(Coord2(0, 0).lerp_iter(Coord2(1, 1), step=2), [(0, 0)])

    assert_yields(
        (c.map(lambda n: round(n, 1)) for c in Coord2(0, 0).lerp_iter(Coord2(1, 1), 0.1)),
        [
            (0, 0),
            (0.1, 0.1),
            (0.2, 0.2),
            (0.3, 0.3),
            (0.4, 0.4),
            (0.5, 0.5),
            (0.6, 0.6),
            (0.7, 0.7),
            (0.8, 0.8),
            (0.9, 0.9),
            (1, 1),
        ],
    )
    assert_yields(
        (c.map(lambda n: round(n, 1)) for c in Coord2(0, 0).lerp_iter(Coord2(1, 1), 0.1, start=0.5)),
        [
            (0.5, 0.5),
            (0.6, 0.6),
            (0.7, 0.7),
            (0.8, 0.8),
            (0.9, 0.9),
            (1, 1),
        ],
    )
    assert_yields(
        (c.map(lambda n: round(n, 1)) for c in Coord2(0, 0).lerp_iter(Coord2(1, 1), 0.1, end=0.5)),
        [
            (0, 0),
            (0.1, 0.1),
            (0.2, 0.2),
            (0.3, 0.3),
            (0.4, 0.4),
            (0.5, 0.5),
        ],
    )

    assert_yields(
        (c.map(lambda n: round(n, 1)) for c in Coord2(0, 0).lerp_iter(Coord2(1, 1), -0.1, start=1, end=0)),
        [
            (1, 1),
            (0.9, 0.9),
            (0.8, 0.8),
            (0.7, 0.7),
            (0.6, 0.6),
            (0.5, 0.5),
            (0.4, 0.4),
            (0.3, 0.3),
            (0.2, 0.2),
            (0.1, 0.1),
            (0, 0),
        ],
    )
    assert_yields(
        (c.map(lambda n: round(n, 1)) for c in Coord2(0, 0).lerp_iter(Coord2(1, 1), -0.1, start=0.5, end=0)),
        [
            (0.5, 0.5),
            (0.4, 0.4),
            (0.3, 0.3),
            (0.2, 0.2),
            (0.1, 0.1),
            (0, 0),
        ],
    )
    assert_yields(
        (c.map(lambda n: round(n, 1)) for c in Coord2(0, 0).lerp_iter(Coord2(1, 1), -0.1, start=1, end=0.5)),
        [
            (1, 1),
            (0.9, 0.9),
            (0.8, 0.8),
            (0.7, 0.7),
            (0.6, 0.6),
            (0.5, 0.5),
        ],
    )

def test_coord2_map() -> None:
    assert Coord2(1, 2).map(double) == Coord2(2, 4)

def test_coord2_on_edge() -> None:
    assert Coord2(0, 0).on_edge((0, 0, 2, 2))
    assert Coord2(1, 0).on_edge((0, 0, 2, 2))
    assert Coord2(2, 0).on_edge((0, 0, 2, 2))
    assert Coord2(0, 1).on_edge((0, 0, 2, 2))
    assert not Coord2(1, 1).on_edge((0, 0, 2, 2))
    assert Coord2(2, 1).on_edge((0, 0, 2, 2))
    assert Coord2(0, 2).on_edge((0, 0, 2, 2))
    assert Coord2(1, 2).on_edge((0, 0, 2, 2))
    assert Coord2(2, 2).on_edge((0, 0, 2, 2))

def test_coord2_snap_to_grid() -> None:
    g = Grid2(-100, -100, 100, 100, step=(10, 10))
    assert Coord2(25, 25).snap_to_grid(g) == Coord2(20, 20)
    assert Coord2(25, 25).snap_to_grid(g, math.ceil) == Coord2(30, 30)
    assert Coord2(25, 25).snap_to_grid(g, math.floor) == Coord2(20, 20)

    assert Coord2(-25, -25).snap_to_grid(g) == Coord2(-20, -20)
    assert Coord2(-25, -25).snap_to_grid(g, math.ceil) == Coord2(-20, -20)
    assert Coord2(-25, -25).snap_to_grid(g, math.floor) == Coord2(-30, -30)

    # Make sure snapping takes the origin into account
    g = Grid2(-108, -103, 89, 92, step=(10, 10), origin=(5, 5))
    assert Coord2(23, 23).snap_to_grid(g) == Coord2(25, 25)
    assert Coord2(23, 23).snap_to_grid(g, math.ceil) == Coord2(25, 25)
    assert Coord2(23, 23).snap_to_grid(g, math.floor) == Coord2(15, 15)

    assert Coord2(-23, -23).snap_to_grid(g) == Coord2(-25, -25)
    assert Coord2(-23, -23).snap_to_grid(g, math.ceil) == Coord2(-15, -15)
    assert Coord2(-23, -23).snap_to_grid(g, math.floor) == Coord2(-25, -25)

    assert Coord2(4, 6).snap_to_grid(Grid2(-100, -100, 100, 100, step=(0, 0))) == Coord2(0, 0)
    assert Coord2(6, 6).snap_to_grid(Grid2(-100, -100, 100, 100, step=(0, 0))) == Coord2(0, 0)
    assert Coord2(6, 4).snap_to_grid(Grid2(-100, -100, 100, 100, step=(0, 0))) == Coord2(0, 0)

    assert Coord2(4, 6).snap_to_grid(Grid2(-100, -100, 100, 100, step=(10, 0))) == Coord2(0, 0)
    assert Coord2(6, 6).snap_to_grid(Grid2(-100, -100, 100, 100, step=(10, 0))) == Coord2(10, 0)
    assert Coord2(6, 4).snap_to_grid(Grid2(-100, -100, 100, 100, step=(10, 0))) == Coord2(10, 0)

    assert Coord2(4, 6).snap_to_grid(Grid2(-100, -100, 100, 100, step=(0, 10))) == Coord2(0, 10)
    assert Coord2(6, 6).snap_to_grid(Grid2(-100, -100, 100, 100, step=(0, 10))) == Coord2(0, 10)
    assert Coord2(6, 4).snap_to_grid(Grid2(-100, -100, 100, 100, step=(0, 10))) == Coord2(0, 0)

def test_coord2_zip_with() -> None:
    assert Coord2(1, 2).zip_with(max, Coord2(0, 4)) == Coord2(1, 4)
    assert Coord2(1, 2).zip_with(max, (0, 4)) == Coord2(1, 4)
    assert Coord2(1, 2).zip_with(operator.add, 10) == Coord2(11, 12)

def test_rect_mag_init() -> None:
    rect_attrs = {'x1': 1, 'y1': 2, 'x2': 3, 'y2': 4}

    assert_attrs(Rect(**rect_attrs), **rect_attrs)  # ty:ignore[invalid-argument-type]

    mut_inst = Rect(0, 1, 2, 3, mut=True)
    assert mut_inst.mutable
    mut_inst.x1 = 1
    assert mut_inst.x1 == 1
    mut_inst.y1 = 2
    assert mut_inst.y1 == 2  # noqa: PLR2004
    mut_inst.x2 = 3
    assert mut_inst.x2 == 3  # noqa: PLR2004
    mut_inst.y2 = 4
    assert mut_inst.y2 == 4  # noqa: PLR2004

    inst = Rect(0, 1, 2, 3)
    assert not inst.mutable
    with pytest.raises(TypeError, match='Cannot modify attribute of immutable Rect instance'):
        inst.x1 = 2
    with pytest.raises(TypeError, match='Cannot modify attribute of immutable Rect instance'):
        inst.y1 = 2
    with pytest.raises(TypeError, match='Cannot modify attribute of immutable Rect instance'):
        inst.x2 = 2
    with pytest.raises(TypeError, match='Cannot modify attribute of immutable Rect instance'):
        inst.y2 = 2

def test_rect_mutable() -> None:
    assert not Rect(0, 1, 2, 3).mutable
    assert not Rect(0, 1, 2, 3, mut=False).mutable
    assert Rect(0, 1, 2, 3, mut=True).mutable

def test_rect_mag_repr() -> None:
    assert repr(Rect(0, 0, 2, 2)) == 'Rect(x1=0, y1=0, x2=2, y2=2)'

def test_rect_mag_str() -> None:
    assert str(Rect(0, 0, 2, 2)) == '(0, 0, 2, 2)'

def test_rect_mag_iter() -> None:
    assert list(Rect(0, 0, 2, 2)) == [0, 0, 2, 2]

def test_rect_mag_getitem() -> None:
    inst = Rect(0, 0, 2, 2)
    assert inst[0] == 0
    assert inst[1] == 0
    assert inst[2] == 2  # noqa: PLR2004
    assert inst[3] == 2  # noqa: PLR2004

def test_rect_mag_hash() -> None:
    assert hash(Rect(0, 0, 2, 2)) == hash(Rect(0, 0, 2, 2))

def test_rect_mag_eq() -> None:
    assert Rect(0, 0, 2, 2) == Rect(0, 0, 2, 2) == (0, 0, 2, 2)

def test_rect_mag_copy() -> None:
    inst = Rect(0, 1, 2, 3)
    copied = copy(inst)

    assert copied is not inst
    assert copied == inst

def test_rect_area() -> None:
    assert Rect(0, 0, 2, 2).area == 4  # noqa: PLR2004

def test_rect_bottom_left() -> None:
    assert Rect(0, 0, 2, 2).bottom_left == Coord2(0, 2)

def test_rect_bottom_right() -> None:
    assert Rect(0, 0, 2, 2).bottom_right == Coord2(2, 2)

def test_rect_center() -> None:
    assert Rect(0, 0, 2, 2).center == Coord2(1, 1)

def test_rect_corners() -> None:
    assert Rect(0, 0, 2, 2).corners == (
        Coord2(0, 0),
        Coord2(2, 0),
        Coord2(0, 2),
        Coord2(2, 2),
    )

def test_rect_height() -> None:
    assert Rect(0, 0, 2, 2).height == 2  # noqa: PLR2004

def test_rect_perimeter() -> None:
    assert Rect(0, 0, 2, 2).perimeter == 8  # noqa: PLR2004

def test_rect_size() -> None:
    assert Rect(0, 0, 2, 2).size == (2, 2)

def test_rect_top_left() -> None:
    assert Rect(0, 0, 2, 2).top_left == Coord2(0, 0)

def test_rect_top_right() -> None:
    assert Rect(0, 0, 2, 2).top_right == Coord2(2, 0)

def test_rect_width() -> None:
    assert Rect(0, 0, 2, 2).height == 2  # noqa: PLR2004

def test_rect_from_size() -> None:
    assert Rect.from_size((100, 100), center=None) == Rect(0, 0, 100, 100)
    assert Rect.from_size((50, 100), center=None) == Rect(0, 0, 50, 100)
    assert Rect.from_size((100, 100), center=(50, 50)) == Rect(0, 0, 100, 100)
    assert Rect.from_size((50, 100), center=(50, 50)) == Rect(25, 0, 75, 100)

def test_rect_as_tuple() -> None:
    assert Rect(0, 0, 2, 2).as_tuple() == (0, 0, 2, 2)
    assert Rect(0.5, 0.5, 2.5, 2.5).as_tuple(int) == (0, 0, 2, 2)
    assert Rect(0, 0, 2, 2).as_tuple(str) == ('0', '0', '2', '2')

def test_rect_map() -> None:
    assert Rect(0.5, 0.5, 2.5, 2.5).map(math.ceil) == Rect(1, 1, 3, 3)
    assert Rect(0.5, 0.5, 2.5, 2.5).map(math.floor) == Rect(0, 0, 2, 2)

def test_rect_resize() -> None:
    assert Rect(0, 0, 2, 2).resize((2, 2)) == Rect(0, 0, 4, 4)
    assert Rect(0, 0, 2, 2).resize((2, 2), from_center=True) == Rect(-1, -1, 3, 3)

def test_rect_translate_by() -> None:
    assert Rect(2, 2, 4, 4).translate_by((2, 2)) == Rect(4, 4, 6, 6)
    assert Rect(2, 2, 4, 4).translate_by((2, 2)).size == Rect(2, 2, 4, 4).size
    assert Rect(2, 2, 4, 4).translate_by((1, 2)) == Rect(3, 4, 5, 6)
    assert Rect(2, 2, 4, 4).translate_by((2, 2)).size == Rect(2, 2, 4, 4).size

def test_rect_translate_to() -> None:
    assert Rect(0, 0, 2, 2).translate_to((2, 2)) == Rect(2, 2, 4, 4)
    assert Rect(0, 0, 2, 2).translate_to((2, 2)).size == Rect(0, 0, 2, 2).size
    assert Rect(0, 0, 2, 2).translate_to((1, 2)) == Rect(1, 2, 3, 4)
    assert Rect(0, 0, 2, 2).translate_to((2, 2)).size == Rect(0, 0, 2, 2).size

def test_rect_zip_with() -> None:
    assert Rect(0, 0, 2, 2).zip_with(max, Rect(-2, -2, 4, 4)) == Rect(0, 0, 4, 4)
    assert Rect(0, 0, 2, 2).zip_with(max, (-2, -2, 4, 4)) == Rect(0, 0, 4, 4)
    assert Rect(0, 0, 2, 2).zip_with(operator.add, 10) == Rect(10, 10, 12, 12)

def test_grid2_mag_init() -> None:
    inst = Grid2(-1 ,-1, 1, 1)
    assert inst.as_tuple() == Rect(-1, -1, 1, 1)
    assert inst.step == Coord2(1, 1)
    assert inst.origin == Coord2(0, 0)

    inst = Grid2(-1 ,-1, 1, 1, step=(1, 2), origin=(1, 1))
    assert inst.step == Coord2(1, 2)
    assert inst.origin == Coord2(1, 1)

    mut_inst = Grid2(-1, -1, 1, 1, mut=True)
    assert mut_inst.mutable
    mut_inst.step = Coord2(2, 2)
    assert mut_inst.step == Coord2(2, 2)
    mut_inst.origin = Coord2(2, 2)
    assert mut_inst.origin == Coord2(2, 2)

    inst = Grid2(-1, -1, 1, 1)
    assert not inst.mutable
    with pytest.raises(TypeError, match='Cannot modify attribute of immutable Grid2 instance'):
        inst.step = Coord2(2, 2)
    with pytest.raises(TypeError, match='Cannot modify attribute of immutable Grid2 instance'):
        inst.origin = Coord2(2, 2)

    # Assert that Coord2 argument values are copied when mut is False
    mut_inst = Grid2(-1, -1, 1, 1, step=(step := Coord2(2, 2)), origin=(origin := Coord2(1, 1)), mut=True)
    assert mut_inst.step is step
    assert mut_inst.origin is origin

    inst = Grid2(-1, -1, 1, 1, step=(step := Coord2(2, 2)), origin=(origin := Coord2(1, 1)))
    assert inst.step is not step
    assert inst.origin is not origin

def test_grid2_mutable() -> None:
    inst = Grid2(0, 1, 2, 3)
    assert not inst.mutable
    assert not inst.step.mutable
    assert not inst.origin.mutable

    assert Grid2(0, 1, 2, 3, mut=True).mutable

def test_grid2_mag_repr() -> None:
    assert repr(Grid2(-1 ,-1, 1, 1)) == 'Grid2(x1=-1, y1=-1, x2=1, y2=1,' \
        + ' step=Coord2(x=1, y=1), origin=Coord2(x=0.0, y=0.0))'

def test_grid2_mag_str() -> None:
    assert str(Grid2(-1 ,-1, 1, 1, step=(2, 2), origin=(-1, -1))) == '(-1, -1, 1, 1)[step=(2, 2), origin=(-1, -1)]'

def test_grid2_mag_copy() -> None:
    inst = Grid2(0, 1, 2, 3, step=(4, 5), origin=(1, 2))
    copied = copy(inst)

    assert copied is not inst
    assert copied == inst
    assert copied.step == inst.step
    assert copied.step is not inst.step
    assert copied.origin == inst.origin
    assert copied.origin is not inst.origin

    must_inst = Grid2(0, 1, 2, 3, step=(4, 5), origin=(1, 2), mut=True)
    copied = copy(must_inst)

    assert copied is not must_inst
    assert copied == must_inst
    assert copied.step == must_inst.step
    assert copied.step is must_inst.step
    assert copied.origin == must_inst.origin
    assert copied.origin is must_inst.origin

def test_grid2_mag_deepcopy() -> None:
    inst = Grid2(0, 1, 2, 3, step=(4, 5), origin=(1, 2))
    copied = deepcopy(inst)

    assert copied is not inst
    assert copied == inst
    assert copied.step == inst.step
    assert copied.step is not inst.step
    assert copied.origin == inst.origin
    assert copied.origin is not inst.origin

    must_inst = Grid2(0, 1, 2, 3, step=(4, 5), origin=(1, 2), mut=True)
    copied = deepcopy(must_inst)

    assert copied is not must_inst
    assert copied == must_inst
    assert copied.step == must_inst.step
    assert copied.step is not must_inst.step
    assert copied.origin == must_inst.origin
    assert copied.origin is not must_inst.origin

def test_grid2_step() -> None:
    grid = Grid2(0, 0, 10, 10, step=(1, 1))
    assert isinstance(grid.step, Coord2)
    assert grid.step == Coord2(1, 1)

    grid = Grid2(0, 0, 10, 10, step=(1, 1), mut=True)
    grid.step = (2, 2)
    assert isinstance(grid.step, Coord2)
    assert grid.step == Coord2(2, 2)

def test_grid2_origin() -> None:
    grid = Grid2(0, 0, 10, 10, origin=(1, 1))
    assert isinstance(grid.origin, Coord2)
    assert grid.origin == Coord2(1, 1)

    grid = Grid2(0, 0, 10, 10, origin=(1, 1), mut=True)
    grid.origin = (2, 2)
    assert isinstance(grid.origin, Coord2)
    assert grid.origin == Coord2(2, 2)

def test_grid2_from_size() -> None:
    inst = Grid2.from_size((100, 100))
    assert inst.step == Coord2(1, 1)
    assert inst.origin == Coord2(50, 50)

    inst = Grid2.from_size((100, 100), step=(10, 10))
    assert inst.step == Coord2(10, 10)

    inst = Grid2.from_size((100, 100), center=(0, 0))
    assert inst.origin == Coord2(0, 0)

    inst = Grid2.from_size((100, 100), center=(0, 0), origin=(-50, -50))
    assert inst.origin == Coord2(-50, -50)

def test_grid2_steps_x() -> None:
    grid = Grid2(0, 1, 2, 3, origin=(0, 1))
    steps = list(grid.steps_x())
    assert all(grid.x1 <= x <= grid.x2 for x in steps)
    assert steps == [0, 1, 2]

    assert take_n(grid.steps_x(inf=True), 10) == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

    assert list(Grid2(0, 0, 2, 2, origin=(0, 0), step=(0, 0)).steps_x()) == []
    assert list(Grid2(0, 0, 2, 2, origin=(0, 0), step=(1, 0)).steps_x()) == [0, 1, 2]

    assert list(Grid2(0, 0, 2, 2, origin=(10, 10)).steps_x()) == []

def test_grid2_steps_y() -> None:
    grid = Grid2(0, 1, 2, 3, origin=(0, 1))
    steps = list(grid.steps_y())
    assert all(grid.y1 <= y <= grid.y2 for y in steps)
    assert steps == [1, 2, 3]

    assert take_n(grid.steps_y(inf=True), 10) == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    assert list(Grid2(0, 0, 2, 2, origin=(0, 0), step=(0, 0)).steps_y()) == []
    assert list(Grid2(0, 0, 2, 2, origin=(0, 0), step=(0, 1)).steps_y()) == [0, 1, 2]

    assert list(Grid2(0, 0, 2, 2, origin=(10, 10)).steps_y()) == []

def test_grid2_steps() -> None:
    grid = Grid2(0, 1, 2, 3, origin=(0, 1))
    steps = list(grid.steps())
    assert_all(lambda xy: xy.in_bounds(grid), steps)
    assert steps == [
        Coord2(0, 1),
        Coord2(0, 2),
        Coord2(0, 3),
        Coord2(1, 1),
        Coord2(1, 2),
        Coord2(1, 3),
        Coord2(2, 1),
        Coord2(2, 2),
        Coord2(2, 3),
    ]

    assert list(Grid2(0, 0, 2, 2, origin=(0, 0), step=(0, 0)).steps()) == []
    assert list(Grid2(0, 0, 2, 2, origin=(0, 0), step=(1, 0)).steps()) == [
        Coord2(0, 0),
        Coord2(1, 0),
        Coord2(2, 0),
    ]
    assert list(Grid2(0, 0, 2, 2, origin=(0, 0), step=(0, 1)).steps()) == [
        Coord2(0, 0),
        Coord2(0, 1),
        Coord2(0, 2),
    ]

    assert list(Grid2(0, 0, 2, 2, origin=(10, 10)).steps()) == []

def test_grid2_project() -> None:
    assert Grid2(-100, -100, 100, 100).project(Coord2(0, 0), Grid2(0, 0, 100, 100)) == Coord2(50, 50)
    assert Grid2(-100, -100, 100, 100).project(Coord2(-50, -50), Grid2(0, 0, 100, 100)) == Coord2(25, 25)
    assert Grid2(-100, -100, 100, 100).project(Coord2(0, 50), Grid2(0, 0, 100, 100)) == Coord2(50, 75)
    assert Grid2(-100, -100, 100, 100).project(Coord2(0, 0), Grid2(0, 0, 100, 200)) == Coord2(50, 100)

def test_grid2_zip_with() -> None:
    assert Grid2(0, 0, 2, 2).zip_with(max, Grid2(-2, -2, 4, 4)) == Grid2(0, 0, 4, 4)
    assert Grid2(0, 0, 2, 2).zip_with(max, (-2, -2, 4, 4)) == Grid2(0, 0, 4, 4)
    assert Grid2(0, 0, 2, 2).zip_with(operator.add, 10) == Grid2(10, 10, 12, 12)

    inst = Grid2(0, 0, 2, 2, step=(5, 5), origin=(0, 0)).zip_with(max, Grid2(-2, -2, 4, 4))
    assert inst.step == Coord2(5, 5)
    assert inst.origin == Coord2(0, 0)

    inst = Grid2(0, 0, 2, 2, step=(5, 5), origin=(0, 0)).zip_with(operator.add, 10)
    assert inst.step == Coord2(5, 5)
    assert inst.origin == Coord2(0, 0)

    inst = Grid2(0, 0, 2, 2, step=(5, 5), origin=(0, 0)).zip_with(max, Grid2(-2, -2, 4, 4), step=(10, 10))
    assert inst.step == Coord2(10, 10)
    assert inst.origin == Coord2(0, 0)

    inst = Grid2(0, 0, 2, 2, step=(5, 5), origin=(0, 0)).zip_with(operator.add, 10, step=(10, 10))
    assert inst.step == Coord2(10, 10)
    assert inst.origin == Coord2(0, 0)

    inst = Grid2(0, 0, 2, 2, step=(5, 5), origin=(0, 0)).zip_with(max, Grid2(-2, -2, 4, 4), origin=(4, 4))
    assert inst.step == Coord2(5, 5)
    assert inst.origin == Coord2(4, 4)

    inst = Grid2(0, 0, 2, 2, step=(5, 5), origin=(0, 0)).zip_with(operator.add, 10, origin=(10, 10))
    assert inst.step == Coord2(5, 5)
    assert inst.origin == Coord2(10, 10)

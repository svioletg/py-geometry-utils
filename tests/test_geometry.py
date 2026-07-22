import math

import pytest

from geometry import Coord2, Grid2, Rect
from tests import assert_all, assert_attrs


def double(n: float) -> float:
    return n * 2

def test_coord2_mag_init() -> None:
    assert_attrs(Coord2(1, 2), x=1, y=2)

def test_coord2_mag_repr() -> None:
    assert repr(Coord2(1, 2)) == 'Coord2(x=1, y=2)'

def test_coord2_mag_bool() -> None:
    assert Coord2(0, 1)
    assert Coord2(1, 0)
    assert Coord2(1, 1)
    assert not Coord2(0, 0)

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

def test_coord2_mag_ge() -> None:
    assert Coord2(1, 1) >= Coord2(1, 1)
    assert Coord2(1, 1) >= (1, 1)
    assert Coord2(1, 1) >= Coord2(1, 0)
    assert Coord2(1, 1) >= (1, 0)
    assert Coord2(1, 1) >= Coord2(0, 1)
    assert Coord2(1, 1) >= (0, 1)
    assert Coord2(1, 1) >= Coord2(0, 0)
    assert Coord2(1, 1) >= (0, 0)
    assert not Coord2(1, 1) >= Coord2(2, 2)
    assert not Coord2(1, 1) >= (2, 2)
    assert not Coord2(1, 1) >= Coord2(2, 1)
    assert not Coord2(1, 1) >= (2, 1)
    assert not Coord2(1, 1) >= Coord2(1, 2)
    assert not Coord2(1, 1) >= (1, 2)

def test_coord2_mag_gt() -> None:
    assert Coord2(1, 1) > Coord2(0, 0)
    assert Coord2(1, 1) > (0, 0)
    assert not Coord2(1, 1) > Coord2(1, 1)
    assert not Coord2(1, 1) > (1, 1)
    assert not Coord2(1, 1) > Coord2(1, 0)
    assert not Coord2(1, 1) > (1, 0)
    assert not Coord2(1, 1) > Coord2(0, 1)
    assert not Coord2(1, 1) > (0, 1)

def test_coord2_mag_le() -> None:
    assert Coord2(1, 1) <= Coord2(1, 1)
    assert Coord2(1, 1) <= (1, 1)
    assert Coord2(1, 0) <= Coord2(1, 1)
    assert Coord2(1, 0) <= (1, 1)
    assert Coord2(0, 1) <= Coord2(1, 1)
    assert Coord2(0, 1) <= (1, 1)
    assert Coord2(0, 0) <= Coord2(1, 1)
    assert Coord2(0, 0) <= (1, 1)
    assert not Coord2(2, 2) <= Coord2(1, 1)
    assert not Coord2(2, 2) <= (1, 1)
    assert not Coord2(2, 1) <= Coord2(1, 1)
    assert not Coord2(2, 1) <= (1, 1)
    assert not Coord2(1, 2) <= Coord2(1, 1)
    assert not Coord2(1, 2) <= (1, 1)

def test_coord2_mag_lt() -> None:
    assert Coord2(0, 0) < Coord2(1, 1)
    assert Coord2(0, 0) < (1, 1)
    assert not Coord2(1, 1) < Coord2(1, 1)
    assert not Coord2(1, 1) < (1, 1)
    assert not Coord2(1, 0) < Coord2(1, 1)
    assert not Coord2(1, 0) < (1, 1)
    assert not Coord2(0, 1) < Coord2(1, 1)
    assert not Coord2(0, 1) < (1, 1)

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

def test_coord2_mag_pow() -> None: #[tests: ]
    assert Coord2(1, 2) ** Coord2(3, 4) == Coord2(1, 16)
    assert Coord2(1, 2) ** (3, 4) == Coord2(1, 16)
    assert Coord2(1, 2) ** 2 == Coord2(1, 4)

    with pytest.raises(TypeError, match=r"(unsupported operand|must be 'int' or 'float')"):
        Coord2(1, 2) ** '2'  # ty:ignore[unsupported-operator]

def test_coord2_as_tuple() -> None:
    assert Coord2(1.0, 2.0).as_tuple() == (1.0, 2.0)
    assert Coord2(1.0, 2.0).as_tuple(int) == (1, 2)
    assert Coord2(1.0, 2.0).as_tuple(str) == ('1.0', '2.0')

def test_coord2_binop() -> None:
    assert Coord2(1, 2).binop(max, Coord2(0, 4)) == Coord2(1, 4)

def test_coord2_distance() -> None:
    a, b = Coord2(1, 2), Coord2(5, 10)
    assert a.distance(b, 'taxi') == b.distance(a, 'taxi') == 12  # noqa: PLR2004
    assert round(a.distance(b, 'euclid'), 4) == round(b.distance(a, 'euclid'), 4) == 8.9443  # noqa: PLR2004

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

def test_rect_mag_init() -> None:
    rect_attrs = {'x1': 1, 'y1': 2, 'x2': 3, 'y2': 4}

    assert_attrs(Rect(**rect_attrs), **rect_attrs)

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

def test_rect_area() -> None:
    assert Rect(0, 0, 2, 2).area == 4  # noqa: PLR2004

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

def test_grid2_mag_init() -> None:
    inst = Grid2((-1 ,-1, 1, 1))
    assert inst.rect == Rect(-1 ,-1, 1, 1)
    assert inst.step == Coord2(1, 1)
    assert inst.origin == Coord2(0, 0)

    inst = Grid2((-1 ,-1, 1, 1), step=(1, 2), origin=(1, 1))
    assert inst.step == Coord2(1, 2)
    assert inst.origin == Coord2(1, 1)

def test_grid2_mag_repr() -> None:
    assert repr(Grid2((-1 ,-1, 1, 1))) == 'Grid2(rect=Rect(x1=-1, y1=-1, x2=1, y2=1),' \
        + ' step=Coord2(x=1, y=1), origin=Coord2(x=0.0, y=0.0))'

def test_grid2_mag_str() -> None:
    assert str(Grid2((-1 ,-1, 1, 1))) == 'Grid2(-1, -1, 1, 1)'

def test_grid2_steps_x() -> None:
    grid = Grid2((0, 1, 2, 3), origin=(0, 1))
    steps = list(grid.steps_x())
    assert all(grid.rect.x1 <= x <= grid.rect.x2 for x in steps)
    assert steps == [0, 1, 2]

def test_grid2_steps_y() -> None:
    grid = Grid2((0, 1, 2, 3), origin=(0, 1))
    steps = list(grid.steps_y())
    assert all(grid.rect.y1 <= y <= grid.rect.y2 for y in steps)
    assert steps == [1, 2, 3]

def test_grid2_steps() -> None:
    grid = Grid2((0, 1, 2, 3), origin=(0, 1))
    steps = list(grid.steps())
    assert_all(lambda xy: xy.in_bounds(grid.rect), steps)
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

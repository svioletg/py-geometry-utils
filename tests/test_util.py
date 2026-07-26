import math

import pytest

from geometry.util import ident, snap_num, take_n


def test_ident() -> None:
    assert ident(0) == 0
    inst = [1, 2, 3]
    assert ident(inst) is inst

def test_snap_num() -> None:
    assert snap_num(6, 10, round) == 10  # noqa: PLR2004
    assert snap_num(6, 10, math.ceil) == 10  # noqa: PLR2004
    assert snap_num(6, 10, math.floor) == 0

def test_take_n() -> None:
    assert take_n((i for i in range(100)), 10) == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

    with pytest.raises(StopIteration):
        take_n((i for i in range(5)), 10, strict=True)

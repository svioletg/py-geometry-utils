import math

import pytest

from geometry.util import ident, lerp, partition, snap_num, take_n


def test_ident() -> None:
    assert ident(0) == 0
    inst = [1, 2, 3]
    assert ident(inst) is inst

def test_snap_num() -> None:
    assert snap_num(6, 10, round) == 10  # noqa: PLR2004
    assert snap_num(6, 10, math.ceil) == 10  # noqa: PLR2004
    assert snap_num(6, 10, math.floor) == 0

def test_lerp() -> None:
    assert lerp(0, 1, 0) == 0
    assert lerp(0, 1, 1) == 1
    assert lerp(0, 1, 0.5) == 0.5  # noqa: PLR2004
    assert lerp(0, -1, 0.5) == -0.5  # noqa: PLR2004
    assert lerp(1, 3, 0) == 1
    assert lerp(1, 3, 2) == 5  # noqa: PLR2004
    assert lerp(1, 3, 0.5) == 2  # noqa: PLR2004
    assert lerp(-1, -3, 0.5) == -2  # noqa: PLR2004

def test_partition() -> None:
    assert partition(range(10), lambda x: x % 2 == 0) == ([0, 2, 4, 6, 8], [1, 3, 5, 7, 9])

def test_take_n() -> None:
    assert take_n((i for i in range(100)), 10) == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

    with pytest.raises(StopIteration):
        take_n((i for i in range(5)), 10, strict=True)

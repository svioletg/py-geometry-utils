import math

from geometry.util import ident, snap_num


def test_ident() -> None:
    assert ident(0) == 0
    inst = [1, 2, 3]
    assert ident(inst) is inst

def test_snap_num() -> None:
    assert snap_num(6, 10, round) == 10  # noqa: PLR2004
    assert snap_num(6, 10, math.ceil) == 10  # noqa: PLR2004
    assert snap_num(6, 10, math.floor) == 0





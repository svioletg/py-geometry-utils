"""General utilities for ``geometry``."""
from collections.abc import Callable


def ident[T](value: T) -> T:
    """Returns the passed value."""
    return value

def snap_num(num: float, mult: int, snap_fn: Callable[[float], int]) -> int:
    """Snaps ``num`` to the smallest or largest (depending on the outcome of ``snap_fn``) multiple of ``mult``.

    :param snap_num: The function to apply to the result of ``num / mult`` which should produce an integer.
    """
    return mult * (snap_fn(num / mult))

"""General utilities for ``geometry``."""
from collections.abc import Callable, Iterator


def ident[T](value: T) -> T:
    """Returns the passed value."""
    return value

def snap_num(num: float, mult: float, snap_fn: Callable[[float], int] = round) -> float:
    """Snaps ``num`` to the smallest or largest (depending on the outcome of ``snap_fn``) multiple of ``mult``.

    :param snap_num: The function to apply to the result of ``num / mult`` which should produce an integer.
    """
    return mult * (snap_fn(num / mult))

def take_n[T](it: Iterator[T], n: int, *, strict: bool = False) -> list[T]:
    """Returns ``n`` items yielded from ``it``.

    :param strict: If ``False``, ``n`` is treated as a maximum and less items than it may be returned if ``it`` runs out
        before reaching ``n``. If ``True``, ``StopIteration`` is raised in this scenario.

    :raises StopIteration:
        There are less than ``n`` items in ``it``, and ``strict`` is ``True``.
    """
    if not strict:
        return [i for _, i in zip(range(n), it, strict=False)]

    items: list[T] = []
    for _ in range(n):
        items.append(next(it))  # noqa: PERF401 ; we want this to propagate StopIteration

    return items

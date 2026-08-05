import operator
from collections.abc import Callable, Generator, Iterable
from typing import Any


def assert_attrs(inst: object, **attrs) -> None:
    """Asserts ``inst.k == v`` for ``k``, ``v`` in ``attrs``."""
    for k, v in attrs.items():
        assert (got := getattr(inst, k, v)), f'{k} == {got!r} (expected: {v!r})'

def assert_all[T](predicate: Callable[[T], bool], items: Iterable[T], *, fail_fast: bool = True) -> None:
    """Asserts that ``predicate(i)`` returns ``True`` for every ``i`` in ``items``.

    This differs from ``assert all(...)`` in that it will automatically report which item(s) failed the predicate.

    :param fail_fast: Whether to immediately raise ``AssertionError`` when an item fails the predicate.
        If ``False``, all ``AssertionError``s are caught and merged together into one message after checking every item.
    """
    failed: list[Any] = []

    for i in items:
        try:
            assert predicate(i), f'predicate failed: {i}'
        except AssertionError:
            if fail_fast:
                raise
            failed.append(i)

    if failed:
        raise AssertionError('predicate failed: ' + ', '.join(map(repr, failed)))

def assert_yields[T](it: Generator[T], expected: Iterable[T], eq: Callable[[T, T], bool] = operator.eq) -> None:
    """Asserts that ``it`` yields the items from ``expected`` and yields them in the same order.

    Fails on the first item that doesn't match.

    :param eq: The function to use to check if the two items are equal. Defaults to the `==` operator.
    """
    suffix: str = '' if eq is operator.eq else f'eq={eq!r}'

    for n, (a, b) in enumerate(zip(it, expected, strict=True)):
        assert eq(a, b), f'Item {n}: expected {b!r}, got {a!r} ({suffix})'

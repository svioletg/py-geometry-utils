from collections.abc import Callable, Iterable
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

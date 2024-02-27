from datetime import datetime
from typing import Any, Callable, Iterable, List, TypeVar, overload

from formula10.database.model.db_race import DbRace
from formula10 import db
from formula10.domain.model.race import Race

_T = TypeVar("_T")


def any_is_none(*args: Any) -> bool:
    for arg in args:
        if arg is None:
            return True

    return False


def positions_are_contiguous(positions: List[str]) -> bool:
    if len(positions) == 0:
        return True

    positions_unique = set(positions)  # Remove duplicates
    positions_sorted: List[int] = sorted([int(position) for position in positions_unique])

    # [2, 3, 4, 5]: 2 + 3 == 5
    return positions_sorted[0] + len(positions_sorted) - 1 == positions_sorted[-1]

@overload
def race_has_started(*, race: Race) -> bool:
    return race_has_started(race=race)

@overload
def race_has_started(*, race_name: str) -> bool:
    return race_has_started(race_name=race_name)

def race_has_started(*, race: Race | None = None, race_name: str | None = None) -> bool:
    if race is None and race_name is not None:
        _race: DbRace | None = db.session.query(DbRace).filter_by(name=race_name).first()

        if _race is None:
            raise Exception(f"Couldn't obtain race {race_name} to check date")

        return datetime.now() > _race.date

    if race is not None and race_name is None:
        return datetime.now() > race.date

    raise Exception("race_has_started received illegal arguments")


def find_first_else_none(predicate: Callable[[_T], bool], iterable: Iterable[_T]) -> _T | None:
    """
    Finds the first element in a sequence matching a predicate.
    Returns None if no element is found.
    """
    return next(filter(predicate, iterable), None)


def find_multiple(predicate: Callable[[_T], bool], iterable: Iterable[_T]) -> List[_T]:
    filtered = list(filter(predicate, iterable))

    return filtered


def find_multiple_strict(predicate: Callable[[_T], bool], iterable: Iterable[_T], count: int = 0) -> List[_T]:
    """
    Finds <count> elements in a sequence matching a predicate (finds all if <count> is 0).
    Throws exception if more/fewer elements were found than specified.
    """
    filtered = list(filter(predicate, iterable))

    if count != 0 and len(filtered) != count:
        raise Exception(f"find_multiple found {len(filtered)} matching elements but expected {count}")

    return filtered


def find_single_strict(predicate: Callable[[_T], bool], iterable: Iterable[_T]) -> _T:
    """
    Find a single element in a sequence matching a predicate.
    Throws exception if more/less than a single element is found.
    """
    filtered = list(filter(predicate, iterable))

    if len(filtered) != 1:
        raise Exception(f"find_single found {len(filtered)} matching elements but expected 1")

    return filtered[0]


def find_single_or_none_strict(predicate: Callable[[_T], bool], iterable: Iterable[_T]) -> _T | None:
    """
    Find a single element in a sequence matching a predicate if it exists.
    Only throws exception if more than a single element is found.
    """
    filtered = list(filter(predicate, iterable))

    if len(filtered) > 1:
        raise Exception(f"find_single_or_none found {len(list(filtered))} matching elements but expected 0 or 1")

    return filtered[0] if len(filtered) == 1 else None
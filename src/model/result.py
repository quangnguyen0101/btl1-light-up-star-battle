"""Result contract shared by every search algorithm.

Layer 1 -- what an algorithm returns
------------------------------------
``solution``       ``list[list[int]]``   coordinates ``[row, col]``, 0-based;
                                         ``[]`` when the puzzle was not solved
``state``          ``tuple[int, ...] | None``
                                         bitmask, **always derived** from
                                         ``solution`` by :func:`build_result`;
                                         algorithms must not fill it themselves
``path``           ``list[tuple[int, ...]]``
                                         bitmask states from the empty board
                                         (``path[0]``) to the goal (``path[-1]``);
                                         ``[]`` when the puzzle was not solved
``expanded``       ``int``               nodes taken out of the frontier and
                                         processed, the goal node included
``generated``      ``int``               nodes pushed onto the frontier
                                         (duplicates and invalid nodes excluded)
``frontier_peak``  ``int``               largest number of nodes the frontier
                                         held at once

Layer 2 -- what ``scripts/run.py`` adds
---------------------------------------
``puzzle``, ``size``, ``status`` (``"xong"`` | ``"timeout"`` | ``"vo nghiem"``)
and ``time_s``.  ``status`` belongs to the runner: an algorithm cannot know that
it was interrupted by a timeout.
"""
from __future__ import annotations

from typing import Any, Iterable, Sequence

Coord = tuple[int, int]
State = tuple[int, ...]

#: Keys every layer-1 result must carry, in a stable order.
CONTRACT_FIELDS: tuple[str, ...] = (
    "solution",
    "state",
    "path",
    "expanded",
    "generated",
    "frontier_peak",
)


def empty_state(problem: Any) -> State:
    """Return the bitmask of a board with no piece placed."""
    return tuple([0] * problem.rows)


def path_from_came_from(
    came_from: dict,
    goal: Sequence[int],
    empty: Sequence[int],
) -> list[State]:
    """Walk ``came_from`` backwards from ``goal`` and return the path in order.

    ``came_from`` maps every visited node to its parent, the root mapping to
    ``None``.  When the root is not the empty board (algorithms that propagate
    forced moves before searching), the empty board is prepended so ``path[0]``
    is always the board with no piece placed.
    """
    states: list[State] = []
    node: Any = tuple(goal)
    while node is not None:
        states.append(tuple(int(mask) for mask in node))
        node = came_from[node]
    states.reverse()
    if states[0] != tuple(empty):
        states.insert(0, tuple(int(mask) for mask in empty))
    return states


def build_result(
    problem: Any,
    *,
    solution: Iterable[Coord] = (),
    path: Iterable[Sequence[int]] = (),
    expanded: int = 0,
    generated: int = 0,
    frontier_peak: int = 0,
) -> dict:
    """Assemble a layer-1 result, deriving ``state`` from ``solution``.

    ``state`` is never taken from the caller: it is recomputed with
    ``problem.state_from_coords(solution)`` so the two fields cannot drift
    apart.  An unsolved puzzle gets ``solution == []``, ``state is None`` and
    ``path == []``.

    Raises ``ValueError`` when the supplied ``path`` does not start at the
    empty board or does not end at the goal state.
    """
    coords: list[list[int]] = [[int(r), int(c)] for r, c in solution]

    if not coords:
        return {
            "solution": [],
            "state": None,
            "path": [],
            "expanded": int(expanded),
            "generated": int(generated),
            "frontier_peak": int(frontier_peak),
        }

    state = problem.state_from_coords(coords)
    states: list[State] = [tuple(int(mask) for mask in item) for item in path]

    if not states:
        raise ValueError("a solved result must carry a non-empty path")
    if states[0] != empty_state(problem):
        raise ValueError(
            f"path[0] must be the empty board, got {states[0]!r}"
        )
    if states[-1] != state:
        raise ValueError(
            f"path[-1] must equal the goal state, got {states[-1]!r} != {state!r}"
        )

    return {
        "solution": coords,
        "state": state,
        "path": states,
        "expanded": int(expanded),
        "generated": int(generated),
        "frontier_peak": int(frontier_peak),
    }


def validate_result(problem: Any, result: dict) -> list[str]:
    """Return the contract violations found in ``result`` (empty when sound).

    Only the layer-1 contract is checked here -- shape, derived ``state``,
    ``path`` endpoints and counters.  Whether the solution obeys the puzzle
    rules is a separate question, answered by ``problem.is_goal(state)``.
    """
    errors: list[str] = []

    missing = [key for key in CONTRACT_FIELDS if key not in result]
    if missing:
        return [f"missing fields: {', '.join(missing)}"]

    solution = result["solution"]
    state = result["state"]
    path = result["path"]

    if not isinstance(solution, list):
        return [f"solution must be a list, got {type(solution).__name__}"]

    for coord in solution:
        if (
            not isinstance(coord, (list, tuple))
            or len(coord) != 2
            or not all(isinstance(x, int) and not isinstance(x, bool) for x in coord)
        ):
            errors.append(f"invalid coordinate: {coord!r}")
            continue
        r, c = coord
        if not (0 <= r < problem.rows and 0 <= c < problem.cols):
            errors.append(f"coordinate out of bounds: {coord!r}")

    for key in ("expanded", "generated", "frontier_peak"):
        value = result[key]
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            errors.append(f"{key} must be a non-negative int, got {value!r}")

    if not isinstance(path, list):
        errors.append(f"path must be a list, got {type(path).__name__}")
        return errors

    if not solution:
        if state is not None:
            errors.append(f"an unsolved result must have state None, got {state!r}")
        if path:
            errors.append("an unsolved result must have an empty path")
        return errors

    try:
        expected = problem.state_from_coords(solution)
    except (ValueError, TypeError) as exc:
        errors.append(f"solution is not convertible to a state: {exc}")
        return errors

    if not isinstance(state, (list, tuple)) or tuple(state) != tuple(expected):
        errors.append("state does not match state_from_coords(solution)")

    if not path:
        errors.append("a solved result must carry a non-empty path")
        return errors

    if tuple(path[0]) != empty_state(problem):
        errors.append("path[0] is not the empty board")
    if tuple(path[-1]) != tuple(expected):
        errors.append("path[-1] is not the goal state")
    if result["expanded"] < 1:
        errors.append("expanded must count at least the goal node")

    return errors

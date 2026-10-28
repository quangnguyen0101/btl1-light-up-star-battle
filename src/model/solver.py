"""Common adapter for search algorithms implemented by other team members."""
from typing import Callable, TypeVar, Any

Problem = TypeVar("Problem")
Result = TypeVar("Result")
Algorithm = Callable[[Problem], Result | None]

def solve(problem: Problem, algo: Algorithm[Problem, Result]) -> Result | None:
    """Call an algorithm using the shared interface; no search is implemented here."""
    if not callable(algo):
        raise TypeError("algo must be callable and accept one problem argument")
    return algo(problem)

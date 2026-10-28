"""Shared puzzle model: problem definitions and the solver adapter."""
from src.model.light_up import LightUpProblem
from src.model.result import (
    CONTRACT_FIELDS,
    build_result,
    empty_state,
    path_from_came_from,
    validate_result,
)
from src.model.solver import solve
from src.model.star_battle import StarBattleProblem

__all__ = [
    "CONTRACT_FIELDS",
    "LightUpProblem",
    "StarBattleProblem",
    "build_result",
    "empty_state",
    "path_from_came_from",
    "solve",
    "validate_result",
]

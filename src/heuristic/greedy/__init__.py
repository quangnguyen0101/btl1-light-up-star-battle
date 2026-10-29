"""Greedy Best-First search, one module per puzzle kind."""
from src.heuristic.greedy.light_up import greedy as _greedy_light_up
from src.heuristic.greedy.star_battle import greedy as _greedy_star_battle
from src.model.star_battle import StarBattleProblem


def greedy(problem) -> dict:
    """Chạy Greedy Best-First với bản cài đặt tương ứng loại bài."""
    if isinstance(problem, StarBattleProblem):
        return _greedy_star_battle(problem)
    return _greedy_light_up(problem)

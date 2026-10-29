"""Tên thuật toán -> hàm, cho họ tìm kiếm có heuristic."""
from src.heuristic.a_star.light_up import a_star as _a_star_light_up
from src.heuristic.a_star.star_battle import a_star as _a_star_star_battle
from src.heuristic.greedy import greedy
from src.model.star_battle import StarBattleProblem


def a_star(problem) -> dict:
    """Chạy A* với bản cài đặt tương ứng loại bài."""
    if isinstance(problem, StarBattleProblem):
        return _a_star_star_battle(problem)
    return _a_star_light_up(problem)


ALGORITHMS = {"a_star": a_star, "greedy": greedy}

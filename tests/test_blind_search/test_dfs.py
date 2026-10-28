"""Test DFS trên dữ liệu thật và trên hợp đồng kết quả."""
import unittest
from pathlib import Path

from src.blind_search import ALGORITHMS
from src.model.light_up import LightUpProblem
from src.model.result import empty_state, validate_result
from src.model.star_battle import StarBattleProblem
from src.utils import load_problem

ROOT = Path(__file__).resolve().parents[2]
DFS = ALGORITHMS["dfs"]

SMALL = (
    "star_battle/sb-5x5-normal-03.json",
    "star_battle/sb-6x6-shapeless-01.json",
    "light_up/lu-7x7-normal-03.json",
    "light_up/lu-7x7-easy-01.json",
)


class TestDFS(unittest.TestCase):
    def test_solves_small_puzzles(self):
        for name in SMALL:
            with self.subTest(puzzle=name):
                problem = load_problem(ROOT / "data" / name)
                result = DFS(problem)

                self.assertTrue(result["solution"], name)
                self.assertTrue(problem.is_goal(result["state"]), name)
                self.assertGreater(result["expanded"], 0)

    def test_contract(self):
        problem = load_problem(ROOT / "data" / "star_battle/sb-5x5-normal-03.json")
        result = DFS(problem)

        self.assertEqual(validate_result(problem, result), [])
        self.assertEqual(result["path"][0], empty_state(problem))
        self.assertEqual(
            result["path"][-1], problem.state_from_coords(result["solution"])
        )
        # Star Battle quyết định một hàng mỗi mức: path dài rows + 1.
        self.assertEqual(len(result["path"]), problem.rows + 1)

    def test_path_holds_only_valid_prefixes(self):
        problem = load_problem(ROOT / "data" / "light_up/lu-7x7-normal-03.json")
        result = DFS(problem)

        self.assertTrue(all(problem.is_valid_state(state) for state in result["path"]))
        bulbs = [sum(mask.bit_count() for mask in state) for state in result["path"]]
        self.assertEqual(bulbs, sorted(bulbs), "so bong khong duoc giam")

    def test_no_solution(self):
        # 2x2, một sao mỗi hàng/cột: mọi cách đặt đều kề chéo nhau.
        problem = StarBattleProblem.from_dict({
            "name": "impossible",
            "type": "star_battle",
            "variant": "shapeless",
            "rows": 2,
            "cols": 2,
            "stars_per_unit": 1,
        })
        result = DFS(problem)

        self.assertEqual(result["solution"], [])
        self.assertIsNone(result["state"])
        self.assertEqual(result["path"], [])
        self.assertGreater(result["expanded"], 0)
        self.assertEqual(validate_result(problem, result), [])

    def test_large_puzzle(self):
        problem = load_problem(ROOT / "data" / "star_battle/sb-10x10-normal-01.json")
        result = DFS(problem)

        self.assertTrue(problem.is_goal(result["state"]))
        self.assertGreater(result["expanded"], 1000)


if __name__ == "__main__":
    unittest.main()

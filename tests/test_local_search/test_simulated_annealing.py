"""Test Simulated Annealing: đề nhỏ (nhanh), hợp đồng, và đề vô nghiệm."""
import unittest
from pathlib import Path

from src.local_search import ALGORITHMS
from src.model.result import empty_state, validate_result
from src.model.star_battle import StarBattleProblem
from src.utils import load_problem

ROOT = Path(__file__).resolve().parents[2]
SA = ALGORITHMS["simulated_annealing"]

SMALL = (
    "star_battle/sb-5x5-normal-03.json",
    "light_up/lu-7x7-normal-03.json",
)


class TestSimulatedAnnealing(unittest.TestCase):
    def test_solves_small_puzzles(self):
        for name in SMALL:
            with self.subTest(puzzle=name):
                problem = load_problem(ROOT / "data" / name)
                result = SA(problem, max_steps=300_000)

                self.assertTrue(result["solution"], name)
                self.assertTrue(problem.is_goal(result["state"]), name)

    def test_contract(self):
        problem = load_problem(ROOT / "data" / "light_up/lu-7x7-normal-03.json")
        result = SA(problem, max_steps=300_000)

        self.assertEqual(validate_result(problem, result), [])
        self.assertEqual(result["path"][0], empty_state(problem))
        self.assertEqual(result["path"][-1], problem.state_from_coords(result["solution"]))
        self.assertEqual(result["frontier_peak"], 1)

    def test_deterministic_with_seed(self):
        problem = load_problem(ROOT / "data" / "star_battle/sb-5x5-normal-03.json")

        self.assertEqual(
            SA(problem, seed=7, max_steps=300_000)["solution"],
            SA(problem, seed=7, max_steps=300_000)["solution"],
        )

    def test_no_solution_stops_at_max_steps(self):
        # 2x2, một sao mỗi hàng/cột: mọi cách đặt đều kề chéo nhau.
        problem = StarBattleProblem.from_dict({
            "name": "impossible",
            "type": "star_battle",
            "variant": "shapeless",
            "rows": 2,
            "cols": 2,
            "stars_per_unit": 1,
        })
        result = SA(problem, max_steps=2_000)

        self.assertEqual(result["solution"], [])
        self.assertIsNone(result["state"])
        self.assertEqual(result["path"], [])
        self.assertEqual(result["expanded"], 2_000)
        self.assertEqual(validate_result(problem, result), [])


if __name__ == "__main__":
    unittest.main()

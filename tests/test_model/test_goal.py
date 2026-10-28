"""Khoá hành vi của ``is_goal`` -- nguồn chân lý duy nhất để chấm lời giải.

Vì dự án chỉ dùng ``is_goal`` (không có bộ kiểm luật thứ hai), mỗi luật dễ bị
bỏ sót được ghim bằng một ca "gần đúng nhưng sai" ở đây.
"""
import unittest

from src.model.light_up import LightUpProblem
from src.model.star_battle import StarBattleProblem


class TestLightUpGoal(unittest.TestCase):
    def test_two_bulbs_around_clue_one(self):
        """Tường '1' có hai bóng kề: sai dù không có bóng nào nhìn nhau."""
        problem = LightUpProblem.from_dict({
            "name": "clue_one",
            "type": "light_up",
            "rows": 3,
            "cols": 3,
            "grid": [
                [".", ".", "."],
                [".", "1", "."],
                [".", ".", "."],
            ],
        })
        state = problem.state_from_coords([(0, 1), (1, 0)])

        self.assertFalse(problem.is_goal(state))

    def test_clues_met_but_one_cell_dark(self):
        """Tường số đã đủ bóng nhưng còn một ô trắng không thể được chiếu sáng."""
        problem = LightUpProblem.from_dict({
            "name": "dark_corner",
            "type": "light_up",
            "rows": 3,
            "cols": 3,
            "grid": [
                [".", ".", "1"],
                [".", ".", "#"],
                ["#", "#", "."],
            ],
        })
        state = problem.state_from_coords([(0, 1)])

        self.assertTrue(problem.is_valid_state(state))  # chưa xét "sáng hết"
        self.assertFalse(problem.is_goal(state))        # nhưng chưa phải đích

    def test_all_lit_but_two_bulbs_see_each_other(self):
        """Mọi ô đều sáng nhưng hai bóng cùng hàng nhìn thấy nhau."""
        problem = LightUpProblem.from_dict({
            "name": "conflict",
            "type": "light_up",
            "rows": 1,
            "cols": 3,
            "grid": [["." , ".", "."]],
        })
        state = problem.state_from_coords([(0, 0), (0, 2)])

        self.assertEqual(
            problem.illuminated_cells(state), {(0, 0), (0, 1), (0, 2)}
        )
        self.assertFalse(problem.is_goal(state))


class TestStarBattleGoal(unittest.TestCase):
    def test_region_short_of_one_star(self):
        """Hàng và cột đúng số sao, không sao nào kề nhau, nhưng vùng sai."""
        problem = StarBattleProblem.from_dict({
            "name": "region_off",
            "type": "star_battle",
            "variant": "normal",
            "rows": 4,
            "cols": 4,
            "stars_per_unit": 1,
            "regions": [
                [0, 0, 1, 1],
                [0, 0, 1, 1],
                [2, 2, 2, 3],
                [2, 2, 2, 3],
            ],
        })
        state = problem.state_from_coords([(0, 1), (1, 3), (2, 0), (3, 2)])

        # Hàng và cột đều đúng một sao, và không cặp nào kề nhau.
        self.assertEqual([mask.bit_count() for mask in state], [1, 1, 1, 1])
        self.assertEqual(
            [sum(mask >> c & 1 for mask in state) for c in range(4)], [1, 1, 1, 1]
        )
        self.assertFalse(problem.is_goal(state))

    def test_two_stars_touch_diagonally(self):
        """Hai sao kề chéo là sai, dù hàng/cột còn đúng."""
        problem = StarBattleProblem.from_dict({
            "name": "diagonal",
            "type": "star_battle",
            "variant": "shapeless",
            "rows": 4,
            "cols": 4,
            "stars_per_unit": 1,
        })
        state = problem.state_from_coords([(0, 0), (1, 1)])

        self.assertFalse(problem.is_goal(state))

    def test_star_on_blocked_cell(self):
        """Sao nằm trên ô bị khoá là sai (state dựng trực tiếp, không qua toạ độ)."""
        problem = StarBattleProblem.from_dict({
            "name": "blocked",
            "type": "star_battle",
            "variant": "shapeless",
            "rows": 3,
            "cols": 3,
            "stars_per_unit": 1,
            "blocked_cells": [[1, 1]],
        })
        state = (0, 1 << 1, 0)

        self.assertFalse(problem.is_goal(state))


if __name__ == "__main__":
    unittest.main()

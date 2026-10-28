"""Blind search (DFS) for Star Battle and Light Up.

State = ``(row bitmasks, depth)``.  Star Battle fills one row per level; Light Up
decides one white cell (bulb / no bulb) per level, in row-major order.  Because
every level only ever adds to the prefix decided so far, the state at depth ``d``
is exactly the path prefix of depth ``d`` -- so the path can be rebuilt from the
goal state alone, without a ``came_from`` table.
"""
from __future__ import annotations

from functools import cache
from itertools import combinations

from src.model.light_up import LightUpProblem
from src.model.result import build_result
from src.model.star_battle import StarBattleProblem


#    Star Battle

@cache
def _row_masks(n: int, k: int) -> list[int]:
    """All rows with exactly k stars, none horizontally adjacent."""
    masks = (sum(1 << c for c in cols) for cols in combinations(range(n), k))
    return [m for m in masks if not m & (m >> 1)]


def star_battle_children(problem: StarBattleProblem, state):
    masks, r = state
    near = masks[r - 1] | masks[r - 1] << 1 | masks[r - 1] >> 1 if r else 0  # cells touching the row above
    kids = []
    for m in _row_masks(problem.cols, problem.stars_per_unit):
        if m & near:
            continue
        child = masks[:r] + (m,) + masks[r + 1:]
        if problem.is_valid_state(child, partial=True):
            kids.append((child, r + 1))
    return kids


def star_battle_path(problem: StarBattleProblem, masks, depth: int):
    """States from the empty board to ``masks``, one per decided row."""
    path = [tuple([0] * problem.rows)]
    for r in range(depth):
        path.append(masks[:r + 1] + (0,) * (problem.rows - r - 1))
    return path


#    Light Up

@cache
def _light_up_info(problem: LightUpProblem):
    """White cells (decision order), cells each white cell can see, numbered walls."""
    rows, cols, grid = problem.rows, problem.cols, problem.grid
    whites = [(r, c) for r in range(rows) for c in range(cols) if grid[r][c] == "."]
    sees = {}
    for r, c in whites:
        seen = {(r, c)}
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            rr, cc = r + dr, c + dc
            while 0 <= rr < rows and 0 <= cc < cols and grid[rr][cc] == ".":
                seen.add((rr, cc))
                rr, cc = rr + dr, cc + dc
        sees[(r, c)] = seen
    numbers = [
        (int(grid[r][c]), [(rr, cc) for rr, cc in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1))
                           if 0 <= rr < rows and 0 <= cc < cols and grid[rr][cc] == "."])
        for r in range(rows) for c in range(cols) if grid[r][c] in "01234"
    ]
    return whites, sees, numbers


def _light_up_ok(problem: LightUpProblem, masks, i: int) -> bool:
    """Cells whites[:i] are decided. Reject if a rule is broken or can no longer be met."""
    if not problem.is_valid_state(masks):  # bulbs see each other / too many around a number
        return False
    whites, sees, numbers = _light_up_info(problem)
    lit = problem.illuminated_cells(masks)
    free = {x for x in whites[i:] if x not in lit}  # undecided cells that can still take a bulb
    if any(x not in lit and not sees[x] & free for x in whites):  # cell can never be lit
        return False
    return all(
        sum(masks[r] >> c & 1 for r, c in nbrs) + sum(x in free for x in nbrs) >= n
        for n, nbrs in numbers
    )


def light_up_children(problem: LightUpProblem, state):
    masks, i = state
    r, c = _light_up_info(problem)[0][i]
    on = masks[:r] + (masks[r] | 1 << c,) + masks[r + 1:]
    return [(s, i + 1) for s in (on, masks) if _light_up_ok(problem, s, i + 1)]


def light_up_path(problem: LightUpProblem, masks, depth: int):
    """States from the empty board to ``masks``, one per decided white cell."""
    whites = _light_up_info(problem)[0]
    rows = [0] * problem.rows
    path = [tuple(rows)]
    for i in range(depth):
        r, c = whites[i]
        if masks[r] >> c & 1:
            rows[r] |= 1 << c
        path.append(tuple(rows))
    return path


#    DFS

def dfs(problem) -> dict:
    """Depth-first search, returning the shared result contract.

    Timeouts are not handled here: ``scripts/run.py`` interrupts the call and
    records ``status`` itself.
    """
    if isinstance(problem, StarBattleProblem):
        children, goal_depth, path_of = star_battle_children, problem.rows, star_battle_path
    else:
        children, goal_depth, path_of = light_up_children, len(_light_up_info(problem)[0]), light_up_path

    stack = [((0,) * problem.rows, 0)]
    expanded = generated = 0
    frontier_peak = 1
    while stack:
        masks, depth = stack.pop()
        expanded += 1  # every popped node counts, the goal node included
        if depth == goal_depth:
            if problem.is_goal(masks):
                return build_result(
                    problem,
                    solution=problem.coords_from_state(masks),
                    path=path_of(problem, masks, depth),
                    expanded=expanded,
                    generated=generated,
                    frontier_peak=frontier_peak,
                )
            continue
        kids = children(problem, (masks, depth))
        generated += len(kids)
        stack.extend(reversed(kids))  # reversed so the first child is explored first
        frontier_peak = max(frontier_peak, len(stack))

    return build_result(
        problem,
        expanded=expanded,
        generated=generated,
        frontier_peak=frontier_peak,
    )

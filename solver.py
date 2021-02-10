from collections import defaultdict
from pprint import pprint

import numpy as np


def eliminate(state_to_constraints, constraint_to_states, selected_state):
    if selected_state not in state_to_constraints:
        return state_to_constraints

    state_to_constraints = dict(state_to_constraints)
    adjacent_states = set.union(
        *(constraint_to_states[constraint] for constraint in state_to_constraints[selected_state]))
    for state in adjacent_states:
        if state in state_to_constraints:
            state_to_constraints.pop(state)
    return state_to_constraints


def solve(state_to_constraints, partial_solution=None):
    partial_solution = partial_solution or set()

    if not state_to_constraints:
        yield frozenset(partial_solution)

    else:
        for selected_state in list(state_to_constraints.keys()):
            original_state_to_constraints = state_to_constraints
            state_to_constraints = eliminate(state_to_constraints, constraint_to_states,
                                             selected_state)

            partial_solution.add(selected_state)
            yield from solve(state_to_constraints, partial_solution)
            partial_solution.remove(selected_state)

            state_to_constraints = original_state_to_constraints


n = 2

grid = [
    [0, 0],
    [0, 0]
]

group_grid = [
    [1, 2],
    [3, 4]
]

# n = 9
#
# grid = [
#     [5, 3, 0, 0, 7, 0, 0, 0, 0],
#     [6, 0, 0, 1, 9, 5, 0, 0, 0],
#     [0, 9, 8, 0, 0, 0, 0, 6, 0],
#     [8, 0, 0, 0, 6, 0, 0, 0, 3],
#     [4, 0, 0, 8, 0, 3, 0, 0, 1],
#     [7, 0, 0, 0, 2, 0, 0, 0, 6],
#     [0, 6, 0, 0, 0, 0, 2, 8, 0],
#     [0, 0, 0, 4, 1, 9, 0, 0, 5],
#     [0, 0, 0, 0, 8, 0, 0, 7, 9]]
#
# group_grid = [
#     [1, 1, 1, 2, 2, 2, 3, 3, 3],
#     [1, 1, 1, 2, 2, 2, 3, 3, 3],
#     [1, 1, 1, 2, 2, 2, 3, 3, 3],
#     [4, 4, 4, 5, 5, 5, 6, 6, 6],
#     [4, 4, 4, 5, 5, 5, 6, 6, 6],
#     [4, 4, 4, 5, 8, 8, 6, 6, 6],
#     [7, 7, 7, 8, 8, 8, 9, 9, 9],
#     [7, 7, 7, 8, 8, 8, 9, 9, 9],
#     [7, 7, 7, 8, 8, 8, 9, 9, 9]]

grid = np.array(grid)
group_grid = np.array(group_grid)

state_to_constraints = defaultdict(set)
constraint_to_states = defaultdict(set)
eliminated_states = set()

for row in range(1, n + 1):
    for col in range(1, n + 1):
        for val in range(1, n + 1):
            state = (row, col, val)

            cell_constraint = f'R{row}C{col}'
            state_to_constraints[state].add(cell_constraint)
            constraint_to_states[cell_constraint].add(state)

            row_constraint = f'R{row}#{val}'
            state_to_constraints[state].add(row_constraint)
            constraint_to_states[row_constraint].add(state)

            col_constraint = f'C{col}#{val}'
            state_to_constraints[state].add(col_constraint)
            constraint_to_states[col_constraint].add(state)

            group = group_grid[row - 1, val - 1]
            group_constraint = f'G{group}#{val}'
            state_to_constraints[state].add(group_constraint)
            constraint_to_states[group_constraint].add(state)

            if grid[row - 1, col - 1] == val:
                eliminated_states.add((row, col, val))

pprint(state_to_constraints)
pprint(constraint_to_states)

for eliminated_state in eliminated_states:
    state_to_constraints = eliminate(state_to_constraints, constraint_to_states, eliminated_state)

solutions = set()
for solution in solve(state_to_constraints, eliminated_states):
    if len(solution) == n ** 2 and solution not in solutions:
        solutions.add(solution)
        print(solution)

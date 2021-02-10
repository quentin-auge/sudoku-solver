from collections import defaultdict

import numpy as np


def eliminate(state_to_constraints, constraint_to_states, selected_state):
    if selected_state not in state_to_constraints:
        raise

    state_to_constraints = dict(state_to_constraints)
    constraint_to_states = {constraint: set(states) for constraint, states in
                            constraint_to_states.items()}

    for constraint in state_to_constraints[selected_state]:
        for state in constraint_to_states[constraint]:
            for constraint2 in state_to_constraints[state]:
                if constraint2 != constraint:
                    constraint_to_states[constraint2].remove(state)
            state_to_constraints.pop(state)
        constraint_to_states.pop(constraint)

    return state_to_constraints, constraint_to_states


def solve(state_to_constraints, constraint_to_states, solution):
    if not state_to_constraints:
        yield solution

    else:
        selected_constraint = min(constraint_to_states,
                                  key=lambda constraint: len(constraint_to_states[constraint]))

        for selected_state in list(constraint_to_states[selected_constraint]):
            eliminated_state_to_constraints, eliminated_constraint_to_states = (
                eliminate(state_to_constraints, constraint_to_states, selected_state)
            )

            yield from solve(eliminated_state_to_constraints, eliminated_constraint_to_states,
                             solution + [selected_state])


def plot_grid(grid, group_grid):
    import matplotlib.pyplot as plt

    plt.matshow(group_grid, cmap=plt.cm.get_cmap('Set3'))

    n_rows, n_cols = grid.shape
    for row in range(n_rows):
        for col in range(n_cols):
            val = str(grid[col, row] or '')
            plt.text(row, col, val, va='center', ha='center')
            plt.xticks(np.arange(0.5, 9.5), [])
            plt.yticks(np.arange(0.5, 9.5), [])
            plt.grid(color='black')

    plt.show()

# n = 2
#
# grid = [
#     [0, 0],
#     [0, 0]
# ]
#
# group_grid = [
#     [1, 2],
#     [1, 2]
# ]

# grid = np.array(grid)
# group_grid = np.array(group_grid)


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
#     [4, 4, 4, 5, 5, 5, 6, 6, 6],
#     [7, 7, 7, 8, 8, 8, 9, 9, 9],
#     [7, 7, 7, 8, 8, 8, 9, 9, 9],
#     [7, 7, 7, 8, 8, 8, 9, 9, 9]]
#
# grid = np.array(grid)
# group_grid = np.array(group_grid)

n = 9
sudoku = np.load('test_2020_04.npz', allow_pickle=True)['sudokus'][0]
grid = sudoku['grid']
group_grid = sudoku['group_grid']

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

            group = group_grid[row - 1, col - 1]
            group_constraint = f'G{group}#{val}'
            state_to_constraints[state].add(group_constraint)
            constraint_to_states[group_constraint].add(state)

            if grid[row - 1, col - 1] == val:
                eliminated_states.add((row, col, val))

for eliminated_state in eliminated_states:
    if eliminated_state not in state_to_constraints:
        row, col, _ = eliminated_state
        raise ValueError(f'Initial grid violates (row {row}, col {col})')

    state_to_constraints, constraint_to_states = eliminate(state_to_constraints,
                                                           constraint_to_states, eliminated_state)

plot_grid(grid, group_grid)

solution_grids = []
for solution in solve(state_to_constraints, constraint_to_states, []):
    solution_grid = grid * 0
    for row, col, val in set.union(eliminated_states, solution):
        solution_grid[row - 1, col - 1] = val
    print(solution_grid)
    solution_grids.append(grid)
    plot_grid(solution_grid, group_grid)

from collections import defaultdict, namedtuple
from copy import deepcopy
from dataclasses import dataclass, field
from typing import Dict, Iterator, List, Set

import numpy as np

# A (filled) sudoku cell representation
State = namedtuple('State', ['row', 'col', 'val'])


@dataclass
class CoverMatrix:
    """
    A sparse cover matrix representation for the exact cover problem.
    """

    # State to constraints mapping (in matrix terms: row to columns)
    constraints: Dict[str, Set] = field(default_factory=lambda: defaultdict(set))

    # Constraint to states mapping (in matrix terms: column to rows)
    states: Dict[str, Set] = field(default_factory=lambda: defaultdict(set))

    def __deepcopy__(self, memodict={}):
        states = {constraint: set(states) for constraint, states in self.states.items()}
        constraints = {state: set(constraints) for state, constraints in self.constraints.items()}
        return CoverMatrix(constraints, states)


def get_cover_matrix(grid: np.ndarray, group_grid: np.ndarray) -> CoverMatrix:
    """
    Transform the sudoku problem into a cover matrix.

    Args:
        grid: the sudoku grid
        group_grid: the group grid

    Returns:
        The cover matrix.

    Raises:
        `ValueError` if the grid is invalid (sudoku constraints violated).
    """

    assert grid.shape == group_grid.shape

    matrix = CoverMatrix()
    eliminated_cells = set()

    for row in range(1, grid.shape[0] + 1):
        for col in range(1, grid.shape[1] + 1):
            for val in range(1, len(np.unique(grid.nonzero())) + 1):
                state = State(row, col, val)

                # A value (1-9) appears exactly once per cell
                cell_constraint = f'R{row}C{col}'
                matrix.constraints[state].add(cell_constraint)
                matrix.states[cell_constraint].add(state)

                # A value (1-9) appears exactly once per row
                row_constraint = f'R{row}#{val}'
                matrix.constraints[state].add(row_constraint)
                matrix.states[row_constraint].add(state)

                # A value (1-9) appears exactly once per column
                col_constraint = f'C{col}#{val}'
                matrix.constraints[state].add(col_constraint)
                matrix.states[col_constraint].add(state)

                # A value (1-9) appears exactly once per group
                group = group_grid[row - 1, col - 1]
                group_constraint = f'G{group}#{val}'
                matrix.constraints[state].add(group_constraint)
                matrix.states[group_constraint].add(state)

                # Record filled cells
                if grid[row - 1, col - 1] == val:
                    eliminated_cells.add((row, col, val))

    # Eliminate already-filled cells
    for eliminated_cell in eliminated_cells:

        if eliminated_cell not in matrix.constraints:
            # Eliminating a cell twice means the grid is invalid
            row, col, _ = eliminated_cell
            raise ValueError(f'Invalid initial grid (constraint violation: row {row}, col {col})')

        # Perform elimination
        matrix = eliminate(matrix, eliminated_cell)

    return matrix


def eliminate(matrix: CoverMatrix, selected_state: State) -> CoverMatrix:
    """
    Select a given state (fill a sudoku cell), and trim the cover matrix accordingly.

    Args:
        matrix: the cover matrix
        selected_state: the selected state

    Returns:
        The trimmed cover matrix.
    """

    # Create a new matrix
    matrix = deepcopy(matrix)

    for selected_constraint in matrix.constraints[selected_state]:
        # Get all the states that match the constraint
        for state in matrix.states[selected_constraint]:
            # Eliminate the contraints associated with this state, as well as the states
            # associated with each of these contraints
            for constraint in matrix.constraints[state]:
                if constraint != selected_constraint:
                    matrix.states[constraint].remove(state)
            matrix.constraints.pop(state)
        # Eliminate selected constraint
        matrix.states.pop(selected_constraint)

    return matrix


def solve_matrix(matrix: CoverMatrix, solution: List[State]) -> Iterator[List[State]]:
    """
    Solve the extract cover problem by recursive elimination.

    Args:
        matrix: the cover matrix
        solution: the current solution (can be partial, depending on the recursion stage)

    Yields:
        All solution states lists.
    """

    if not matrix.constraints:
        yield solution

    else:
        # Select constraint with the minimum number of associated states.
        # The rational of this is: "rush as fast as possible to a possible solution before
        # backtracking".
        min_key = lambda constraint: len(matrix.states[constraint])
        selected_constraint = min(matrix.states, key=min_key)

        # Perform recursive elimination
        for selected_state in list(matrix.states[selected_constraint]):
            trimmed_matrix = eliminate(matrix, selected_state)
            yield from solve_matrix(trimmed_matrix, solution + [selected_state])


def solve_grid(grid: np.ndarray, group_grid: np.ndarray) -> np.ndarray:
    """
    Solve a sudoku grid.

    Returns:
        A solution grid.

    Raises:
        `RuntimeError` if there is no solution.
    """

    matrix = get_cover_matrix(grid, group_grid)

    try:
        solution = next(solve_matrix(matrix, []))
    except StopIteration:
        raise RuntimeError('No solution')
    else:
        return fill_grid(grid, solution)


def fill_grid(grid: np.array, solution: List[State]) -> np.array:
    """
    Form a solution grid from initial grid and a solution states list.

    Args:
        grid: the grid
        solution: the solution

    Returns:
        A filled grid.
    """

    grid = grid.copy()
    for state in solution:
        grid[state.row - 1, state.col - 1] = state.val
    return grid


def plot_grid(grid, group_grid, colormap='Set3'):
    """
    Plot a sudoku grid.
    """

    from matplotlib import pyplot as plt

    n_rows, n_cols = grid.shape
    plt.rcParams['figure.figsize'] = (n_rows, n_cols)

    plt.matshow(group_grid, cmap=plt.cm.get_cmap(colormap))

    for row in range(n_rows):
        for col in range(n_cols):
            val = str(grid[col, row] or '')
            plt.text(row, col, val, va='center', ha='center')
            plt.xticks(np.arange(0.5, n_rows + 0.5), [])
            plt.yticks(np.arange(0.5, n_cols + 0.5), [])
            plt.grid(color='black')

    plt.show()

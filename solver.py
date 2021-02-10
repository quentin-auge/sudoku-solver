import itertools
from collections import defaultdict
from pprint import pprint
import random

state_to_constraints = defaultdict(set)
constraint_to_states = defaultdict(set)

n = 2

for row in range(1, n+1):
  for col in range(1, n+1):
    for val in range(1, n+1):
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




def solve(state_to_constraints, partial_solution=None):
  partial_solution = partial_solution or set()

  if len(partial_solution) == n ** 2:
    yield frozenset(partial_solution)

  else:
    deleted_state_to_constraints = {}

    for selected_state, constraints in list(state_to_constraints.items()):
      # print(' ' * i * 2, 'select', selected_state)

      adjacent_states = set.union(*(constraint_to_states[constraint] for constraint in constraints))
      for state in adjacent_states:
        if state in state_to_constraints:
          # print(' ' * i * 2, '->', 'eliminate', state)
          deleted_state_to_constraints[state] = state_to_constraints.pop(state)
      # print(' ' * i * 2, '--->', state_to_constraints)

      partial_solution.add(selected_state)
      yield from solve(dict(state_to_constraints), partial_solution)
      partial_solution.remove(selected_state)

      for state in adjacent_states:
        if state in deleted_state_to_constraints:
          state_to_constraints[state] = deleted_state_to_constraints.pop(state)

      # print(' ' * i * 2, 'rollback', state_to_constraints)


pprint(state_to_constraints)
pprint(constraint_to_states)

solutions = set()
for solution in solve(state_to_constraints, set()):
  if solution not in solutions:
    solutions.add(solution)
    print(solution)

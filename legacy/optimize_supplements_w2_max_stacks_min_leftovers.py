# ChatGPT ref: https://chatgpt.com/c/66e662b8-6358-8008-8997-05c1b0e6c049

# TODO: can we also include current stock on hand into this optimisation as well?

# TODO: could we also include the costs + cost of shipping in this; and/or include a constraint for hitting the threshold for free shipping?

# TODO: would it make sense to include a constraint that we want to be able to make full weeks of doses (since that's how we lay them out)

from pulp import LpMaximize, LpProblem, LpVariable, lpSum, LpStatus
from tabulate import tabulate

from supplements_data import supplements

# Set the weights of the 2 variables being optimised for
w1, w2 = 10, 1
# w1, w2 = 10, 5

# Set a realistic minimum/maximum limit for the number of daily stacks (so the problem has non-infinite bounds)
s_min = 0
s_max = 4 * 4 * 7 # approx 4 months (4 * 4 weeks) of daily stacks
# s_max = 365

# Define the problem
problem = LpProblem("Maximize_Stacks_Minimize_Leftover", LpMaximize)

# Define problem variables

# Variable: x Bottles of Supplement
x = {supp['label']: LpVariable(f'x_{supp["label"]}', lowBound=0, cat='Integer') for supp in supplements}

# Variable: s Total Daily Stacks
s = LpVariable('s', lowBound=0, cat='Integer')

# Variable: r Unused Units of Supplement
r = {supp['label']: LpVariable(f'r_{supp["label"]}', lowBound=0, cat='Integer') for supp in supplements}

# Define problem constraints

# Compute total unused units (r) across all supplements
total_unused_units = lpSum(r[supp['label']] for supp in supplements)

# Constraint: Objective function: Maximize daily stacks (s) while minimizing unused units
#   We use weights (w1 and w2) to balance the importance of maximizing the number of daily stacks (s)
#   against minimizing the total unused units across all supplements (total_unused_units).
problem += (w1 * s) - (w2 * total_unused_units)

# Constraint: Min/max daily stacks
problem += s >= s_min
problem += s <= s_max

for supp in supplements:
  label = supp['label']
  daily_dose = supp['daily_dose']
  bottle_size = supp['bottle_size']

  # Helper variables to make the constraints clearer
  total_units_required = s * daily_dose           # Total units required to make 's' daily stacks
  total_units_available = x[label] * bottle_size  # Total units from all purchased bottles, where x[label] is the number of bottles.

  # Constraint: The required units must not exceed the total available from the purchased bottles.
  problem += total_units_required <= total_units_available

  # Constraint: Calculate the leftover units (r[label]) as the difference between available and required units.
  problem += r[label] == total_units_available - total_units_required

# Solve the problem
problem.solve()

# Check if the problem was solved optimally
if LpStatus[problem.status] == 'Optimal':
  print(f"Objective function weights: w1={w1}, w2={w2}")
  print(f"Minimum allowed number of daily stacks: {s_min}")
  print(f"Maximum allowed number of daily stacks: {s_max}")
  print(f"Optimal number of daily stacks: {int(s.varValue)}")

  print("\nBottles to purchase for each supplement:")

  results = [[
    supp['label'],
    int(x[supp['label']].varValue),
    int(r[supp['label']].varValue)
  ] for supp in supplements]

  print(tabulate(results, headers=["Supplement", "Bottles", "Unused Units"], tablefmt="simple"))
else:
  print("The problem did not solve optimally.")
  print(f"Solver Status: {LpStatus[problem.status]}")

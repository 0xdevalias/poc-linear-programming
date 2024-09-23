# ChatGPT ref: https://chatgpt.com/c/66e662b8-6358-8008-8997-05c1b0e6c049

# TODO: I'm not sure if this version is actually optimising very well at the moment..?

# TODO: could we also include the costs + cost of shipping in this; and/or include a constraint for hitting the threshold for free shipping?

# TODO: if we include the cost, we could potentially aim to minimize the cost of unused supplements instead of/as well as total number of unused?

# TODO: would it make sense to include a constraint that we want to be able to make full weeks of doses (since that's how we lay them out)

# TODO: would it make sense to include an optional constraint so that we don't try and buy a bottle when we only need less than 50% of it? Or is that already handled by trying to minimise the leftovers?

from pulp import LpMaximize, LpProblem, LpVariable, lpSum, LpStatus
from tabulate import tabulate

from supplements_data import supplements

# Set the weights of the 3 variables being optimized for
w1, w2, w3 = 0, 5, 5
# w1, w2, w3 = 10, 5, 5

# Set a realistic minimum/maximum limit for the number of daily stacks (so the problem has non-infinite bounds)
# s_min = 0
s_min = 1 * 4 * 7 # approx 1 month (1 * 4 weeks) of daily stacks
# s_min = 2 * 4 * 7 # approx 2 months (2 * 4 weeks) of daily stacks

s_max = 4 * 4 * 7 # approx 4 months (4 * 4 weeks) of daily stacks
# s_max = 5 * 4 * 7 # approx 5 months (5 * 4 weeks) of daily stacks
# s_max = 365

# Set to True to enforce weekly packs (s must be divisible by 7)
enforce_weekly_packs = False

# Set to True to require free shipping (total cost must be > $80)
require_free_shipping = True

# Define the problem
problem = LpProblem("Maximize_Stacks_Minimize_Leftover_And_Cost", LpMaximize)

# Define problem variables

# Variable: x Bottles of Supplement
x = {supp['label']: LpVariable(f'x_{supp["label"]}', lowBound=0, cat='Integer') for supp in supplements}

# Variable: s Total Daily Stacks
s = LpVariable('s', lowBound=0, cat='Integer')

# Variable: r Unused Units of Supplement
r = {supp['label']: LpVariable(f'r_{supp["label"]}', lowBound=0, cat='Integer') for supp in supplements}

# Conditional variable: k Number of Weeks (only used if weekly packs are enforced)
if enforce_weekly_packs:
  k = LpVariable('k', lowBound=0, cat='Integer')

# Define problem constraints

# Compute total unused units (r) across all supplements
total_unused_units = lpSum(r[supp['label']] for supp in supplements)

# Compute total cost of bottles purchased
total_cost = lpSum(supp['bottle_cost'] * x[supp['label']] for supp in supplements)

# Compute total cost of unused supplements
unused_cost = lpSum((supp['bottle_cost'] / supp['bottle_size']) * r[supp['label']] for supp in supplements)

# Objective function: Maximize daily stacks (s) while minimizing cost and unused units
#   We use weights (w1, w2, w3) to balance the importance of maximizing the number of daily stacks (s),
#   minimizing the total cost (total_cost), and minimizing the cost of unused supplements (unused_cost).
problem += (w1 * s) - (w2 * unused_cost) - (w3 * total_cost)

# Constraint: Min/max daily stacks
problem += s >= s_min
problem += s <= s_max

# Conditional constraint: Ensure that s is divisible by 7 (s = 7 * k) if weekly packs are enforced
if enforce_weekly_packs:
  problem += s == 7 * k

# Conditional constraint: Require free shipping if the total cost must be greater than $80
if require_free_shipping:
  problem += total_cost >= 80

for supp in supplements:
  label = supp['label']
  daily_dose = supp['daily_dose']
  bottle_size = supp['bottle_size']
  current_stock = supp['current_stock']

  # Helper variables to make the constraints clearer
  total_units_required = s * daily_dose                             # Total units required to make 's' daily stacks
  total_units_available = current_stock + (x[label] * bottle_size)  # Total units from current stock + all purchased bottles

  # Constraint: The required units must not exceed the total available from the purchased bottles and current stock.
  problem += total_units_required <= total_units_available

  # Constraint: Calculate the leftover units (r[label]) as the difference between available and required units.
  problem += r[label] == total_units_available - total_units_required

# Solve the problem
problem.solve()

# Check if the problem was solved optimally
if LpStatus[problem.status] == 'Optimal':
  print(f"Enforce weekly packs: {enforce_weekly_packs}")
  print(f"Require free shipping: {require_free_shipping}")
  print(f"Objective function weights: w1={w1}, w2={w2}, w3={w3}")
  print(f"Minimum allowed number of daily stacks: {s_min}")
  print(f"Maximum allowed number of daily stacks: {s_max}")
  print(f"Optimal number of daily stacks: {int(s.varValue)}")

  print(f"\nTotal cost of bottles purchased: ${total_cost.value():.2f}")
  print(f"Total cost of unused supplements: ${unused_cost.value():.2f}")

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

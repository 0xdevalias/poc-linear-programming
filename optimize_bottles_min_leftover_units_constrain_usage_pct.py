import pulp
from tabulate import tabulate

from supplements_data import supplements

# NOTE: This version attempts to minimize the leftover units, while conforming to a constraint of not purchasing new
# bottles unless a certain % of that bottle would be utilised. In reality, this seems to just end up arbitrarily
# restricting our potential options in ways that seem sub-par in the real world; unless we set the % so low (eg. 10%)
# that it makes it practically meaningless.
#
# It uses the Big M method to implement a conditional application of the minimum usage %, so that it only effectively
# applies when new bottles are purchased. This is a bit of a linear programming hack, necessitated by the PuLP library's
# inability to handle more complicated restraints directly within it's DSL (or the underlying solvers).

# Parameters
min_stacks = 0  # Minimum number of stacks (days)
max_stacks = 365  # Maximum number of stacks (days)
min_usage_pct = 0.1  # Minimum usage percentage of the last bottle
# min_usage_pct = 0.6  # Minimum usage percentage of the last bottle

M = 100000  # Big M for big-M method

# Initialize the LP problem
prob = pulp.LpProblem("SupplementPurchasing", pulp.LpMinimize)

# Decision variable: number of stacks (integer between min_stacks and max_stacks)
stacks = pulp.LpVariable("Stacks", lowBound=min_stacks, upBound=max_stacks, cat='Integer')

# Decision variables: number of bottles to purchase (integer >=0) and leftover units (continuous >=0) for each supplement
bottles_purchased = {supp['label']: pulp.LpVariable(f"BottlesPurchased_{supp['label']}", lowBound=0, cat='Integer') for supp in supplements}
leftover_units = {supp['label']: pulp.LpVariable(f"LeftoverUnits_{supp['label']}", lowBound=0, cat='Continuous') for supp in supplements}

# Decision variable: purchase indicator for each supplement
purchase_indicator = {supp['label']: pulp.LpVariable(f"PurchaseIndicator_{supp['label']}", cat='Binary') for supp in supplements}

# Constraints and Objective Function

for supp in supplements:
  label = supp['label']
  daily_dose = supp['daily_dose']
  bottle_size = supp['bottle_size']
  current_stock = supp['current_stock']

  # Ensure total available units cover the required units
  prob += (
    current_stock + (bottles_purchased[label] * bottle_size) - (stacks * daily_dose) - leftover_units[label] == 0,
    f"Balance_{label}"
  )

  # Constraints for purchase indicator variable
  prob += (
    bottles_purchased[label] >= purchase_indicator[label],
    f"PurchaseIndicatorLowerBound_{label}"
  )
  prob += (
    bottles_purchased[label] <= M * purchase_indicator[label],
    f"PurchaseIndicatorUpperBound_{label}"
  )

  # # Constraint ensuring leftover units can't be greater than bottle size
  # prob += (
  #   leftover_units[label] <= bottle_size,
  #   f"LeftoverUnitsLessThanBottleSizeConstraint2_{label}"
  # )

  # Constraint for leftover units when a new bottle is purchased
  #   When purchase_indicator == 1, we effectively apply the first branch
  #   When purchase_indicator == 0, we effectively apply the 2nd branch, where the big M is used as an artificially high value to basically nullify this constraint
  prob += (
    leftover_units[label]
    <=
    # When bottles purchased, enforce the usage percent
    (purchase_indicator[label] * (1 - min_usage_pct) * bottle_size)
    +
    # When bottles not purchased, use big M to make this constraint irrelevant
    ((1 - purchase_indicator[label]) * M),
    f"LeftoverUnitsUsagePercentConstraint_{label}"
  )

# Objective function: Minimize total leftover units
prob += pulp.lpSum([leftover_units[label] for label in leftover_units]), "MinimizeTotalLeftoverUnits"

# Solve the problem
prob.solve()

print("Configuration:")
print(f"  min_stacks={min_stacks}")
print(f"  max_stacks={max_stacks}")
print(f"  min_usage_pct={min_usage_pct}")
print(f"  M={M}")

# Check the solution status
status = pulp.LpStatus[prob.status]
print("\nStatus:", pulp.LpStatus[prob.status])

if status != 'Optimal':
  print(f"\nProblem could not be solved optimally.")
else:
  # Print the results
  table = []
  total_cost = 0

  for supp in supplements:
    label = supp['label']
    daily_dose = supp['daily_dose']
    bottle_size = supp['bottle_size']
    current_stock = supp['current_stock']
    bottle_cost = supp['bottle_cost']

    purchased_bottles = int(bottles_purchased[label].varValue)
    total_units_available = current_stock + purchased_bottles * bottle_size
    total_units_needed = stacks.varValue * daily_dose
    leftover = leftover_units[label].varValue
    # leftover_pct = leftover / bottle_size * 100
    # usage_pct = (1 - (leftover / bottle_size)) * 100

    cost = purchased_bottles * bottle_cost
    total_cost += cost

    if purchased_bottles > 0:
      # Calculate leftover and usage percentage relative to a purchased bottle
      leftover_pct = f"{leftover / bottle_size * 100:.2f}%"
      usage_pct = f"{(1 - (leftover / bottle_size)) * 100:.2f}%"
    else:
      # No bottles purchased, leftover_pct and usage_pct should be N/A
      leftover_pct = "N/A"
      usage_pct = "N/A"

    table.append([
      label,
      daily_dose,
      current_stock,
      purchased_bottles,
      bottle_size,
      total_units_available,
      total_units_needed,
      leftover,
      leftover_pct,
      usage_pct,
      f"${cost:.2f}" if purchased_bottles else "N/A",
    ])

  headers = [
    "Supplement",
    "Daily Dose",
    "Current Stock",
    "Bottles Purchased",
    "Bottle Size",
    "Total Units Available",
    "Total Units Needed",
    "Leftover Units",
    "Leftover %",
    "Usage %",
    "Cost"
  ]

  print(f"\n{tabulate(table, headers=headers)}")

  print(f"\nTotal Cost: ${total_cost:.2f}")

  print(f"\nOptimal number of stacks (days): {int(stacks.varValue)}")

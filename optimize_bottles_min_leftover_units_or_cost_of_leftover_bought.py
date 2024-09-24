# TODO: Add an optional constraint for free shipping (>$80)
#   # Set to True to require free shipping (total cost must be > $80)
#   require_free_shipping = True
#
#   # Compute total cost of bottles purchased
#   total_cost = lpSum(supp['bottle_cost'] * x[supp['label']] for supp in supplements)
#
#   # Compute total cost of unused supplements
#   unused_cost = lpSum((supp['bottle_cost'] / supp['bottle_size']) * unused_units[supp['label']] for supp in supplements)
#
#   # Conditional constraint: Require free shipping if the total cost must be greater than $80
#   if require_free_shipping:
#     problem += total_cost >= 80

# TODO: Add an optional constraint to enforce weekly packs?
#   # Set to True to enforce weekly packs (s must be divisible by 7)
#   enforce_weekly_packs = False

#   # Conditional variable: k Number of Weeks (only used if weekly packs are enforced)
#   if enforce_weekly_packs:
#     k = LpVariable('k', lowBound=0, cat='Integer')
#
#   # Conditional constraint: Ensure that s is divisible by 7 (s = 7 * k) if weekly packs are enforced
#   if enforce_weekly_packs:
#     problem += stacks == 7 * k

import argparse

import pulp
from tabulate import tabulate
from enum import Enum

from supplements_data import supplements

class OptimizationMode(Enum):
  LEFTOVER_UNITS = "leftover_units"
  LEFTOVER_UNITS_COST = "leftover_units_cost"
  ADJUSTED_LEFTOVER_UNITS = "adjusted_leftover_units"
  ADJUSTED_LEFTOVER_UNITS_COST = "adjusted_leftover_units_cost"

# Map CLI argument to OptimizationMode enum
def get_mode_enum(mode_str):
  if mode_str == "leftover_units":
    return OptimizationMode.LEFTOVER_UNITS
  elif mode_str == "leftover_units_cost":
    return OptimizationMode.LEFTOVER_UNITS_COST
  elif mode_str == "adjusted_leftover_units":
    return OptimizationMode.ADJUSTED_LEFTOVER_UNITS
  elif mode_str == "adjusted_leftover_units_cost":
    return OptimizationMode.ADJUSTED_LEFTOVER_UNITS_COST
  else:
    raise ValueError(f"Unknown mode: {mode_str}")

# Define CLI arguments
def parse_args():
  parser = argparse.ArgumentParser(description="Optimize supplement purchasing strategy.")

  parser.add_argument(
    '--min-stacks', type=int, default=7 * 4,
    help="Minimum number of stacks (default: 7 * 4 days)"
  )
  parser.add_argument(
    '--max-stacks', type=int, default=7 * 4 * 2,
    help="Maximum number of stacks (default: 7 * 4 * 2 days)"
  )
  mode_arg_choices = [
    'leftover_units',
    'leftover_units_cost',
    'adjusted_leftover_units',
    'adjusted_leftover_units_cost'
  ]
  parser.add_argument(
    '--mode', type=str, choices=mode_arg_choices, default='leftover_units',
    help=f"Optimization mode (default: 'leftover_units_cost')"
  )
  # parser.add_argument(
  #   '--require-free-shipping', action='store_true',
  #   help="Optional: Require free shipping if total cost exceeds $80"
  # )
  # parser.add_argument(
  #   '--enforce-weekly-packs', action='store_true',
  #   help="Optional: Enforce weekly packs (stacks divisible by 7)"
  # )

  return parser.parse_args()

# Main function
def main():
  args = parse_args()

  # Parameters from CLI arguments
  min_stacks = args.min_stacks     # Minimum number of stacks (days)
  max_stacks = args.max_stacks     # Maximum number of stacks (days)
  mode = get_mode_enum(args.mode)
  # require_free_shipping = args.require_free_shipping
  # enforce_weekly_packs = args.enforce_weekly_packs

  # Define a big M constant
  M = 1e6

  # Initialize the LP problem
  prob = pulp.LpProblem("SupplementPurchasing", pulp.LpMinimize)

  # Decision variable: number of stacks (integer between min_stacks and max_stacks)
  stacks = pulp.LpVariable("Stacks", lowBound=min_stacks, upBound=max_stacks, cat='Integer')

  # Decision variables: number of bottles to purchase (integer >=0) and leftover units (continuous >=0) for each supplement
  bottles_purchased = {supp['label']: pulp.LpVariable(f"BottlesPurchased_{supp['label']}", lowBound=0, cat='Integer') for supp in supplements}
  leftover_units = {supp['label']: pulp.LpVariable(f"LeftoverUnits_{supp['label']}", lowBound=0, cat='Continuous') for supp in supplements}
  leftover_units_cost = {supp['label']: pulp.LpVariable(f"LeftoverUnitsCost_{supp['label']}", lowBound=0, cat='Continuous') for supp in supplements}

  # Introduce binary variables per supplement
  did_purchase = {supp['label']: pulp.LpVariable(f"DidPurchaseBottle_{supp['label']}", cat='Binary') for supp in supplements}

  # Adjusted leftover units and cost
  adjusted_leftover_units = {supp['label']: pulp.LpVariable(f"AdjustedLeftoverUnits_{supp['label']}", lowBound=0, cat='Continuous') for supp in supplements}
  adjusted_leftover_units_cost = {supp['label']: pulp.LpVariable(f"AdjustedLeftoverUnitsCost_{supp['label']}", lowBound=0, cat='Continuous') for supp in supplements}

  # TODO
  # # Optional constraint for free shipping (>$80)
  # if require_free_shipping:
  #   total_cost = pulp.lpSum(bottles_purchased[supp['label']] * supp['bottle_cost'] for supp in supplements)
  #   prob += total_cost >= 80, "FreeShippingConstraint"

  # TODO
  # # Optional constraint to enforce weekly packs (divisible by 7)
  # if enforce_weekly_packs:
  #   weekly_packs = pulp.LpVariable('k', lowBound=0, cat='Integer')
  #   prob += stacks == 7 * k, "WeeklyPacksConstraint"

  # Constraints and Objective Function

  for supp in supplements:
    label = supp['label']
    daily_dose = supp['daily_dose']
    bottle_size = supp['bottle_size']
    bottle_cost = supp['bottle_cost']
    current_stock = supp['current_stock']

    # Ensure total available units cover the required units
    prob += (
      current_stock + (bottles_purchased[label] * bottle_size) >= stacks * daily_dose,
      f"Balance_{label}"
    )

    # Define leftover units
    prob += (
      leftover_units[label] == current_stock + (bottles_purchased[label] * bottle_size) - (stacks * daily_dose),
      f"LeftoverUnits_{label}"
    )

    # Ensure leftover units are non-negative
    # TODO: Since we set lowBound=0 when defining it, I'm not sure we explicitly need to add this constraint here?
    prob += (
      leftover_units[label] >= 0,
      f"NonNegativeLeftover_{label}"
    )

    # Define leftover units cost
    prob += (
      leftover_units_cost[label] == leftover_units[label] * (bottle_cost / bottle_size),
      f"LeftoverUnitsCost_{label}"
    )

    # Link bottles purchased to the purchase flag
    prob += bottles_purchased[label] <= did_purchase[label] * M, f"BottlesPurchasedLimit_{label}"

    # Adjust leftover units based on the purchase flag
    prob += adjusted_leftover_units[label] <= leftover_units[label], f"AdjustedLeftoverUnitsUpper_{label}"
    prob += adjusted_leftover_units[label] <= did_purchase[label] * M, f"AdjustedLeftoverUnitsLimit_{label}"
    prob += adjusted_leftover_units[label] >= leftover_units[label] - ((1 - did_purchase[label]) * M), f"AdjustedLeftoverUnitsLower_{label}"

    # Define adjusted leftover units cost
    prob += (
        adjusted_leftover_units_cost[label] == adjusted_leftover_units[label] * (bottle_cost / bottle_size),
        f"AdjustedLeftoverUnitsCost_{label}"
    )

  # Set the optimization objective based on the selected mode
  if mode == OptimizationMode.LEFTOVER_UNITS:
    # Objective function: Minimize total leftover units
    prob += pulp.lpSum([leftover_units[label] for label in leftover_units]), "MinimizeTotalLeftoverUnits"
  elif mode == OptimizationMode.LEFTOVER_UNITS_COST:
    # Objective function: Minimize total cost of leftover units
    prob += pulp.lpSum([leftover_units_cost[label] for label in leftover_units]), "MinimizeTotalLeftoverUnitsCost"
  elif mode == OptimizationMode.ADJUSTED_LEFTOVER_UNITS:
    # Objective function: Minimize total adjusted leftover units
    prob += pulp.lpSum([adjusted_leftover_units[label] for label in adjusted_leftover_units]), "MinimizeTotalAdjustedLeftoverUnits"
  elif mode == OptimizationMode.ADJUSTED_LEFTOVER_UNITS_COST:
    # Objective function: Minimize total cost of adjusted leftover units
    prob += pulp.lpSum([adjusted_leftover_units_cost[label] for label in adjusted_leftover_units]), "MinimizeTotalAdjustedLeftoverUnitsCost"
  else:
    raise ValueError(f"Unknown optimization mode: {mode}")

  # Solve the problem
  prob.solve()

  # TODO: should we iterate over the CLI args here instead of manually hardcoding what we're outputting?
  print("Configuration:")
  print(f"  min_stacks={min_stacks}")
  print(f"  max_stacks={max_stacks}")
  print(f"  mode={mode}")

  # Check the solution status
  status = pulp.LpStatus[prob.status]
  print("\nStatus:", pulp.LpStatus[prob.status])

  if status != 'Optimal':
    print(f"\nProblem could not be solved optimally.")
  else:
    # Print the results
    table = []
    total_cost = 0
    total_leftover_cost = 0
    total_adjusted_leftover_cost = 0

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
      adjusted_leftover = adjusted_leftover_units[label].varValue

      leftover_cost = leftover_units_cost[label].varValue
      adjusted_leftover_cost = adjusted_leftover_units_cost[label].varValue

      total_leftover_cost += leftover_cost
      total_adjusted_leftover_cost += adjusted_leftover_cost

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
        adjusted_leftover,
        leftover_pct,
        usage_pct,
        f"${bottle_cost:.2f}",
        f"${cost:.2f}",
        f"${leftover_cost:.2f}",
        f"${adjusted_leftover_cost:.2f}",
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
      "Adjusted Leftover Units",
      "Leftover %",
      "Usage %",
      "Bottle Cost",
      "Total Cost",
      "Leftover Cost",
      "Adjusted Leftover Cost",
    ]

    print(f"\nFull Results Table:\n")
    print(f"{tabulate(table, headers=headers)}")

    # Filter for entries where bottles were purchased
    filtered_table = [row for row in table if row[3] > 0]  # row[3] corresponds to 'Bottles Purchased'

    # Print the filtered table with only purchased bottles
    if filtered_table:
      print(f"\nFiltered Table (Bottles to purchase):\n")
      print(f"{tabulate(filtered_table, headers=headers)}")
    else:
      print("\nNo bottles to purchase in the solution.")

    print(f"\nTotal Cost: ${total_cost:.2f}")
    print(f"Total Leftover Cost: ${total_leftover_cost:.2f}")
    print(f"Total Adjusted Leftover Cost: ${total_adjusted_leftover_cost:.2f}")

    print(f"\nOptimal number of stacks (days): {int(stacks.varValue)} (approx {stacks.varValue / 7:.2f} weeks)")

if __name__ == "__main__":
  main()

# ChatGPT ref:
#   https://chatgpt.com/c/66eb75d7-89cc-8008-a8e8-25c6aff37d83
#   etc

# TODO: Once we have calculated the max stacks, we then need to try and minimize the leftover unused units

import pulp
from tabulate import tabulate

from supplements_data import supplements

# Parameters
min_stacks = 0  # Minimum number of stacks (days)
max_stacks = 365  # Maximum number of stacks (days)
min_usage_pct = 0.1  # Minimum usage percentage of the last bottle

# Initialize the LP problem
prob = pulp.LpProblem("SupplementPurchasing", pulp.LpMaximize)

# Decision variable: number of stacks (integer between min_stacks and max_stacks)
stacks = pulp.LpVariable("Stacks", lowBound=min_stacks, upBound=max_stacks, cat='Integer')

# Decision variables for the number of bottles to buy (integer variables)
buy_bottles = {s["label"]: pulp.LpVariable(f"BuyBottles_{s['label']}", lowBound=0, cat='Integer') for s in supplements}

# Decision variable: Units used from bought bottles
used_units_from_bought = {s["label"]: pulp.LpVariable(f"UsedUnits_{s['label']}", lowBound=0, cat='Continuous') for s in supplements}

# Decision variable: Number of fully used bottles (integer)
fully_used_bottles = {s["label"]: pulp.LpVariable(f"FullyUsedBottles_{s['label']}", lowBound=0, cat='Integer') for s in supplements}

# Decision variable: Units used in the last bottle (continuous)
units_used_in_last_bottle = {s["label"]: pulp.LpVariable(f"UnitsUsedLastBottle_{s['label']}", lowBound=0, upBound=s["bottle_size"], cat='Continuous') for s in supplements}

# Decision variable: Whether the last bottle was used (TODO: can we name this better?)
last_bottle_used = {s["label"]: pulp.LpVariable(f"LastBottleUsed_{s['label']}", cat='Binary') for s in supplements}

# Objective function: maximize the number of stacks
prob += stacks, "TotalStacks"

# Constraints
for s in supplements:
    label = s["label"]
    daily_dose = s["daily_dose"]
    bottle_size = s["bottle_size"]
    current_stock = s["current_stock"]

    required_units = stacks * daily_dose
    total_bought_units = buy_bottles[label] * bottle_size
    total_available_units = current_stock + total_bought_units

    # Ensure variables are non-negative integers
    prob += stacks >= 0, f"StacksNonNegative_{label}"
    prob += daily_dose >= 0, f"DoseNonNegative_{label}"
    prob += required_units >= 0, f"RequiredUnitsNonNegative_{label}"
    prob += buy_bottles[label] >= 0, f"BuyBottlesNonNegative_{label}"
    prob += used_units_from_bought[label] >= 0, f"UsedUnitsNonNegative_{label}"
    prob += fully_used_bottles[label] >= 0, f"FullyUsedBottlesNonNegative_{label}"

    # Bottle constraints/relationships
    prob += buy_bottles[label] == fully_used_bottles[label] + last_bottle_used[label], f"BottleCountConstraint_{label}"
    prob += fully_used_bottles[label] <= buy_bottles[label], f"FullyUsedBottlesUpperBound_{label}"

    # Ensure available units cover required units
    prob += total_available_units >= required_units, f"UnitsConstraint_{label}"

    # Units used from bought bottles must meet the demand beyond current stock, and cannot exceed what's actually bought
    prob += used_units_from_bought[label] == required_units - current_stock, f"UsedUnitsCoversRequired_{label}"
    prob += used_units_from_bought[label] == (fully_used_bottles[label] * bottle_size) + units_used_in_last_bottle[label], f"UsedUnitsConstraint_{label}"
    prob += used_units_from_bought[label] <= total_bought_units, f"UsedUnitsUpperBound1_{label}"
    prob += used_units_from_bought[label] <= total_available_units, f"UsedUnitsUpperBound2_{label}"

    # Constraints linking units_used_in_last_bottle with last_bottle_used
    prob += units_used_in_last_bottle[label] >= last_bottle_used[label] * (min_usage_pct * bottle_size), f"MinUsageUnitsConstraint_{label}"
    prob += units_used_in_last_bottle[label] <= last_bottle_used[label] * bottle_size, f"MaxUnitsUsedLastBottle_{label}"

# Solve the problem
prob.solve()

# Check the solution status
status = pulp.LpStatus[prob.status]
if status != 'Optimal':
    print(f"Problem could not be solved optimally. Status: {status}")
else:
    # Prepare output data
    output_data = []
    total_cost = 0
    optimal_stacks = int(stacks.varValue)

    for s in supplements:
      label = s["label"]
      bottle_cost = s["bottle_cost"]
      bottle_size = s["bottle_size"]
      daily_dose = s["daily_dose"]
      current_stock = s["current_stock"]

      # Get the value of relevant PuLP variables
      bought_bottles = int(buy_bottles[label].varValue)
      used_units_from_bought_bottles = int(used_units_from_bought[label].varValue)
      fully_used_bottles_value = int(fully_used_bottles[label].varValue)
      units_used_in_last_bottle_value = int(units_used_in_last_bottle[label].varValue)

      # Calculate the total available units and leftover units directly from PuLP variables
      total_available_units = int(current_stock + used_units_from_bought_bottles)
      total_required_units = int(optimal_stacks * daily_dose)
      leftover_units = total_available_units - total_required_units

      # Usage percentage of the last bottle (if any bottles are bought)
      if bought_bottles > 0:
          usage_pct_last_bottle = (units_used_in_last_bottle_value / bottle_size) * 100
          usage_pct_display = f"{usage_pct_last_bottle:.2f}%"
      else:
          usage_pct_display = "N/A"

      if bought_bottles > 0 and units_used_in_last_bottle_value > 0:
          usage_pct_last_bottle = (units_used_in_last_bottle_value / bottle_size) * 100
          usage_pct_display = f"{usage_pct_last_bottle:.2f}%"
      else:
          usage_pct_display = "N/A"

      # Calculate the combined bottle cost
      combined_bottle_cost = bought_bottles * bottle_cost

      # Add this supplement's data to the output
      output_data.append({
          "Supplement": label,
          "Bottles to Buy": bought_bottles,
          "Bottle Cost": f"${bottle_cost:.2f}",
          "Combined Bottle Cost": f"${combined_bottle_cost:.2f}",
          "Units per Bottle": bottle_size,
          "Fully used bottles": fully_used_bottles_value,
          "Starting stock": current_stock,
          "Total available units": total_available_units,
          "Total required units": total_required_units,
          "Leftover Units": leftover_units,
          "Used units from bought bottles": used_units_from_bought_bottles,
          "Used from last bottle": units_used_in_last_bottle_value,
          "Usage % of Last Bottle": usage_pct_display
      })

      # Increment total cost
      total_cost += combined_bottle_cost

    # Display the results
    print("Configuration:")
    print(f"  Minimum allowed number of daily stacks: {min_stacks}")
    print(f"  Maximum allowed number of daily stacks: {max_stacks}")
    print(f"  Minimum usage percentage of the last bottle: {min_usage_pct * 100}%")

    print(f"\nOptimal Number of Stacks (Days): {optimal_stacks}\n")

    print(tabulate(output_data, headers="keys", tablefmt="simple"))

    print(f"\nTotal Cost: ${total_cost:.2f}")

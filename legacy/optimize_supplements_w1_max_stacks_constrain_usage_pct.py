# ChatGPT ref: https://chatgpt.com/c/66e92d13-cd4c-8008-a055-b96bc7497791

import pulp
from tabulate import tabulate

from supplements_data import supplements

# Parameters
min_stacks = 0  # Minimum number of stacks (days)
max_stacks = 365  # Maximum number of stacks (days)
min_usage_pct = 0.8  # Minimum usage percentage of bought bottle units

# Initialize the LP problem
prob = pulp.LpProblem("SupplementPurchasing", pulp.LpMaximize)

# Decision variable: number of stacks (integer between min_stacks and max_stacks)
stacks = pulp.LpVariable("Stacks", lowBound=min_stacks, upBound=max_stacks, cat='Integer')

# Decision variables for the number of bottles to buy (integer variables)
buy_bottles = {
    s["label"]: pulp.LpVariable(f"BuyBottles_{s['label']}", lowBound=0, cat='Integer') for s in supplements
}

# Objective function: maximize the number of stacks
prob += stacks, "TotalStacks"

# Constraints
for s in supplements:
    label = s["label"]
    daily_dose = s["daily_dose"]
    bottle_size = s["bottle_size"]
    current_stock = s["current_stock"]

    # Total required units for this supplement
    required_units = stacks * daily_dose

    # Total bought units for this supplement
    total_bought_units = buy_bottles[label] * bottle_size

    # Total available units after purchasing
    available_units = current_stock + total_bought_units

    # Constraint: Available units must cover required units
    prob += available_units >= required_units, f"UnitsConstraint_{label}"

    # Calculate units needed from bought bottles
    units_needed_from_bought = required_units - current_stock

    # Ensure units_needed_from_bought is at least 0
    # Introduce a non-negative variable to represent max(required_units - current_stock, 0)
    units_needed_from_bought_var = pulp.LpVariable(f"UnitsNeeded_{label}", lowBound=0, cat='Continuous')
    prob += units_needed_from_bought_var >= required_units - current_stock, f"UnitsNeededMin_{label}"
    prob += units_needed_from_bought_var >= 0, f"UnitsNeededNonNeg_{label}"

    # Enforce minimum usage percentage if buying new bottles
    prob += units_needed_from_bought_var >= min_usage_pct * total_bought_units, f"UsageConstraint_{label}"

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
    for s in supplements:
        label = s["label"]
        daily_dose = s["daily_dose"]
        bottle_size = s["bottle_size"]
        current_stock = s["current_stock"]
        bottle_cost = s["bottle_cost"]

        bought_bottles = int(pulp.value(buy_bottles[label]))
        total_bought_units = bought_bottles * bottle_size
        total_available_units = current_stock + total_bought_units

        required_units = int(pulp.value(stacks)) * daily_dose
        used_units_from_bought = max(required_units - current_stock, 0)
        leftover_units = max(total_available_units - required_units, 0)

        # Calculate usage % for the last bottle
        # usage_percentage = (used_units_from_bought / total_bought_units * 100) if bought_bottles > 0 else 0.0
        fully_used_bottles = used_units_from_bought // bottle_size
        remaining_units_in_last_bottle = used_units_from_bought % bottle_size
        usage_percentage_last_bottle = (
            (remaining_units_in_last_bottle / bottle_size) * 100 if remaining_units_in_last_bottle > 0 else 100.0
        ) if bought_bottles > 0 else 0.0

        total_cost_supplement = bought_bottles * bottle_cost
        total_cost += total_cost_supplement

        output_data.append({
            "Supplement": label,
            "Bottles to Buy": bought_bottles,
            "Bottle Cost": f"${bottle_cost:.2f}",
            "Combined Bottle Cost": f"${bought_bottles * bottle_cost:.2f}",
            "Units per Bottle": bottle_size,
            "Leftover Units": leftover_units,
            # "Usage %": f"{usage_percentage:.2f}%" if bought_bottles > 0 else "N/A"
            "Usage % of Last Bottle": f"{usage_percentage_last_bottle:.2f}%" if bought_bottles > 0 else "N/A"
        })

    # Display the results
    # print(f"Enforce weekly packs: {enforce_weekly_packs}")
    # print(f"Require free shipping: {require_free_shipping}")
    # print(f"Objective function weights: w1={w1}, w2={w2}, w3={w3}")
    print("Configuration:")
    print(f"  Minimum allowed number of daily stacks: {min_stacks}")
    print(f"  Maximum allowed number of daily stacks: {max_stacks}")
    print(f"  Minimum usage percentage of bought bottle units: {min_usage_pct}")
    # print(f"Optimal number of daily stacks: {int(s.varValue)}")

    print(f"\nOptimal Number of Stacks (Days): {int(pulp.value(stacks))}\n")

    print(tabulate(output_data, headers="keys", tablefmt="simple"))

    print(f"\nTotal Cost: ${total_cost:.2f}")

    # print(f"Total cost of bottles purchased: ${total_cost.value():.2f}")
    # print(f"Total cost of unused supplements: ${unused_cost.value():.2f}")

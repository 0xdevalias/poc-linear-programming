# ChatGPT ref: https://chatgpt.com/c/66ebad21-42c8-8008-b192-a651f6a6a9c5

# TODO: I'm not sure if this is actually working properly currently..

import math
from functools import reduce
from tabulate import tabulate

from supplements_data import supplements

# Set a maximum reference period (e.g., 360 days)
max_period = 365

# Function to calculate LCM of two numbers
def lcm(a, b):
  return abs(a * b) // math.gcd(a, b)

# Function to calculate LCM for a list of numbers
def lcm_multiple(numbers):
  return reduce(lcm, numbers)

# Calculate days of supply for each supplement (how long one bottle lasts)
for supplement in supplements:
  supplement["days_supply"] = supplement["bottle_size"] // supplement["daily_dose"]

# Extract the list of days_supply for LCM calculation
days_supplies = [supplement["days_supply"] for supplement in supplements]

# Calculate the overall LCM for all the supplements
overall_lcm = lcm_multiple(days_supplies)
capped_lcm = min(overall_lcm, max_period)

for supplement in supplements:
  # Calculate how many bottles are needed for each supplement to last the overall LCM period
  # supplement["bottles_needed"] = overall_lcm / supplement["days_supply"]
  # supplement["bottles_needed_capped"] = capped_lcm / supplement["days_supply"]
  supplement["bottles_needed"] = math.ceil(overall_lcm / supplement["days_supply"])
  supplement["bottles_needed_capped"] = math.ceil(capped_lcm / supplement["days_supply"])

  # Calculate total units consumed and excess leftover units for each supplement
  total_units_provided = supplement["bottles_needed"] * supplement["bottle_size"]
  total_units_provided_capped = supplement["bottles_needed_capped"] * supplement["bottle_size"]

  total_units_consumed = supplement["daily_dose"] * overall_lcm
  total_units_consumed_capped = supplement["daily_dose"] * capped_lcm

  supplement["leftover_units"] = total_units_provided - total_units_consumed
  supplement["leftover_units_capped"] = total_units_provided_capped - total_units_consumed_capped

# # Output the results
# for supplement in supplements:
#   print(f"{supplement['label']}: Needs {supplement['bottles_needed']} bottles to cover {overall_lcm} days.")

# Output the results
table_data = [
  [
    supplement["label"],
    supplement["daily_dose"],
    supplement["bottle_size"],
    supplement["days_supply"],
    supplement["bottles_needed"],
    supplement["leftover_units"],
    supplement["bottles_needed_capped"],
    supplement["leftover_units_capped"]
  ]
  for supplement in supplements
]
table_headers = [
  "Supplement",
  "Daily Dose",
  "Bottle Size",
  "Days per Bottle",
  "Bottles Needed",
  "Leftover Units",
  "Bottles Needed (capped)",
  "Leftover Units (capped)"
]
print(tabulate(table_data, table_headers, tablefmt="simple"))

print("\nConfiguration:")
print(f"  max_period: {max_period}")

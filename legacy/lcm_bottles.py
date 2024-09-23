# ChatGPT ref: https://chatgpt.com/c/66ebad21-42c8-8008-b192-a651f6a6a9c5

import math
from functools import reduce
from tabulate import tabulate

from supplements_data import supplements

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

# Calculate how many bottles are needed for each supplement to last the overall LCM period
for supplement in supplements:
  supplement["bottles_needed"] = overall_lcm // supplement["days_supply"]

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
    supplement["bottles_needed"]
  ]
  for supplement in supplements
]
table_headers = ["Supplement", "Daily Dose", "Bottle Size", "Days per Bottle", "Bottles Needed"]
print(tabulate(table_data, table_headers, tablefmt="simple"))

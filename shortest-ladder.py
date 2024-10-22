# Playing with Neighbour’s Ladder (Applied Optimization) [10 marks]
#   Our neighbour is asking us for the length of the shortest ladder that is able to reach the house by
#   clearing the 8 meters high fence located three meters away from his house (see figure below):
#
#   Assume that the vertical wall of the house and the horizontal ground have infinite extent.
#
#   [hint: the best variable is an angle between the ladder and the horizontal ground]

# ChatGPT: https://chatgpt.com/c/6715fba2-859c-8008-b628-da04528199a7

# Note: This is an example of non-linear optimisation
#   SLSQP = Sequential Least Squares Programming
#     https://en.wikipedia.org/wiki/Sequential_quadratic_programming

# Note: This version was based on using some equations we had already manually calculated..
# see shortest-ladder-2.py for a version that attempts to stick closer to the original problem
# description without first relying on manual calculations.

import numpy as np
from scipy.optimize import minimize

# Objective function: Ladder length L as a function of theta
def ladder_length(theta):
    return (3 / np.cos(theta)) + (8 / np.sin(theta))

# Constraints: theta must satisfy the fence clearance condition
def fence_constraint(theta):
    # Ensure that tan(theta)*(x0 - 3) >= 8
    # x0 = 3 + 8 / tan(theta)
    x0 = 3 + 8 / np.tan(theta)
    return x0 - 3  # x0 must be greater than or equal to 3

# Initial guess for theta (in radians)
initial_theta = np.radians(45)  # 45 degrees

# Bounds for theta: between a small positive value and (pi/2) - a small value
theta_bounds = [(np.radians(1), np.radians(89))]

# Define the constraint in a form suitable for scipy.optimize
constraints = {
    'type': 'ineq',  # Inequality constraint
    'fun': fence_constraint
}

# Perform the optimization
result = minimize(
    ladder_length,
    x0=initial_theta,
    method='SLSQP',
    bounds=theta_bounds,
    constraints=constraints
)

# Extract the optimal theta and ladder length
optimal_theta = result.x[0]
min_ladder_length = result.fun

# Convert theta to degrees for interpretation
optimal_theta_degrees = np.degrees(optimal_theta)

print(f"Optimal angle theta: {optimal_theta_degrees:.2f} degrees")
print(f"Minimum ladder length L: {min_ladder_length:.2f} meters")



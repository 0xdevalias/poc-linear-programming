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

# Ref: https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.minimize.html

import numpy as np
from scipy.optimize import minimize

# Objective function: Length of the ladder L to minimize
def ladder_length(vars):
    x0, yB = vars  # Unpack variables

    # In the setup, the ladder forms a right triangle with:
    #
    # - x0 as the horizontal distance from the base of the ladder (on the ground) to the wall.
    # - yB as the vertical distance from the ground to the top of the ladder (the height where the ladder touches the wall).
    #
    # Since the ladder is leaning against the wall and the ground, it forms a right triangle where:
    #
    # - L is the hypotenuse (the length of the ladder).
    # - x0 is the horizontal distance from the wall to the base of the ladder.
    # - yB is the height where the ladder touches the wall.
    #
    # This setup directly leads to the Pythagorean theorem, which relates the lengths of the legs of a right triangle to the hypotenuse.
    #
    # Pythagorean theorem states that, for a right triangle:
    #   L^2 = x0^2 + yB^2
    #
    # Which we can re-arrange in terms of L to get:
    #   L = sqrt(x0^2 + yB^2)
    return np.sqrt(x0**2 + yB**2)

# Constraint function: Ladder must clear the fence at x = 3 meters
def fence_clearance(vars):
    x0, yB = vars

    # The code includes a check for x0 = 0 to avoid division by zero, although this case
    # shouldn't occur because we set a lower bound on x0 >= 3
    if x0 == 0:
        return -np.inf  # Prevent division by zero

    # The ladder forms a straight line from the point where it touches the wall at a
    # height yB to the point where it touches the ground at distance x0
    #
    # The equation of a line in slope-intercept form is given by:
    #
    # y = mx+b
    #
    # where:
    #
    # - m is the slope of the line
    # - b is the y-intercept
    #
    # However, since the ladder touches the ground at (x0, 0) and the wall at (0, yB) the equation
    # of the ladder can be written in point-slope form:
    #
    # y = yB * (1 - (x / x0))
    #
    # This equation represents the height y at any horizontal position x along the ladder,
    # based on the total height yB where it touches the wall and the distance x0 from the
    # foot of the ladder to the wall.
    #
    # Calculate the height of the ladder at the position of the fence (x=3 meters away from the wall)
    y_fence = yB * (1 - 3 / x0)

    # y at the fence position (x=3) must be at least 8 meters
    #
    # The function returns the difference between the height of the ladder at the fence (y_fence)
    # and the required fence height (8 meters).
    #
    # For the constraint to be satisfied, the return value must be non-negative:
    #   y_fence - 8 >= 0
    # or
    #   y_fence >= 8
    #
    # This constraint ensures that the ladder is always tall enough at the point where it crosses the fence to clear the 8-meter obstacle.
    return y_fence - 8  # Constraint: y_fence - 8 >= 0 AKA y_fence >= 8

# Bounds for the variables
#   Sequence of (min, max) pairs for each element in x. None is used to specify no bound.
bounds = (
    (3, None),  # x0 >= 3 meters (foot of the ladder beyond the fence)
    (0, None)   # yB >= 0 meters (height cannot be negative)
)

# Constraints dictionary
constraints = {
    'type': 'ineq',  # Inequality constraint
    'fun': fence_clearance
}

# Initial guess for x0 and yB
initial_guess = [5, 10]  # Starting values (can be any reasonable numbers)

# Perform the optimization
result = minimize(
    ladder_length,
    x0=initial_guess,
    method='SLSQP',
    bounds=bounds,
    constraints=constraints
)

# Extract the optimal variables and minimum ladder length
optimal_x0, optimal_yB = result.x
min_ladder_length = result.fun

print(f"Optimal foot distance x0: {optimal_x0:.4f} meters")
print(f"Optimal height yB: {optimal_yB:.4f} meters")
print(f"Minimum ladder length L: {min_ladder_length:.4f} meters")

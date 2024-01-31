from pyomo.environ import *
from pyomo.opt import SolverFactory

def main():
    # Create a Pyomo model object
    model = ConcreteModel()
    # Define decision variables
    model.a = Var(within=Integers)
    model.b = Var(within=Integers)
    # Define objective function for mximum total Profit
    model.obj = Objective(expr = 40*model.a + 80*model.b, sense=maximize)
    # create ConstraintList object
    model.constraints = ConstraintList()

    # Define constraints
    model.constraints.add(expr = 2*model.a + 3*model.b <= 105) # Plant
    model.constraints.add(expr = model.a <= 30) # For Product A
    model.constraints.add(expr = model.b <= 20) # For product B
    solver = SolverFactory('glpk')

    # Solve the LP problem and assign output to results
    results = solver.solve(model)
    # Print the optimal values of the number of units for product A and Product B

    print(f"Product A = {model.a.value}")
    print(f"Product B = {model.b.value}")
    print(f"Profit = {model.obj.expr()}")
    return 1

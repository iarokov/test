from pyomo.environ import *
from pyomo.opt import SolverFactory

def basic_energ_arb():
    from pyomo.environ import *

# Define the time periods
T = [1, 2, 3, 4, 5]

# Define the bounds and parameters
gamma_s = 0.9  # Efficiency of storage
q_bar_D = 10   # Upper bound on discharge quantity
q_bar_R = 10   # Upper bound on charge quantity
S_bar = 100    # Upper bound on state of charge
C_d = 20  # Discharge cost
C_r = 15  # Charge cost
r = 0.05  # Discount rate

# Create a Concrete Model
model = ConcreteModel()

# Define the variables
model.q_D = Var(T, within=NonNegativeReals, bounds=(0, q_bar_D))
model.q_R = Var(T, within=NonNegativeReals, bounds=(0, q_bar_R))
model.S = Var(T, within=NonNegativeReals, bounds=(0, S_bar))

# Define the objective function
model.obj = Objective(expr=sum((P_t[t-1] - C_d) * model.q_D[t] - (P_t[t-1] + C_r) * model.q_R[t] for t in T) * exp(-r * t), sense=maximize)

# Define the constraints
model.constraints = ConstraintList()
for t in T:
    if t == 1:
        model.constraints.add(model.S[t] == gamma_s * 0 + gamma_s * model.S[T[-1]] + model.q_R[t] - model.q_D[t])
    else:
        model.constraints.add(model.S[t] == gamma_s * model.S[t-1] + gamma_s * model.S[T[-1]] + model.q_R[t] - model.q_D[t])

# Define the LP form
model.LP_formulation = ConstraintList()
for t in T:
    model.LP_formulation.add(model.q_D[t] <= q_bar_D)
    model.LP_formulation.add(model.q_R[t] <= q_bar_R)
    model.LP_formulation.add(model.S[t] <= S_bar)

# Solve the model
solver = SolverFactory('glpk')
solver.solve(model)

# Display the results
print("Optimal Revenue:", model.obj())
for t in T:
    print(f"Time Period {t}: Charge={model.q_R[t].value}, Discharge={model.q_D[t].value}, State={model.S[t].value}")


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

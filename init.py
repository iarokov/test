from pyomo.environ import *
from pyomo.opt import SolverFactory
import pandas as pd

def basic_energ_arb():


    # Define the bounds and parameters
    gamma_s = 0.9  # Efficiency of storage
    gamma_c = 0.8  # Conversion efficiency
    mu_ru = 0.8    # Average fraction of regulation up offer called upon
    mu_rd = 0.7    # Average fraction of regulation down offer called upon
    q_bar_D = 10   # Upper bound on discharge quantity
    q_bar_R = 10   # Upper bound on charge quantity
    S_bar = 100    # Upper bound on state of charge
    Cd = 3  # Cost of discharging at each time period
    Cr = 4  # Cost of recharging at each time period
    r = 0.05  # Interest rate

    # Create a Concrete Model
    model = ConcreteModel()
    #Load prices 
    df = pd.read_csv('20230901-20240229 CAISO Average Price.csv')
    T = range(1, len(df) + 1)
    num_periods = len(T)


    # Define the variables
    model.q_D = Var(T, within=NonNegativeReals, bounds=(0, q_bar_D))
    model.q_R = Var(T, within=NonNegativeReals, bounds=(0, q_bar_R))
    model.S = Var(T, within=NonNegativeReals, bounds=(0, S_bar))
    # model.q_RU = Var(T, within=NonNegativeReals, bounds=(0, q_bar_R))
    # model.q_RD = Var(T, within=NonNegativeReals, bounds=(0, q_bar_R))
    # model.alpha_ru = Var(within=NonNegativeReals, bounds=(0, 1))
    # model.alpha_rd = Var(within=NonNegativeReals, bounds=(0, 1))
    
    #define gamma through uptime 
    # Calculate the regulation up and down efficiencies
    #model.gamma_ru = model.alpha_ru.value * mu_ru
    #model.gamma_rd = model.alpha_rd.value * mu_rd
    
    # Define the objective function
    model.obj = Objective(expr=sum((df['price'][t-1] - C_d) * model.q_D[t] - (df['price'][t-1] + C_r) * model.q_R[t] for t in T) * exp(-r * t), sense=maximize)
    # objective w regulation
    # Objective(expr=sum((df['price'][t-1] - C_d) * model.q_D[t] - (df['price'][t-1] + C_r) * model.q_R[t] for t in T) * exp(-r * t), sense=maximize)

    

    # Define the constraints
    model.constraints = ConstraintList()
    for t in T:
        if t == 0:
            model.constraints.add(model.S[t] == 0)
            #  model.constraints.add(model.S[t] == gamma_c * model.q_R[t] - model.q_D[t] + gamma_c * gamma_rd * model.q_RD[t] - gamma_ru * model.q_RU[t])
        else:
            model.constraints.add(model.S[t] == gamma_s * model.S[t-1] + gamma_c * model.q_R[t] - model.q_D[t])
            #model.constraints.add(model.S[t] == gamma_s * model.S[t-1] + gamma_c * model.q_R[t] - model.q_D[t] + gamma_c * gamma_rd * model.q_RD[t] - model.gamma_ru * model.q_RU[t])
        model.constraints.add(model.S[t] <= S_bar)
        model.constraints.add(model.q_R[t] <= q_bar_R)
        #model.constraints.add(model.q_R[t] + model.q_RD[t] <= q_bar_R)
        model.constraints.add(model.q_D[t] <= q_bar_D)
        #model.constraints.add(model.q_D[t] + model.q_RU[t] <= q_bar_D)
        #model.constraints.add(model.alpha_ru + model.alpha_rd == 1)
        #model.constraints.add(0 <= model.alpha_ru <= 1)
        #model.constraints.add(0 <= model.alpha_rd <= 1) 

    

    #do we need these (?) no because
    # we define all the constraints itteravely we do not 
    # need vector form unless performance issue
    # Ar = [[gamma_c * gamma_s**(j-i) if i <= j else 0 for i in range(num_periods)] for j in range(num_periods)]
    # As = [[-1* gamma_s**(j-i) if i <= j else 0 for i in range(num_periods)] for j in range(num_periods)]
    # If we need follow constraints As = [Ad|Ar] Constraint1: As*x= S  A =  [-As/As] b = [ 0 0 0 S S S S ] Constraint2: A*x < b
    # Solve the model                                                                                         
    solver = SolverFactory('glpk')
    solver.solve(model)

    # Display the results
    print("Optimal Profit:", model.obj())
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

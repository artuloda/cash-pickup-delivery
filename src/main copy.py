from pulp import LpProblem, LpMinimize, LpVariable, lpSum, LpBinary

# Problem data
n_services = 20  # Total services
n_vehicles = 3  # Number of vehicles
MAX_KM = 150000  # Max kilometers per vehicle per day
MAX_CAPACITY = 1000  # Max vehicle capacity
MAX_STOCK = 5000  # Max depot stock
k1 = 1  # Storage cost within stock limit
k2 = 5  # Storage cost exceeding stock limit

# Example service data
distances = [
    [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160, 170, 180, 190],
    [10, 0, 15, 25, 35, 45, 55, 65, 75, 85, 95, 105, 115, 125, 135, 145, 155, 165, 175, 185],
    [20, 15, 0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160, 170],
    [30, 25, 10, 0, 15, 25, 35, 45, 55, 65, 75, 85, 95, 105, 115, 125, 135, 145, 155, 165],
    [40, 35, 20, 15, 0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150],
    [50, 45, 30, 25, 10, 0, 15, 25, 35, 45, 55, 65, 75, 85, 95, 105, 115, 125, 135, 145],
    [60, 55, 40, 35, 20, 15, 0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130],
    [70, 65, 50, 45, 30, 25, 10, 0, 15, 25, 35, 45, 55, 65, 75, 85, 95, 105, 115, 125],
    [80, 75, 60, 55, 40, 35, 20, 15, 0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110],
    [90, 85, 70, 65, 50, 45, 30, 25, 10, 0, 15, 25, 35, 45, 55, 65, 75, 85, 95, 105],
    [100, 95, 80, 75, 60, 55, 40, 35, 20, 15, 0, 10, 20, 30, 40, 50, 60, 70, 80, 90],
    [110, 105, 90, 85, 70, 65, 50, 45, 30, 25, 10, 0, 15, 25, 35, 45, 55, 65, 75, 85],
    [120, 115, 100, 95, 80, 75, 60, 55, 40, 35, 20, 15, 0, 10, 20, 30, 40, 50, 60, 70],
    [130, 125, 110, 105, 90, 85, 70, 65, 50, 45, 30, 25, 10, 0, 15, 25, 35, 45, 55, 65],
    [140, 135, 120, 115, 100, 95, 80, 75, 60, 55, 40, 35, 20, 15, 0, 10, 20, 30, 40, 50],
    [150, 145, 130, 125, 110, 105, 90, 85, 70, 65, 50, 45, 30, 25, 10, 0, 15, 25, 35, 45],
    [160, 155, 140, 135, 120, 115, 100, 95, 80, 75, 60, 55, 40, 35, 20, 15, 0, 10, 20, 30],
    [170, 165, 150, 145, 130, 125, 110, 105, 90, 85, 70, 65, 50, 45, 30, 25, 10, 0, 15, 25],
    [180, 175, 160, 155, 140, 135, 120, 115, 100, 95, 80, 75, 60, 55, 40, 35, 20, 15, 0, 10],
    [190, 185, 170, 165, 150, 145, 130, 125, 110, 105, 90, 85, 70, 65, 50, 45, 30, 25, 10, 0]
]
demand = [738, 15, 498, 143, 180, 319, 108, 58, 280, 238, -738, -15, -498, -143, -180, -319, -108, -58, -280, -238]

# Decision variables
problem = LpProblem("Cash_Pickup_and_Delivery", LpMinimize)

# Binary decision variable: whether a service is performed by a vehicle
x = LpVariable.dicts("x", [(i, j) for i in range(n_vehicles) for j in range(n_services)], cat=LpBinary)

# Amount of cash carried by a vehicle after servicing a node
load = LpVariable.dicts("load", [(i, j) for i in range(n_vehicles) for j in range(n_services)], lowBound=0)

# Excess depot stock
excess_stock = LpVariable("excess_stock", lowBound=0)

# Objective function: Minimize unperformed services, transportation costs, and storage cost
transport_costs = lpSum(distances[i][j] * x[i, j] for i in range(n_vehicles) for j in range(n_services))
storage_costs = k1 * MAX_STOCK + k2 * excess_stock
unperformed_services = lpSum(1 - lpSum(x[i, j] for i in range(n_vehicles)) for j in range(n_services))

problem += transport_costs + storage_costs + unperformed_services, "Total_Cost"

# Constraints

# 1. Each service must be performed at most once
for j in range(n_services):
    problem += lpSum(x[i, j] for i in range(n_vehicles)) <= 1, f"Service_{j}_performed_once"

# 2. Vehicle capacity constraint
for i in range(n_vehicles):
    for j in range(n_services):
        problem += load[i, j] >= demand[j] * x[i, j], f"Load_balance_{i}_{j}"
        problem += load[i, j] <= MAX_CAPACITY, f"Max_capacity_{i}_{j}"

# 3. Mileage constraint
for i in range(n_vehicles):
    problem += lpSum(distances[j][k] * x[i, k] for k in range(n_services)) <= MAX_KM, f"Max_km_{i}"

# 4. Depot stock constraint
problem += lpSum(demand[j] * lpSum(x[i, j] for i in range(n_vehicles)) for j in range(n_services)) <= MAX_STOCK + excess_stock, "Depot_stock"

# Solve the problem
problem.solve()

# Results
print("Status:", problem.status)
print("Objective Value:", problem.objective.value())
for i in range(n_vehicles):
    for j in range(n_services):
        if x[i, j].value() == 1:
            print(f"Vehicle {i} serves Service {j}")
print("Excess Stock:", excess_stock.value())

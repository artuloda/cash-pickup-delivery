from pulp import LpProblem, LpMinimize, LpVariable, lpSum, LpBinary, LpContinuous

class ExactSolution:
    def __init__(self, context, instance):
        self.context = context
        self.instance = instance
        self.initialize_solution()

    def initialize_solution(self):
        self.routes = [[] for _ in range(self.context.parameters.n_vehicles)]
        self.unserved = set(self.instance.nodes_ids[1:])
        self.remaining_capacity = [self.context.parameters.VEHICLE_CAPACITY] * self.context.parameters.n_vehicles
        self.remaining_distance = [self.context.parameters.MAX_DISTANCE] * self.context.parameters.n_vehicles
        self.current_stock = sum(-min(demand, 0) for demand in self.instance.demands)
        self.total_distance = 0
        self.storage_cost = 0
        self.fitness = 0

    def solve(self):
        nodes = self.instance.nodes_ids
        distances = self.instance.distances
        demands = self.instance.demands
        k1 = 10  # Base storage cost
        k2 = 100  # Additional cost per unit over MAX_STOCK

        # Decision variables
        problem = LpProblem("CashPickupDelivery", LpMinimize)
        
        # Correct initialization of x with all necessary keys
        x = LpVariable.dicts("x", 
                            ((nodes[i], nodes[j], k) for i in range(len(nodes))
                                                   for j in range(len(nodes))
                                                   for k in range(self.context.parameters.n_vehicles)),
                            cat=LpBinary)
        
        u = LpVariable.dicts("u", (i for i in range(1, len(nodes))), lowBound=1)  # u[i] = position of node i in the route

        # Objective function: Minimize unperformed services, total distance, and storage cost
        problem += lpSum(distances[i][j] * x[i, j, k]
                        for i in range(len(nodes))
                        for j in range(len(nodes))
                        for k in range(self.context.parameters.n_vehicles))# \
                # + k2 * max(0, self.current_stock - self.context.parameters.MAX_STOCK) \
                # + k1 * len(self.unserved)  # Penalize unperformed services

        # Add constraints for each vehicle
        for k in range(self.context.parameters.n_vehicles):
            # Distance and capacity constraints
            problem += lpSum(distances[i][j] * x[i, j, k] for i in range(len(nodes)) for j in range(len(nodes))) <= self.context.parameters.MAX_DISTANCE
            problem += lpSum(demands[j] * x[i, j, k] for i in range(len(nodes)) for j in range(1, len(nodes))) <= self.context.parameters.VEHICLE_CAPACITY

            # Ensure each vehicle starts and ends at the depot
            problem += lpSum(x[0, j, k] for j in range(1, len(nodes))) == 1
            problem += lpSum(x[j, 0, k] for j in range(1, len(nodes))) == 1

        # Ensure each customer is visited exactly once
        for j in range(1, len(nodes)):
            problem += lpSum(x[i, j, k] for i in range(len(nodes)) for k in range(self.context.parameters.n_vehicles)) == 1

        # Flow conservation constraints
        for k in range(self.context.parameters.n_vehicles):
            for i in range(len(nodes)):
                problem += lpSum(x[i, j, k] for j in range(len(nodes))) == lpSum(x[j, i, k] for j in range(len(nodes)))

        # Subtour elimination constraints
        for i in range(1, len(nodes)):
            for j in range(1, len(nodes)):
                if i != j:
                    for k in range(self.context.parameters.n_vehicles):
                        problem += u[i] - u[j] + self.context.parameters.VEHICLE_CAPACITY * x[i, j, k] <= self.context.parameters.VEHICLE_CAPACITY - demands[j]

        # Solve the optimization problem
        problem.solve()

        # Check the solution status
        if problem.status != 1:
            print("Problem not solved successfully. Status:", problem.status)

        # Extract routes from the solution
        for k in range(self.context.parameters.n_vehicles):
            for i in range(len(nodes)):
                for j in range(len(nodes)):
                    if x[i, j, k].varValue > 0.5:
                        self.routes[k].append(nodes[j])
                        print(f"Route {k}: {self.routes[k]}")

        # Determine unserved nodes
        served_nodes = {node for route in self.routes for node in route}
        self.unserved = set(nodes) - served_nodes - {0}

        # Calculate remaining capacity and distance for each vehicle
        self.remaining_capacity = [
            self.context.parameters.VEHICLE_CAPACITY - sum(
                demands[i] * (x[i, j, k].varValue or 0) for i in range(1, len(nodes)) for j in range(1, len(nodes))
            )
            for k in range(self.context.parameters.n_vehicles)
        ]

        self.remaining_distance = [
            self.context.parameters.MAX_DISTANCE - sum(
                distances[i][j] * (x[i, j, k].varValue or 0) for i in range(1, len(nodes)) for j in range(1, len(nodes))
            )
            for k in range(self.context.parameters.n_vehicles)
        ]

        # Calculate total distance traveled
        self.total_distance = sum(
            distances[i][j] * (x[i, j, k].varValue or 0)
            for i in range(1, len(nodes)) for j in range(1, len(nodes)) for k in range(self.context.parameters.n_vehicles)
        )

        # Calculate storage cost and overall fitness
        self.storage_cost = sum(self.instance.calculate_storage_cost(demand) for demand in demands[1:])
        self.fitness = self.instance.calculate_total_cost(self.total_distance) + self.storage_cost

        # Print the solution
        self.print_solution()

    def print_solution(self):
        print(f"Routes: {self.routes}")
        print(f"Unserved: {self.unserved}")
        print(f"Remaining capacity: {self.remaining_capacity}")
        print(f"Remaining distance: {self.remaining_distance}")
        print(f"Total distance: {self.total_distance}")
        print(f"Storage cost: {self.storage_cost}")
        print(f"Total cost: {self.fitness}")

    def __str__(self):
        return f"Solution(routes={self.routes}, total_distance={self.total_distance}, storage_cost={self.storage_cost}, total_cost={self.fitness}, unserved={self.unserved})"
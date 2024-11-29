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
        problem = LpProblem("CVRP", LpMinimize)
        x = LpVariable.dicts("x", ((i, j, k) for i in range(len(nodes))
                                for j in range(len(nodes))
                                for k in range(self.context.parameters.n_vehicles)),
                            cat=LpBinary) # x[i][j][k] = 1 if vehicle k travels from node i to node j
        u = LpVariable.dicts("u", (i for i in range(1, len(nodes) + 1)), lowBound=0) # u[i] = position of node i in the route

        # Objective function: Minimize total distance and storage cost
        problem += lpSum(distances[i][j] * x[i, j, k]
                        for i in range(len(nodes))
                        for j in range(len(nodes))
                        for k in range(self.context.parameters.n_vehicles)) \
                   + k2 * max(0, self.current_stock - self.context.parameters.MAX_STOCK if self.current_stock > self.context.parameters.MAX_STOCK else k1)

        # Vehicle constraints 
        for k in range(self.context.parameters.n_vehicles):
            problem += lpSum(distances[i][j] * x[i, j, k] for i in range(len(nodes)) for j in range(len(nodes))) <= self.context.parameters.MAX_DISTANCE
            problem += lpSum(self.instance.demands[j] * x[i, j, k] for i in range(len(nodes)) for j in range(1, len(nodes))) <= self.context.parameters.VEHICLE_CAPACITY

            # Ensure each vehicle starts and ends at the depot
            problem += lpSum(x[0, j, k] for j in range(1, len(nodes))) == 1
            problem += lpSum(x[j, 0, k] for j in range(1, len(nodes))) == 1

        # Ensure service completion
        for j in range(1, len(nodes)):
            for k in range(self.context.parameters.n_vehicles):
                problem += lpSum(x[i, j, k] for i in range(len(nodes))) <= 1

        # Each customer is visited exactly once
        for j in range(1, len(nodes)):
            problem += lpSum(x[i, j, k] for i in range(len(nodes))
                            for k in range(self.context.parameters.n_vehicles)) == 1

        # Flow conservation
        for k in range(self.context.parameters.n_vehicles):
            for i in range(len(nodes)):
                problem += lpSum(x[i, j, k] for j in range(len(nodes))) == \
                        lpSum(x[j, i, k] for j in range(len(nodes)))

        # Subtour elimination (MTZ constraints)
        for i in range(1, len(nodes)):
            for j in range(1, len(nodes)):
                if i != j:
                    for k in range(self.context.parameters.n_vehicles):
                        problem += u[i] - u[j] + self.context.parameters.VEHICLE_CAPACITY * x[i, j, k] <= self.context.parameters.VEHICLE_CAPACITY - self.instance.demands[j]

            
         # Solve the problem
        problem.solve()

        # Debug: Check the status of the problem
        print(f"Problem status: {problem.status}")
        # Check if the problem was solved successfully
        if problem.status != 1:  # 1 corresponds to LpStatusOptimal
            print("Problem not solved successfully. Status:", problem.status)

        # Extract the routes
        for k in range(self.context.parameters.n_vehicles):
            for i in range(len(nodes)):
                for j in range(len(nodes)):
                    if x[i, j, k].varValue > 0.5:
                        self.routes[k].append(nodes[j])

        # Find unserved nodes
        served_nodes = set()
        for route in self.routes:
            served_nodes.update(route)
        self.unserved = set(self.instance.nodes_ids) - served_nodes - {0}  # Exclude depot

        # Calculate remaining capacity and kilometers
        self.remaining_capacity = [
            self.context.parameters.VEHICLE_CAPACITY - sum(
                self.instance.demands[i] * (x[i, j, k].varValue if x[i, j, k].varValue is not None else 0) for i in range(1, len(self.instance.nodes_ids)) for j in range(1, len(self.instance.nodes_ids))
            )
            for k in range(self.context.parameters.n_vehicles)
        ]

        self.remaining_distance = [
            self.context.parameters.MAX_DISTANCE - sum(
                self.instance.distances[i][j] * (x[i, j, k].varValue if x[i, j, k].varValue is not None else 0) for i in range(1, len(self.instance.nodes_ids)) for j in range(1, len(self.instance.nodes_ids))
            )
            for k in range(self.context.parameters.n_vehicles)
        ]

        # Calculate total distance
        self.total_distance = sum(
            self.instance.distances[i][j] * (x[i, j, k].varValue if x[i, j, k].varValue is not None else 0)
            for i in range(1, len(self.instance.nodes_ids)) for j in range(1, len(self.instance.nodes_ids)) for k in range(self.context.parameters.n_vehicles)
        )

        # Calculate storage cost and fitness
        self.storage_cost = sum(
            self.instance.calculate_storage_cost(current_stock) for current_stock in self.instance.demands[1:]
        )
        self.fitness = self.instance.calculate_total_cost(self.total_distance) + self.storage_cost

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
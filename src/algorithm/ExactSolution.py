from pulp import LpProblem, LpMinimize, LpVariable, lpSum, LpBinary, LpContinuous

class ExactSolution:
    def __init__(self, context, instance):
        self.context = context
        self.instance = instance
        self.initialize_solution()


    def initialize_solution(self):
        self.routes = [[] for _ in range(self.context.parameters.n_vehicles)]
        self.unserved = set(self.instance.nodes_ids[1:])
        self.current_capacity = [0] * self.context.parameters.n_vehicles
        self.current_distance = [0] * self.context.parameters.n_vehicles
        self.vehicles_initial_load = [0] * self.context.parameters.n_vehicles
        self.current_stock = self.context.parameters.MAX_STOCK * 0.8
        self.total_distance = 0
        self.storage_cost = 0
        self.fitness = 0


    def solve(self):
        # Include the depot
        nodes = self.instance.nodes_df['Id'].astype(int).to_list()
        distances = self.instance.distances
        demands = self.instance.nodes_df['Items'].astype(int).to_list()
        n_vehicles = self.context.parameters.n_vehicles
        vehicle_capacity = self.context.parameters.VEHICLE_CAPACITY
        n_nodes = len(nodes)
        max_stock = self.context.parameters.MAX_STOCK
        k1 = 10
        k2 = 100
        penalty_cost = 1000000

        # Set up the problem
        problem = LpProblem('cash_pickup_delivery', LpMinimize)

        # Decision variables
        x = LpVariable.dicts("x", ((i, j, k) for i in range(n_nodes)
                                            for j in range(n_nodes)
                                            for k in range(n_vehicles)),
                            cat=LpBinary) # 1 if vehicle k travels from node i to node j, 0 otherwise
        y = LpVariable.dicts("y", (k for k in range(n_vehicles)), cat=LpBinary) # 1 if vehicle k is used, 0 otherwise
        u = LpVariable.dicts("u", (j for j in range(1, n_nodes)), lowBound=0, upBound=vehicle_capacity, cat=LpContinuous) # Amount of demand delivered to node j
        z = LpVariable.dicts("z", (j for j in range(1, n_nodes)), cat=LpBinary) # 1 if node j is visited, 0 otherwise

        # Objective function: Minimize total distance, storage cost, and maximize served nodes
        problem += (
            lpSum(distances[i][j] * x[i, j, k] for i in range(n_nodes) for j in range(n_nodes) for k in range(n_vehicles)) +
            (k1 if self.current_stock <= max_stock else k2 * (self.current_stock - max_stock)) -
            penalty_cost * lpSum(z[j] for j in range(1, n_nodes))
        )

        # Constraints
        # Each node (except the depot) must be visited exactly once
        for j in range(1, n_nodes):
            problem += lpSum(x[i, j, k] for i in range(n_nodes) for k in range(n_vehicles)) == 1

        # Each vehicle must start and end at the depot
        for k in range(n_vehicles):
            problem += lpSum(x[0, j, k] for j in range(1, n_nodes)) == 1
            problem += lpSum(x[j, 0, k] for j in range(1, n_nodes)) == 1

            # Capacity constraint: Ensure vehicle capacity is not exceeded
            problem += lpSum(demands[j] * x[i, j, k] for i in range(n_nodes) for j in range(1, n_nodes)) <= vehicle_capacity * y[k]

            # Mileage constraint: Ensure vehicle mileage is not exceeded
            problem += lpSum(distances[i][j] * x[i, j, k] for i in range(n_nodes) for j in range(1, n_nodes)) <= self.context.parameters.MAX_DISTANCE * y[k]

        # Flow conservation: If a vehicle enters a node, it must leave it
        for k in range(n_vehicles):
            for i in range(n_nodes):
                problem += lpSum(x[i, j, k] for j in range(n_nodes)) == lpSum(x[j, i, k] for j in range(n_nodes))

        # Eliminate subtours MTZ
        for k in range(n_vehicles):
            for i in range(1, n_nodes):
                for j in range(1, n_nodes):
                    if i != j:
                        problem += u[j] >= u[i] + demands[j] * x[i, j, k] - vehicle_capacity * (1 - x[i, j, k])

        # Solve the problem
        status = problem.solve()

        # Check solution status
        if status != 1:
            print("Problem not solved successfully. Status:", status)
            return None

        # Extract routes
        self.routes = [[] for _ in range(n_vehicles)]
        for k in range(n_vehicles):
            for i in range(n_nodes):
                for j in range(n_nodes):
                    if x[i, j, k].varValue > 0.5:
                        self.routes[k].append(nodes[j])

        # Determine unserved nodes
        served_nodes = {node for route in self.routes for node in route}
        self.unserved = set(nodes[1:]) - served_nodes

        # Calculate metrics
        self.current_capacity = [
            vehicle_capacity - sum(demands[nodes.index(j)] for j in route if j != nodes[0])
            for route in self.routes
        ]
        self.current_distance = [
            self.context.parameters.MAX_DISTANCE - sum(distances[nodes.index(route[i])][nodes.index(route[i + 1])] for i in range(len(route) - 1))
            for route in self.routes
        ]
        self.total_distance = sum(
            distances[nodes.index(route[i])][nodes.index(route[i + 1])]
            for route in self.routes for i in range(len(route) - 1)
        )
        self.storage_cost = self.instance.calculate_storage_cost(self.current_stock)
        self.fitness = self.instance.get_solution_value(self.total_distance, self.current_stock, len(self.unserved))

        self.print_solution()


    def print_solution(self):
        print(f"Routes: {self.routes}")
        print(f"Unserved: {self.unserved}")
        print(f"Current capacity: {self.current_capacity}")
        print(f"Current distance: {self.current_distance}")
        print(f"Total distance: {self.total_distance}")
        print(f"Storage cost: {self.storage_cost}")
        print(f"Total cost: {self.fitness}")

    def __str__(self):
        return f"Solution(routes={self.routes}, total_distance={self.total_distance}, storage_cost={self.storage_cost}, total_cost={self.fitness}, unserved={self.unserved})"
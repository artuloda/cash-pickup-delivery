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
        # Exclude the depot's row and column from the distance matrix
        distances = self.instance.distances
        demands = self.instance.nodes_df['Items'].astype(int).to_list()
        depot = 0
        n_vehicles = self.context.parameters.n_vehicles
        max_distance = self.context.parameters.MAX_DISTANCE
        vehicle_capacity = self.context.parameters.VEHICLE_CAPACITY
        max_stock = self.context.parameters.MAX_STOCK
        k1 = 10
        k2 = 100
        penalty_unperformed = 1000
        n_nodes = len(nodes)


        # Create the problem
        problem = LpProblem("CVRP_with_stock", LpMinimize)

        # Decision variables
        x = LpVariable.dicts("x", ((i, j, k) for i in range(n_nodes)
                                            for j in range(n_nodes)
                                            for k in range(n_vehicles)),
                            cat=LpBinary)  # Binary decision: whether vehicle k travels from i to j
        u = LpVariable.dicts("u", (i for i in range(1, n_nodes)), lowBound=0, upBound=vehicle_capacity, cat=LpContinuous)
        stock = LpVariable("stock", lowBound=0, cat=LpContinuous)  # Remaining stock

        # Objective function: Minimize total distance
        problem += lpSum(distances[i][j] * x[i, j, k]
                        for i in range(n_nodes) for j in range(n_nodes) for k in range(n_vehicles))

        # Constraints

        # Ensure each node is visited exactly once (except the depot)
        for j in range(1, n_nodes):
            problem += lpSum(x[i, j, k] for i in range(n_nodes) for k in range(n_vehicles)) == 1

        # Flow conservation for each vehicle
        for k in range(n_vehicles):
            for i in range(n_nodes):
                problem += lpSum(x[i, j, k] for j in range(n_nodes)) == lpSum(x[j, i, k] for j in range(n_nodes))

        # Vehicles start and end at the depot
        for k in range(n_vehicles):
            problem += lpSum(x[0, j, k] for j in range(1, n_nodes)) == 1
            problem += lpSum(x[j, 0, k] for j in range(1, n_nodes)) == 1

        # Vehicle capacity constraint
        for k in range(n_vehicles):
            for i in range(1, n_nodes):
                for j in range(1, n_nodes):
                    if i != j:
                        problem += u[j] >= u[i] + demands[j] * x[i, j, k] - vehicle_capacity * (1 - x[i, j, k])

        # Ensure the stock is properly handled for deliveries (negative demands)
        for k in range(n_vehicles):
            for i in range(1, n_nodes):
                for j in range(1, n_nodes):
                    if demands[j] < 0:  # Delivery point
                        problem += stock >= -demands[j] * x[i, j, k]

        # Total distance constraint for each vehicle
        for k in range(n_vehicles):
            problem += lpSum(distances[i][j] * x[i, j, k] for i in range(n_nodes) for j in range(n_nodes)) <= max_distance

        # Solve the problem
        problem.solve()

        # Check solution status
        if problem.status != 1:
            print("Problem not solved successfully. Status:", problem.status)
            return None
        

        routes = [[] for _ in range(n_vehicles)]
        for k in range(n_vehicles):
            for i in range(n_nodes):
                for j in range(n_nodes):
                    if x[i, j, k].varValue > 0.5:
                        routes[k].append((i, j))
        total_distance = sum(distances[i][j] * x[i, j, k].varValue for i in range(n_nodes)
                            for j in range(n_nodes) for k in range(n_vehicles))
        print(f"Routes: {routes}")
        print(f"Total Distance: {total_distance}")
        print(f"Remaining Stock: {stock.varValue}")

        self.current_stock = stock.varValue

        # Corrected logic to construct final_routes
        self.routes = []
        for route in routes:
            vehicle_route = []
            for i, j in route:
                vehicle_route.append(nodes[i])
            vehicle_route.append(nodes[0])  # Ensure the route returns to the depot
            self.routes.append(vehicle_route)

        # Determine unserved nodes
        served_nodes = {node for route in self.routes for node in route}
        self.unserved = set(nodes[1:]) - served_nodes

        # Calculate metrics
        self.current_capacity = [
            vehicle_capacity - sum(demands[nodes.index(j)] for j in route if j != nodes[0])
            for route in self.routes
        ]
        self.current_distance = [
            max_distance - sum(distances[nodes.index(route[i])][nodes.index(route[i + 1])] for i in range(len(route) - 1))
            for route in self.routes
        ]
        self.total_distance = sum(
            distances[nodes.index(route[i])][nodes.index(route[i + 1])]
            for route in self.routes for i in range(len(route) - 1)
        )
        self.storage_cost = self.instance.calculate_storage_cost(self.current_stock)
        self.fitness = self.total_distance + penalty_unperformed * len(self.unserved) + self.storage_cost

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
# import numpy as np
from algorithm import Instance, Context
# import pulp
from pulp import LpProblem, LpMinimize, LpVariable, lpSum, LpBinary, LpContinuous
class ExactSolution:
    def __init__(self, context: Context, instance: Instance):
        self.context = context
        self.instance = instance
        self.initialize_solution()

    def initialize_solution(self):
        self.routes = [[] for _ in range(self.context.parameters.n_vehicles)]
        self.unserved = set(self.instance.nodes_ids[1:])
        self.remaining_capacity = [self.context.parameters.VEHICLE_CAPACITY] * self.context.parameters.n_vehicles
        self.remaining_km = [self.context.parameters.MAX_KM] * self.context.parameters.n_vehicles
        self.current_stock = sum(-min(demand, 0) for demand in self.instance.demands)  # Initial stock in depot
        self.total_distance = 0
        self.storage_cost = 0
        self.fitness = 0


    def solve(self):
        """
        Solve the cash pickup and delivery problem using MILP.
        """
        nodes = self.instance.nodes_ids
        vehicles = [i for i in range(self.context.parameters.n_vehicles)]
        vehicles_capacity = [self.context.parameters.VEHICLE_CAPACITY] * self.context.parameters.n_vehicles
        stocks = self.instance.demands
        storage_cost = {
            'k1': 10,  # Base storage cost
            'k2': 100  # Additional cost per unit over MAX_STOCK
        }

        # Create the problem
        prob = LpProblem("Cash_Pickup_and_Delivery", LpMinimize)

        # Decision variables
        x = LpVariable.dicts("x", (nodes, nodes, vehicles), 0, 1, LpBinary)
        y = LpVariable.dicts("y", (nodes, vehicles), 0, 1, LpBinary)
        # z = LpVariable.dicts("z", vehicles, 0, None, LpContinuous)

        # Objective function
        prob += lpSum(self.instance.distances[i][j] * x[i][j][k] for i in nodes for j in nodes for k in vehicles) + \
                lpSum(storage_cost * (current_stock - self.context.parameters.MAX_STOCK) for current_stock in stocks if current_stock > self.context.parameters.MAX_STOCK)

        # Constraints
        for k in vehicles:
            # Ensure each vehicle starts and ends at the depot
            prob += lpSum(x[0][j][k] for j in nodes if j != 0) == 1  # Start at depot
            prob += lpSum(x[i][0][k] for i in nodes if i != 0) == 1  # End at depot

            # Flow conservation for each node
            for i in nodes:
                if i != 0:
                    prob += lpSum(x[i][j][k] for j in nodes if j != i) == y[i][k]
                    prob += lpSum(x[j][i][k] for j in nodes if j != i) == y[i][k]

            # Capacity constraint
            prob += lpSum(stocks[i] * y[i][k] for i in nodes) <= vehicles_capacity[k]

            # Distance constraint
            prob += lpSum(self.instance.distances[i][j] * x[i][j][k] for i in nodes for j in nodes) <= self.context.parameters.MAX_KM

        # Ensure each node is visited exactly once
        for i in nodes:
            if i != 0:
                prob += lpSum(y[i][k] for k in vehicles) == 1

        # Solve the problem
        prob.solve()

        # Check if the problem was solved successfully
        if prob.status != 1:  # 1 corresponds to LpStatusOptimal
            print("Problem not solved successfully. Status:", prob.status)
            return

        # Extract the solution
        self.routes = [[] for _ in range(self.context.parameters.n_vehicles)]
        self.unserved = set()
        for k in range(self.context.parameters.n_vehicles):
            current_node = 0  # Start at the depot
            visited = set()
            while True:
                next_node = None
                for j in self.instance.nodes_ids:
                    if j != current_node and x[current_node][j][k].varValue is not None and x[current_node][j][k].varValue > 0.5:
                        next_node = j
                        break
                if next_node is None or next_node == 0 or next_node in visited:
                    break  # No more nodes to visit or returned to depot
                self.routes[k].append(next_node)
                visited.add(next_node)
                current_node = next_node
        
        # Find unserved nodes
        served_nodes = set()
        for route in self.routes:
            served_nodes.update(route)
        self.unserved = set(self.instance.nodes_ids) - served_nodes - {0}  # Exclude depot

        # Calculate remaining capacity and kilometers
        self.remaining_capacity = [
            self.context.parameters.VEHICLE_CAPACITY - sum(
                self.instance.demands[i] * (y[i][k].varValue if y[i][k].varValue is not None else 0) for i in self.instance.nodes_ids
            )
            for k in range(self.context.parameters.n_vehicles)
        ]

        self.remaining_km = [
            self.context.parameters.MAX_KM - sum(
                self.instance.distances[i][j] * (x[i][j][k].varValue if x[i][j][k].varValue is not None else 0) for i in self.instance.nodes_ids for j in self.instance.nodes_ids
            )
            for k in range(self.context.parameters.n_vehicles)
        ]

        # Calculate total distance
        self.total_distance = sum(
            self.instance.distances[i][j] * (x[i][j][k].varValue if x[i][j][k].varValue is not None else 0)
            for i in self.instance.nodes_ids for j in self.instance.nodes_ids for k in range(self.context.parameters.n_vehicles)
        )

        # Calculate storage cost and fitness
        self.storage_cost = sum(
            self.calculate_storage_cost(current_stock) for current_stock in self.instance.demands
        )
        self.fitness = self.calculate_total_cost(self.total_distance) + self.storage_cost

        self.print_solution()


    def calculate_storage_cost(self, current_stock: int) -> int:
        """
        # Calculate the storage cost based on the current stock
        """
        k1 = 10 # Base storage cost
        k2 = 100   # Additional cost per unit over max_stock
        if current_stock <= self.context.parameters.MAX_STOCK:
            return k1
        else:
            return k2 * (current_stock - self.context.parameters.MAX_STOCK)
        

    def calculate_total_cost(self, total_distance: int) -> int:
        """
        Calculate the total cost
        """
        return total_distance * 0.45


    def print_solution(self):
        print(f"Routes: {self.routes}")
        print(f"Unserved: {self.unserved}")
        print(f"Remaining capacity: {self.remaining_capacity}")
        print(f"Remaining km: {self.remaining_km}")
        print(f"Total distance: {self.total_distance}")
        print(f"Storage cost: {self.storage_cost}")
        print(f"Total cost: {self.fitness}")
    

    def __str__(self):
        return f"Solution(routes={self.routes}, total_distance={self.total_distance}, storage_cost={self.storage_cost}, total_cost={self.fitness}, unserved={self.unserved})"

import numpy as np
from algorithm import Instance, Context

class Solution:
    def __init__(self, context: Context, instance: Instance):
        self.context = context
        self.instance = instance
        self.routes = [[] for _ in range(self.context.parameters.n_vehicles)]
        self.unserved = set(range(1, self.context.parameters.n_vehicles + 1))
        self.total_distance = 0
        self.storage_cost = 0
        self.total_cost = 0

    def solve(self) -> tuple:
        """
        Solve the cash pickup and delivery problem using a greedy approach.
        """
        current_stock = sum(-min(demand, 0) for demand in self.instance.demands)  # Initial stock in depot
        remaining_capacity = [self.context.parameters.VEHICLE_CAPACITY] * self.context.parameters.n_vehicles  # Track vehicle capacities
        remaining_km = [self.context.parameters.MAX_KM] * self.context.parameters.n_vehicles  # Track vehicle mileage

        # Assign routes using a greedy approach
        for vehicle in range(self.context.parameters.n_vehicles):
            current_node = 0  # Start at the depot
            while self.unserved:
                # Find the nearest feasible node
                candidate_nodes = self.find_feasible_nodes(current_node, current_stock)
                if not candidate_nodes:
                    break  # No more feasible nodes for this vehicle

                # Select the next node to visit
                node, distance = max(candidate_nodes, key=lambda x: (self.instance.demands[x[0]] < 0, abs(self.instance.demands[x[0]]), -x[1]))

                # Append node to route
                self.routes[vehicle].append(node)
                remaining_capacity[vehicle] -= abs(self.instance.demands[node])
                remaining_km[vehicle] -= distance
                self.total_distance += distance
                current_stock += self.instance.demands[node]
                self.unserved.remove(node)
                current_node = node

            # Return to depot
            if self.routes[vehicle]:
                self.total_distance += self.instance.distances[current_node][0]
                remaining_km[vehicle] -= self.instance.distances[current_node][0]

        # Calculate storage stock and total cost
        self.storage_cost = self.calculate_storage_cost(current_stock)
        self.total_cost = self.calculate_total_cost(self.total_distance)

    
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


    def find_feasible_nodes(self, current_node: int, current_stock: int) -> list:
        """
        Find the nearest feasible node for a given vehicle.

        Args:
            current_node (int): Current node
            current_stock (int): Current stock

        Returns:
            list: Candidate nodes
        """
        candidate_nodes = [
            (node, self.instance.distances[current_node][node]) for node in self.unserved
            if (
                self.context.parameters.VEHICLE_CAPACITY >= abs(self.instance.demands[node]) and
                self.context.parameters.MAX_KM >= self.instance.distances[current_node][node] + self.instance.distances[node][0] and
                (current_stock + self.instance.demands[node] <= self.context.parameters.MAX_STOCK if self.instance.demands[node] > 0 else True)
            )
        ]
        return candidate_nodes
    

    def __str__(self):
        return f"Solution(routes={self.routes}, total_distance={self.total_distance}, storage_cost={self.storage_cost}, total_cost={self.total_cost}, unserved={self.unserved})"

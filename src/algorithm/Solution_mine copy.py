import numpy as np

class Solution_mine:
    def __init__(self, instance):
        self.instance = instance
        self.routes = []
        self.total_distance = 0
        self.storage_stock = 0
        self.total_cost = 0
        self.unserved = []

    def solve(self) -> tuple:
        """
        Solve the cash pickup and delivery problem using a greedy approach.

        Args:
            n_services (int): Number of services
            n_vehicles (int): Number of vehicles
            max_km (int): Maximum kilometers per vehicle
            max_stock (int): Maximum depot storage
            vehicle_capacity (int): Capacity per vehicle
            distances (np.ndarray): Distance matrix
            demands (np.ndarray): Demands
            nodes_ids (np.ndarray): Nodes IDs

        Returns:
            tuple: Routes, total distance, storage cost, total cost, unserved services
        """
        # Initialize variables
        routes = [[] for _ in range(self.instance.n_vehicles)]  # Routes per vehicle
        remaining_capacity = [self.instance.vehicle_capacity] * self.instance.n_vehicles  # Track vehicle capacities
        remaining_km = [self.instance.max_km] * self.instance.n_vehicles  # Track vehicle mileage
        unserved = set(self.instance.nodes_ids[1:])  # Services to complete
        current_stock = sum(-min(demand, 0) for demand in self.instance.demands)  # Initial stock in depot
        total_distance = 0


        # Assign routes using a greedy approach
        for vehicle in range(self.instance.n_vehicles):
            current_node = 0  # Start at the depot
            while unserved:
                # Find the nearest feasible node
                candidate_nodes = self.find_feasible_nodes(current_node, unserved, remaining_capacity[vehicle], remaining_km[vehicle], current_stock)
                if not candidate_nodes:
                    break  # No more feasible nodes for this vehicle

                # Select the next node to visit
                # node, distance = min(candidate_nodes, key=lambda x: x[1])
                # node, distance = max(candidate_nodes, key=lambda x: (self.instance.demands[x[0]], -x[1]))
                node, distance = max(
                    candidate_nodes,
                    key=lambda x: (self.instance.demands[x[0]] < 0, abs(self.instance.demands[x[0]]), -x[1])
                )

                # Append node to route
                self.add_node_to_route(vehicle, node, distance, routes, remaining_capacity, remaining_km, total_distance, current_stock, unserved, current_node)
                current_node = node

            # Return to depot
            if routes[vehicle]:
                total_distance += self.instance.distances[current_node][0]
                remaining_km[vehicle] -= self.instance.distances[current_node][0]

        # Calculate storage stock and total cost
        # storage_stock = current_stock if current_stock <= self.instance.max_stock else current_stock - self.instance.max_stock
        storage_stock = max(0, current_stock - self.instance.max_stock)
        total_cost = total_distance + storage_stock

        self.routes = routes
        self.total_distance = total_distance
        self.storage_stock = storage_stock
        self.total_cost = total_cost
        self.unserved = unserved
        return routes, total_distance, storage_stock, total_cost, unserved


    def find_feasible_nodes(self, current_node: int, unserved: set, remaining_capacity: int, remaining_km: int, current_stock: int) -> list:
        """
        Find the nearest feasible node for a given vehicle.

        Args:
            current_node (int): Current node
            unserved (set): Unserved nodes
            distances (np.ndarray): Distance matrix
            remaining_capacity (int): Remaining capacity
            remaining_km (int): Remaining kilometers
            current_stock (int): Current stock
            max_stock (int): Maximum stock
            demands (np.ndarray): Demands

        Returns:
            list: Candidate nodes
        """
        candidate_nodes = [
            (node, self.instance.distances[current_node][node]) for node in unserved
            if (
                remaining_capacity >= abs(self.instance.demands[node]) and
                remaining_km >= self.instance.distances[current_node][node] + self.instance.distances[node][0] and
                (current_stock + self.instance.demands[node] <= self.instance.max_stock if self.instance.demands[node] > 0 else True)
            )
        ]
        return candidate_nodes
    
    def add_node_to_route(self, vehicle: int, node: int, distance: int, routes: list, remaining_capacity: list, remaining_km: list, total_distance: int, current_stock: int, unserved: set, current_node: int):
        """
        Add a node to the route

        Args:
            vehicle (int): Vehicle ID
            node (int): Node ID
            distance (int): Distance
            routes (list): Routes
            remaining_capacity (list): Remaining capacity
            remaining_km (list): Remaining kilometers
            total_distance (int): Total distance
            current_stock (int): Current stock
            unserved (set): Unserved nodes
            current_node (int): Current node
        """
        routes[vehicle].append(node)
        remaining_capacity[vehicle] -= abs(self.instance.demands[node])
        remaining_km[vehicle] -= distance
        total_distance += distance
        current_stock += self.instance.demands[node]
        unserved.remove(node)

    def __str__(self):
        return f"Solution(routes={self.routes}, total_distance={self.total_distance}, storage_cost={self.storage_cost}, total_cost={self.total_cost}, unserved={self.unserved})"

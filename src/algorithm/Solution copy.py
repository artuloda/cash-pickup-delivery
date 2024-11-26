import numpy as np

class Solution:
    def __init__(self, instance):
        self.instance = instance
        self.routes = [[] for _ in range(self.instance.n_vehicles)]
        self.unserved = set(range(1, self.instance.n_services + 1))
        self.total_distance = 0
        self.storage_cost = 0
        self.total_cost = 0

    def solve(self):

        # Improved heuristic: Assign services to vehicles based on proximity
        for service_id in range(1, self.instance.n_services + 1):
            demand = self.instance.demands[service_id]
            assigned = False

            # Sort vehicles by the additional distance required to serve the service
            vehicle_distances = []
            for vehicle_id in range(self.instance.n_vehicles):
                if self.can_assign_service(vehicle_id, service_id, demand):
                    current_route = self.routes[vehicle_id]
                    additional_distance = self.calculate_additional_distance(current_route, service_id)
                    vehicle_distances.append((additional_distance, vehicle_id))

            # Sort vehicles by the additional distance in ascending order
            vehicle_distances.sort()

            # Assign the service to the vehicle with the least additional distance
            for _, vehicle_id in vehicle_distances:
                if self.can_assign_service(vehicle_id, service_id, demand):
                    self.assign_service(vehicle_id, service_id, demand)
                    assigned = True
                    break

            if not assigned:
                self.unserved.add(service_id)

        # Calculate total cost
        self.total_cost = self.calculate_total_cost()

        return self.routes, self.total_distance, self.storage_stock, self.total_cost, self.unserved

    def calculate_additional_distance(self, current_route, service_id):
        # Calculate the additional distance required to add a service to the current route
        if not current_route:
            # If the route is empty, calculate distance from depot to service and back
            return (self.instance.distances[0, service_id] +
                    self.instance.distances[service_id, 0])
        else:
            # Calculate the additional distance by inserting the service at the end of the route
            last_node = current_route[-1]
            return (self.instance.distances[last_node, service_id] +
                    self.instance.distances[service_id, 0] -
                    self.instance.distances[last_node, 0])

    def can_assign_service(self, vehicle_id, service_id, demand):
        # Check if the vehicle can take the service without exceeding capacity or distance
        current_route = self.routes[vehicle_id]
        current_distance = self.calculate_route_distance(current_route + [service_id])
        current_capacity = sum(self.instance.demands[s] for s in current_route) + demand

        return (current_distance <= self.instance.max_km and
                abs(current_capacity) <= self.instance.vehicle_capacity)

    def assign_service(self, vehicle_id, service_id, demand):
        # Assign the service to the vehicle
        self.routes[vehicle_id].append(service_id)
        self.unserved.discard(service_id)
        self.total_distance += self.calculate_route_distance(self.routes[vehicle_id])
        self.storage_cost += demand

    def calculate_route_distance(self, route):
        # Calculate the total distance of a given route
        distance = 0
        last_node = 0  # Start from depot
        for node in route:
            distance += self.instance.distances[last_node, node]
            last_node = node
        distance += self.instance.distances[last_node, 0]  # Return to depot
        return distance

    def calculate_total_cost(self, distance: int, storage_cost: int):
        # Calculate the total cost including storage cost
        return distance + storage_cost

    def calculate_storage_cost(self):
        # Calculate the storage cost based on the current stock
        k1 = 10 # Base storage cost
        k2 = 100   # Additional cost per unit over max_stock
        if self.storage_stock <= self.instance.max_stock:
            return k1
        else:
            return k1 + k2 * (self.storage_stock - self.instance.max_stock)

    def __str__(self):
        return f"Solution(routes={self.routes}, total_distance={self.total_distance}, storage_cost={self.storage_cost}, total_cost={self.total_cost}, unserved={self.unserved})"

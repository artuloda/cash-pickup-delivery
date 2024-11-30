from algorithm import Instance, Context
from utils import Random

class Solution:
    def __init__(self, context: Context, instance: Instance):
        self.random = Random()
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
        """
        Solve the cash pickup and delivery problem using a greedy approach.
        """
        # Assign routes using a greedy approach
        for vehicle in range(self.context.parameters.n_vehicles):
            previous_node = 0
            while self.unserved:
                # Find the nearest feasible node
                candidate_nodes = self.find_feasible_nodes(previous_node, vehicle)
                if not candidate_nodes:
                    break  # No more feasible nodes for this vehicle

                # Select the next node to visit
                node, distance = self.select_next_node(candidate_nodes, vehicle)

                # Add node to route
                previous_node = self.add_node_to_route(node, vehicle, distance, self.instance.demands[node])
                    
            # Return to depot
            if self.routes[vehicle]:
                self.total_distance += self.instance.distances[previous_node][0]
                self.current_distance[vehicle] += self.instance.distances[previous_node][0]
                # print(f"Vehicle {vehicle}, nodes: {self.routes[vehicle]}, distance: {self.current_distance[vehicle]}, capacity: {self.current_capacity[vehicle]}, stock: {self.current_stock}")

        # Calculate storage stock and total cost
        self.storage_cost = self.instance.calculate_storage_cost(self.current_stock)
        self.fitness = self.instance.calculate_total_cost(self.total_distance)
        # self.print_solution()


    def find_feasible_nodes(self, previous_node , vehicle) -> list:
        """
        Find the feasible nodes for a given vehicle. Ensuring capacity, mileage, and stock constraints

        Args:
            previous_node (int): Previous node
            vehicle (int): Vehicle index
        Returns:
            list: Candidate nodes
        """
        candidate_nodes = []
        depot_node = 0  # Assuming the depot is node 0
        for node in self.unserved:
            # Check distance constraint
            distance = self.instance.distances[previous_node][node]
            if self.current_distance[vehicle] + distance + self.instance.distances[node][depot_node] <= self.context.parameters.MAX_DISTANCE:
                # Check capacity constraint
                demand = self.instance.demands[node]
                value_to_add = self.current_capacity[vehicle] + demand
                if demand < 0: # Delivery node
                    if value_to_add <= self.current_stock and value_to_add <= self.context.parameters.VEHICLE_CAPACITY: # Check if the depot has enough stock to deliver the demand:
                        candidate_nodes.append((node, distance))
                else: # Pickup node
                    if value_to_add <= self.context.parameters.VEHICLE_CAPACITY:
                        candidate_nodes.append((node, distance))
        return candidate_nodes
        

    def select_next_node(self, candidate_nodes: list, vehicle: int) -> tuple:
        """
        Select the next node to visit: prioritize nodes that minimize storage cost and maximize service completion

        Args:
            candidate_nodes (list): Candidate nodes
            vehicle (int): Vehicle index
        Returns:
            tuple: Next node and distance
        """
        # Define weights for each factor
        weight_distance = self.random.get_random_float(0.3, 0.8)
        weight_stock_penalty = self.random.get_random_float(0.3, 0.5)
        dynamic_weight_return_to_depot = 0

        # Determine if the vehicle is almost full or almost empty
        almost_full_vehicle_multiplier = self.random.get_random_float(0.6, 0.8)
        capacity_threshold = self.context.parameters.VEHICLE_CAPACITY * almost_full_vehicle_multiplier
        millage_threshold = self.context.parameters.MAX_DISTANCE * almost_full_vehicle_multiplier
        if self.current_capacity[vehicle] >= capacity_threshold and self.current_distance[vehicle] >= millage_threshold:
            dynamic_weight_return_to_depot = self.random.get_random_float(0.6, 0.8)

        # Normalize the weights
        total_weight = weight_distance + weight_stock_penalty + dynamic_weight_return_to_depot
        weight_distance_normalized = weight_distance / total_weight
        weight_stock_penalty_normalized = weight_stock_penalty / total_weight
        dynamic_weight_return_to_depot_normalized = dynamic_weight_return_to_depot / total_weight

        def evaluate_candidate(node_distance_tuple):
            node, distance = node_distance_tuple  # Node and distance
            stock_after_visit = self.current_stock + self.instance.demands[node]  # Stock after visit
            stock_penalty = max(0, stock_after_visit - self.context.parameters.MAX_STOCK)  # Stock penalty
            
            # Combine factors with weights
            return (
                weight_distance_normalized * distance +
                weight_stock_penalty_normalized * stock_penalty +
                dynamic_weight_return_to_depot_normalized * distance
            )

        node, distance = min(candidate_nodes, key=evaluate_candidate)
        return node, distance
    
    
    def add_node_to_route(self, node: int, vehicle: int, distance: float, demand: int):
        """
        Add a node to the route of a vehicle

        Args:
            node (int): Node to add
            vehicle (int): Vehicle index
            distance (float): Distance to the node
            demand (int): Demand of the node
        Returns:
            int: Node added
        """
        self.current_capacity[vehicle] += demand
        self.current_distance[vehicle] += distance
        self.routes[vehicle].append(node)
        self.total_distance += distance
        self.unserved.remove(node)

        # Delivery node
        if demand < 0:
            # Calculate the difference before updating the capacity
            difference = abs(demand) - (self.current_capacity[vehicle] - demand)
            if difference > 0:
                self.current_stock -= difference  # Reduce the current stock
                self.vehicles_initial_load[vehicle] += difference  # Update the vehicles initial load
                self.current_capacity[vehicle] = 0  # Reset capacity to zero if it goes negative
        return node
    

    def print_solution(self):

        print("Routes per vehicle:")
        for v, route in enumerate(self.routes):
            current_capacity = self.current_capacity[v] # Assuming capacities is a list of used capacities per vehicle
            current_distance = self.current_distance[v]  # Assuming remaining_distance is a list of used distance per vehicle
            print(f"  Vehicle {v + 1}: Depot -> {' -> '.join(map(str, route))} -> Depot | Current capacity: {current_capacity} | Current distance: {current_distance / 1000:.2f} km")

        print(f"Total routes: {len(self.routes)}")
        print(f"Total distance: {self.total_distance}")
        print(f"Storage cost: {self.storage_cost}")
        print(f"Fitness: {self.fitness}")
        print(f"Current stock: {self.current_stock}")
        print(f"Unserved: {self.unserved}")
        print(f"Current capacity: {self.current_capacity}")
        print(f"Current distance: {self.current_distance}")
        print(f"Vehicles initial load: {self.vehicles_initial_load}")
        print("-----------------------------------------------------------------------------------")
    

    def __str__(self):
        return f"Solution(routes={self.routes}, total_distance={self.total_distance}, storage_cost={self.storage_cost}, total_cost={self.fitness}, unserved={self.unserved})"

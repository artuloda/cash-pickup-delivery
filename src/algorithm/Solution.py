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
        self.current_stock = self.context.parameters.MAX_STOCK * 0.8
        self.total_distance = 0
        self.storage_cost = 0
        self.fitness = 0


    def solve(self):
        """
        Solve the cash pickup and delivery problem using a greedy approach.
        """
        # Assign routes using a greedy approach
        vehicles_initial_load = [0] * self.context.parameters.n_vehicles
        for vehicle in range(self.context.parameters.n_vehicles):
            previous_node = 0
            while self.unserved:
                # Get random node from unserved
                if previous_node == 0:
                    node = self.random.get_random_choice(list(self.unserved))
                else:
                    # Find the nearest feasible node
                    candidate_nodes = self.find_feasible_nodes(previous_node, vehicle)
                    if not candidate_nodes:
                        break  # No more feasible nodes for this vehicle
                    # Select the next node to visit
                    node, distance = self.select_next_node(candidate_nodes, vehicle)
                    
                # Update distance and capacity
                distance = self.instance.distances[previous_node][node]
                if distance + self.instance.distances[node][0] <= self.context.parameters.MAX_DISTANCE:
                    demand = self.instance.demands[node]
                    # Pickup node
                    if demand > 0:
                        if self.current_capacity[vehicle] + demand <= self.context.parameters.VEHICLE_CAPACITY:
                            self.current_capacity[vehicle] += demand
                            self.current_distance[vehicle] += distance
                            self.routes[vehicle].append(node)
                            self.total_distance += distance
                            self.current_stock += demand
                            self.unserved.remove(node)
                            previous_node = node
                        else:
                            continue # Skip this node if the capacity is exceeded
                    # Delivery node
                    else:
                        vehicles_initial_load[vehicle] += abs(demand) - self.current_capacity[vehicle]
                        self.current_capacity[vehicle] -= abs(demand)
                        self.current_distance[vehicle] += distance + self.instance.distances[node][0]
                        self.routes[vehicle].append(node)
                        self.total_distance += distance
                        self.current_stock -= abs(demand)
                        self.unserved.remove(node)
                        previous_node = node
                # If the distance is too long, skip this node
                else:
                    continue

            # Return to depot
            if self.routes[vehicle]:
                self.total_distance += self.instance.distances[previous_node][0]
                self.current_distance[vehicle] += self.instance.distances[previous_node][0]
                # print(f"Vehicle {vehicle}, nodes: {self.routes[vehicle]}, distance: {self.current_distance[vehicle]}, capacity: {self.current_capacity[vehicle]}, stock: {self.current_stock}")

        # Calculate storage stock and total cost
        self.storage_cost = self.instance.calculate_storage_cost(self.current_stock)
        self.fitness = self.instance.calculate_total_cost(self.total_distance)
        # self.print_solution()


    def find_feasible_nodes(self,previous_node , vehicle) -> list:
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
            distance = self.instance.distances[previous_node][node]
            # Check distance and capacity constraints
            if self.current_distance[vehicle] + distance + self.instance.distances[node][depot_node] <= self.context.parameters.MAX_DISTANCE and \
                self.current_capacity[vehicle] + self.instance.demands[node] <= self.context.parameters.VEHICLE_CAPACITY: 
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
    

    def print_solution(self):

        print("Routes per vehicle:")
        for v, route in enumerate(self.routes):
            current_capacity = self.current_capacity[v]  # Assuming capacities is a list of used capacities per vehicle
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
        print("-----------------------------------------------------------------------------------")
    

    def __str__(self):
        return f"Solution(routes={self.routes}, total_distance={self.total_distance}, storage_cost={self.storage_cost}, total_cost={self.fitness}, unserved={self.unserved})"

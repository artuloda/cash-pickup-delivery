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
        self.remaining_capacity = [self.context.parameters.VEHICLE_CAPACITY] * self.context.parameters.n_vehicles
        self.remaining_distance = [self.context.parameters.MAX_DISTANCE] * self.context.parameters.n_vehicles
        self.current_stock = sum(-min(demand, 0) for demand in self.instance.demands)  # Initial stock in depot
        self.total_distance = 0
        self.storage_cost = 0
        self.fitness = 0


    def solve(self):
        """
        Solve the cash pickup and delivery problem using a greedy approach.
        """
        # Assign routes using a greedy approach
        for vehicle in range(self.context.parameters.n_vehicles):
            current_node = 0  # Start at the depot
            while self.unserved:

                # Find the nearest feasible node
                candidate_nodes = self.find_feasible_nodes(current_node, vehicle)
                if not candidate_nodes:
                    break  # No more feasible nodes for this vehicle

                # Select the next node to visit
                node, distance = self.select_next_node(candidate_nodes, vehicle)

                # Append node to route
                self.add_node_to_route(vehicle, node, distance)
                current_node = node

            # Return to depot
            if self.routes[vehicle]:
                self.total_distance += self.instance.distances[current_node][0]
                self.remaining_distance[vehicle] -= self.instance.distances[current_node][0]

        # Calculate storage stock and total cost
        self.storage_cost = self.instance.calculate_storage_cost(self.current_stock)
        self.fitness = self.instance.calculate_total_cost(self.total_distance) + self.storage_cost
        # self.print_solution()


    def find_feasible_nodes(self, current_node: int, vehicle: int) -> list:
        """
        Find the feasible nodes for a given vehicle. Ensuring capacity, mileage, and stock constraints

        Args:
            current_node (int): Current node
            current_stock (int): Current stock
            unserved (set): Unserved nodes
        Returns:
            list: Candidate nodes
        """
        depot_node = 0  # Assuming the depot is node 0
        candidate_nodes = [
            (node, self.instance.distances[current_node][node]) for node in self.unserved
            if not (
                self.remaining_capacity[vehicle] < abs(self.instance.demands[node]) or 
                self.remaining_distance[vehicle] < (self.instance.distances[current_node][node] + self.instance.distances[node][depot_node])
            )
        ]
        return candidate_nodes
        

    # def select_next_node2(self, candidate_nodes: list) -> tuple:
    #     """
    #     Select the next node to visit: prioritize nodes that minimize storage cost and maximize service completion

    #     Args:
    #         candidate_nodes (list): Candidate nodes
    #     Returns:
    #         tuple: Next node and distance
    #     """
    #     def evaluate_candidate(node_distance_tuple):
    #         node, distance = node_distance_tuple # Node and distance
    #         stock_after_visit = self.current_stock + self.instance.demands[node] # Stock after visit
    #         stock_penalty = max(0, stock_after_visit - self.context.parameters.MAX_STOCK) # Stock penalty
            
    #         # Additional heuristic factors
    #         demand_priority = abs(self.instance.demands[node])  # Prioritize larger demands
    #         proximity_to_others = sum(self.instance.distances[node][other] for other in self.unserved) / len(self.unserved) # Proximity to others
            
    #         # Combine factors with weights
    #         return distance + stock_penalty + (1 / demand_priority) + proximity_to_others

    #     node, distance = min(candidate_nodes, key=evaluate_candidate)
    #     return node, distance
    

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
        weight_stock_penalty = self.random.get_random_float(0.3, 0.8)
        weight_demand_priority = self.random.get_random_float(0.1, 0.3)
        weight_proximity = self.random.get_random_float(0.3, 0.8)
        dynamic_weight_return_to_depot = 0

        #Determine if the vehicle is almost full or almost empty
        almost_full_vehicle_multiplier = self.random.get_random_float(0.6, 0.8)
        capacity_threshold = self.context.parameters.VEHICLE_CAPACITY * almost_full_vehicle_multiplier
        millage_threshold = self.context.parameters.MAX_DISTANCE * almost_full_vehicle_multiplier
        if self.remaining_capacity[vehicle] <= capacity_threshold and self.remaining_distance[vehicle] <= millage_threshold:
            dynamic_weight_return_to_depot = self.random.get_random_float(0.6, 0.8)

        # Normalize the weights
        total_weight = weight_distance + weight_stock_penalty + weight_demand_priority + weight_proximity + dynamic_weight_return_to_depot
        weight_distance_normalized = weight_distance / total_weight
        weight_stock_penalty_normalized = weight_stock_penalty / total_weight
        weight_demand_priority_normalized = weight_demand_priority / total_weight
        weight_proximity_normalized = weight_proximity / total_weight
        dynamic_weight_return_to_depot_normalized = dynamic_weight_return_to_depot / total_weight

        def evaluate_candidate(node_distance_tuple):
            node, distance = node_distance_tuple  # Node and distance
            stock_after_visit = self.current_stock + self.instance.demands[node]  # Stock after visit
            stock_penalty = max(0, stock_after_visit - self.context.parameters.MAX_STOCK)  # Stock penalty
            
            # Additional heuristic factors
            demand_priority = abs(self.instance.demands[node])  # Prioritize larger demands
            proximity_to_others = sum(self.instance.distances[node][other] for other in self.unserved) / len(self.unserved)  # Proximity to others
            
            # Combine factors with weights
            return (
                weight_distance_normalized * distance +
                weight_stock_penalty_normalized * stock_penalty +
                weight_demand_priority_normalized * (1 / demand_priority) +
                weight_proximity_normalized * proximity_to_others +
                dynamic_weight_return_to_depot_normalized * distance
            )

        node, distance = min(candidate_nodes, key=evaluate_candidate)
        return node, distance
    

    def add_node_to_route(self, vehicle: int, node: int, distance: int):
        """
        Add a node to a route

        Args:
            vehicle (int): Vehicle index
            node (int): Node index
            distance (int): Distance
        """
        self.routes[vehicle].append(node)
        self.remaining_capacity[vehicle] -= abs(self.instance.demands[node])
        self.remaining_distance[vehicle] -= distance
        self.total_distance += distance
        self.current_stock += self.instance.demands[node]
        self.unserved.remove(node)


    def print_solution(self):
        print(f"Routes: {self.routes}")
        print(f"Unserved: {self.unserved}")
        print(f"Remaining capacity: {self.remaining_capacity}")
        print(f"Remaining distance: {self.remaining_distance}")
        print(f"Total distance: {self.total_distance}")
        print(f"Storage cost: {self.storage_cost}")
        print(f"Fitness: {self.fitness}")
        print("-----------------------------------------------------------------------------------")
    

    def __str__(self):
        return f"Solution(routes={self.routes}, total_distance={self.total_distance}, storage_cost={self.storage_cost}, total_cost={self.fitness}, unserved={self.unserved})"

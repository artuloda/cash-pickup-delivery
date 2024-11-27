from algorithm import Instance, Context

class Solution:
    def __init__(self, context: Context, instance: Instance):
        self.context = context
        self.instance = instance
        self.initialize_solution()


    def initialize_solution(self):
        self.routes = [[] for _ in range(self.context.parameters.n_vehicles)]
        self.unserved = set(range(1, self.context.parameters.n_services + 1))
        self.remaining_capacity = [self.context.parameters.VEHICLE_CAPACITY] * self.context.parameters.n_vehicles
        self.remaining_km = [self.context.parameters.MAX_KM] * self.context.parameters.n_vehicles
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
                node, distance = self.select_next_node(candidate_nodes)

                # Append node to route
                self.add_node_to_route(vehicle, node, distance)
                current_node = node

            # Return to depot
            if self.routes[vehicle]:
                self.total_distance += self.instance.distances[current_node][0]
                self.remaining_km[vehicle] -= self.instance.distances[current_node][0]

        # Calculate storage stock and total cost
        self.storage_cost = self.calculate_storage_cost(self.current_stock)
        self.fitness = self.calculate_total_cost(self.total_distance) + self.storage_cost
        # self.print_solution()

    
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
                self.remaining_km[vehicle] < (self.instance.distances[current_node][node] + self.instance.distances[node][depot_node])
            )
        ]
        return candidate_nodes
        

    def select_next_node(self, candidate_nodes: list) -> tuple:
        """
        Select the next node to visit: prioritize nodes that minimize storage cost and maximize service completion

        Args:
            candidate_nodes (list): Candidate nodes
            current_stock (int): Current stock
        Returns:
            tuple: Next node and distance
        """
        # Improved heuristic: prioritize nodes that minimize storage cost and maximize service completion
        node, distance = min(
            candidate_nodes,
            key=lambda x: (
                self.instance.demands[x[0]] < 0,  # Prioritize pickups
                abs(self.instance.demands[x[0]]),  # Prioritize larger demands
                -x[1],  # Minimize distance
                self.current_stock + self.instance.demands[x[0]] > self.context.parameters.MAX_STOCK  # Minimize storage cost
            )
        )
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
        self.remaining_km[vehicle] -= distance
        self.total_distance += distance
        self.current_stock += self.instance.demands[node]
        self.unserved.remove(node)


    def print_solution(self):
        print(f"Routes: {self.routes}")
        print(f"Unserved: {self.unserved}")
        print(f"Remaining capacity: {self.remaining_capacity}")
        print(f"Remaining km: {self.remaining_km}")
        print(f"Total distance: {self.total_distance}")
        print(f"Storage cost: {self.storage_cost}")
        print(f"Fitness: {self.fitness}")
        print("-----------------------------------------------------------------------------------")
    

    def __str__(self):
        return f"Solution(routes={self.routes}, total_distance={self.total_distance}, storage_cost={self.storage_cost}, total_cost={self.fitness}, unserved={self.unserved})"

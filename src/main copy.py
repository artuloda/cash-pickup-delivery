import time
import numpy as np
# from algorithm import Problem, Instance, Solution, PreValidation, PostValidation
# from model import Algorithm

def print_ASCII_logo():
    logo_str =  """
    @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@((&@@@@((@@@@@@@@(@@@@@@@@%%@@@@@@@@@@@@@@@@
    @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@((&@((((((((@@(((((((@@%%%%%%%%@@@@@@@@@@@@@
    @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@((&@((((((((@@(((((((@@%%%%%%%%@@@@@@@@@@@@@
    @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@((&@@@@((#@@@@@@(((@@@@@@&%%&@@@@@@@@@@@@@@@
    @@@@@@@@@@@@@((((@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@((((@@@@@@@@@@@@@@@@(((@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    @@@@@@@@@@@@@((((@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@((@@@@@@@@@@@@@@@@@(((@@@@@@@@@@@@@@@@@@@@@@@@@@@((&@@#(((((@@@((@@@(((((@@@@@%%%%%@@@@%%%%%@
    @@@@@@((((((@((((@@@@@@@@%(((((%@@@@@@@@@@@@#((((((@@@@@((((@@@@@@@@%(((((%@(((@@@@@@@@@((((((@@@@@@@@@@@@((&@((((((((@@((@@((((((((@%%%%%%%%@@%%%%%%%
    @@(((((((((((((((@@@@@(((((((((((((@@@@@(((((((((((((@@@((((@@@@@((((((((((((((@@@@@(((((((((((((@@@@@@@@@((&@@((((((@@@((@@(((((((@@@%%%%%%&@@%%%%%%%
    @((((@@@@@@@@((((@@@((((@@@@@@@@((((@@@((((@@@@@@@@@@@@@((((@@@((((@@@@@@@@@(((@@@@(((%@@@@@@@@(((@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    ((((@@@@@@@@@((((@@@((((((((((((((((@@((((@@@@@@@@@@@@@@((((@@@((((@@@@@@@@@(((@@@((((((((((((((((@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    @(((@@@@@@@@@((((@@@((((@@@@@@@@@@@@@@((((@@@@@@@@@@@@@@((((@@@((((@@@@@@@@@(((@@@%(((@@@@@@@@@@@@@@@@@@@@((&@@((((((@@@(((((((@@@%%%%%%@@@@@@@@@@@@@@
    @#(((((@@@@@@((((@@@@(((((@@@@@@#((@@@@#(((((@@@@@(((@@@((((@@@@(((((@@@@@@@(((@@@@((((((@@@@@@((@@@@@@@@@((&@((((((((@@(((((((@@%%%%%%%%@@@@@@@@@@@@@
    @@@@(((((((((((((@@@@@@((((((((((((@@@@@@@(((((((((((@@@((((@@@@@@(((((((((((((@@@@@@@((((((((((((@@@@@@@@((&@@@(((((@@@@(((((@@@@%%%%%@@@@@@@@@@@@@@@
    @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
                        """ 
    print(logo_str)


# def execute():
#     start_time = time.time()

#     # Create Problem context
#     problem = Problem() # Initialize problem
#     problem.logger.info(problem.parameters)

#     # Create Instance
#     instance = Instance(problem) # Initialize instance
#     #instance.print_instance()

#     # Pre-validation
#     PreValidation(problem, instance)

#     # Start algorithm
#     algorithm = Algorithm(problem, instance)

#     # Keep Solution
#     solution = Solution(problem, instance, algorithm)

#     # Post-validation
#     PostValidation(problem, instance, solution)

#     # Remove all handlers after logging
#     problem.logger.info(f"Execution End: Time taken: {time.time() - start_time} s.")
#     problem.logger.remove_handlers()
    
def test():
    # Input parameters
    n_services = 100  # Number of services
    n_vehicles = 20   # Number of vehicles
    max_km = 300     # Maximum kilometers per vehicle
    max_stock = 5000 # Maximum depot storage
    vehicle_capacity = 1000  # Capacity per vehicle
    k1, k2 = 1, 2    # Storage cost factors

    # Example data (replace with real data)
    np.random.seed(42)
    distances = np.random.randint(10, 100, size=(n_services + 1, n_services + 1))
    np.fill_diagonal(distances, 0)  # No self-loop cost
    demands = np.random.randint(-200, 200, size=n_services)  # Pickup (-) and delivery (+)
    demands = np.append(0, demands)  # Depot demand is 0

    # Route assignment and cost calculation
    def solve_cvrp():
        # Initialize variables
        routes = [[] for _ in range(n_vehicles)]  # Routes per vehicle
        remaining_capacity = [vehicle_capacity] * n_vehicles  # Track vehicle capacities
        remaining_km = [max_km] * n_vehicles  # Track vehicle mileage
        unserved = set(range(1, n_services + 1))  # Services to complete
        current_stock = sum(-min(demand, 0) for demand in demands)  # Initial stock in depot
        total_distance = 0

        # Assign routes using a greedy approach
        for vehicle in range(n_vehicles):
            current_node = 0  # Start at the depot
            while unserved:
                # Find the nearest feasible node
                candidate_nodes = [
                    (node, distances[current_node][node]) for node in unserved
                    if (
                        remaining_capacity[vehicle] >= abs(demands[node]) and
                        remaining_km[vehicle] >= distances[current_node][node] + distances[node][0] and
                        (current_stock + demands[node] <= max_stock if demands[node] > 0 else True)
                    )
                ]
                if not candidate_nodes:
                    break  # No more feasible nodes for this vehicle

                # Select the nearest node
                node, distance = min(candidate_nodes, key=lambda x: x[1])
                routes[vehicle].append(node)
                remaining_capacity[vehicle] -= abs(demands[node])
                remaining_km[vehicle] -= distance
                total_distance += distance
                current_stock += demands[node]
                unserved.remove(node)
                current_node = node

            # Return to depot
            if routes[vehicle]:
                total_distance += distances[current_node][0]
                remaining_km[vehicle] -= distances[current_node][0]

        # Calculate storage costs
        excess_stock = max(0, current_stock - max_stock)
        storage_cost = k1 * current_stock if current_stock <= max_stock else \
            k1 * max_stock + k2 * excess_stock

        # Total cost
        total_cost = total_distance + storage_cost

        return routes, total_distance, storage_cost, total_cost, unserved

    # Solve and display results
    routes, total_distance, storage_cost, total_cost, unserved = solve_cvrp()

    print("Routes per vehicle:")
    for v, route in enumerate(routes):
        print(f"  Vehicle {v + 1}: Depot -> {' -> '.join(map(str, route))} -> Depot")

    print(f"\nUnserved services: {unserved}")
    print(f"Total distance traveled: {total_distance}")
    print(f"Depot storage cost: {storage_cost}")
    print(f"Total cost: {total_cost}")

if __name__ == '__main__':
    print_ASCII_logo()
    test()
    # execute()
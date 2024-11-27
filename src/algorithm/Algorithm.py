from algorithm import Context, Instance, Solution, ExactSolution
import time

class Algorithm:
    def __init__(self, context: Context, instance: Instance):
        self.context = context
        self.instance = instance
        self.solutions_fitness = []
        self.solutions = []
        self.best_solution = None
        self.best_fitness = 0x3f3f3f3f
        self.execute_algorithm()

    
    def add_solution(self, solution: Solution):
        """
        Add a solution to the algorithm

        Args:
            solution (Solution): Solution to add
        """
        self.solutions.append(solution)
        self.solutions_fitness.append(solution.fitness)

    
    def set_best_solution(self, solution: Solution):
        """
        Set the best solution

        Args:
            solution (Solution): Solution to set as best
        """
        self.best_solution = solution
        self.best_fitness = solution.fitness


    def execute_algorithm(self):
        """
        Execute the algorithm
        """
        self.construct()
        self.improve()


    def construct(self):
        """
        Construct the solutions
        """
        self.context.logger.info("Constructing solutions...")
        start_time = time.time()
        iteration = 0
        while iteration < self.context.parameters.MAX_ITERATIONS and time.time() - start_time < self.context.parameters.MAX_TIME:
            start_time_iteration = time.time()
            # Create a new solution
            if self.context.parameters.ALGORITHM_OPTION == 1:
                solution = Solution(self.context, self.instance)
            else:
                solution = ExactSolution(self.context, self.instance)
            solution.solve()
            self.add_solution(solution)

            # Update best solution
            if solution.fitness < self.best_fitness:
                self.set_best_solution(solution)
            self.context.logger.info(f"Iteration {iteration} - Best fitness: {self.best_fitness}, Time: {time.time() - start_time_iteration:.2f}s")
            iteration += 1


    def improve(self):
        """
        Improve the solutions
        """
        self.context.logger.info("Improving solutions...")


    def print_results(self):
        """
        Print the solution

        Args:
            routes (list): Routes per vehicle
            total_distance (int): Total distance traveled
            storage_cost (int): Depot storage cost
            fitness (int): Total cost
            unserved (set): Unserved services
        """
        print("Routes per vehicle:")
        for v, route in enumerate(self.best_solution.routes):
            remaining_capacity = self.best_solution.remaining_capacity[v]  # Assuming capacities is a list of used capacities per vehicle
            remaining_km = self.best_solution.remaining_km[v]  # Assuming remaining_km is a list of used km per vehicle
            print(f"  Vehicle {v + 1}: Depot -> {' -> '.join(map(str, route))} -> Depot | Remaining capacity: {remaining_capacity} | Remaining KM: {remaining_km}")

        print(f"\nUnserved services: {self.best_solution.unserved}")
        print(f"Total distance traveled: {self.best_solution.total_distance}")
        print(f"Depot storage cost: {self.best_solution.storage_cost}")
        print(f"Total cost: {round(self.best_solution.fitness, 2)} €")


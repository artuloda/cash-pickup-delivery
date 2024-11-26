from algorithm import Context
from utils import Random
import numpy as np

class Instance:
    def __init__(self, context: Context):
        self.random = Random()
        self.context = context
        self.distances = self.load_distances()
        self.demands = self.load_demands()
        self.nodes_ids = self.load_nodes_ids()
        self.validate()

    def load_distances(self):
        """
        Load the distances matrix
        """
        distances = np.random.randint(5, 50, size=(self.context.parameters.n_services + 1, self.context.parameters.n_services + 1))
        np.fill_diagonal(distances, 0)  # No self-loop cost
        return distances

    def load_demands(self):
        """
        Load the demands vector
        """
        demands = np.random.randint(-200, 200, size=self.context.parameters.n_services + 1)
        demands = np.append(0, demands)  # Depot demand is 0
        return demands

    def load_nodes_ids(self):
        """
        Load the nodes ids vector
        """
        nodes_ids = np.arange(self.context.parameters.n_services + 1)
        return nodes_ids

    def validate(self):
        """
        Validate the instance
        """
        # Demand validation
        if sum(self.demands) > self.context.parameters.VEHICLE_CAPACITY * self.context.parameters.n_vehicles:
            raise ValueError(f"Total demand must be less than the total vehicle capacity, {sum(self.demands)} > {self.context.parameters.VEHICLE_CAPACITY * self.context.parameters.n_vehicles}")

        # Stock validation
        if sum(self.demands) > self.context.parameters.MAX_STOCK:
            raise ValueError(f"Total demand must be less than the maximum stock, {sum(self.demands)} > {self.context.parameters.MAX_STOCK}")


    def __str__(self):
        return f"Instance(total_demand={sum(self.demands)}, total_nodes={len(self.nodes_ids)})"
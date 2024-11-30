from algorithm import Context
from utils import Random, IO, Geo
import numpy as np

class Instance:
    def __init__(self, context: Context):
        self.random = Random()
        self.IO = IO()
        self.Geo = Geo()
        self.context = context
        self.nodes_df = self.IO.read_csv(self.context.parameters.input_file_path + '/nodes.csv', separator=';', decimal=',', encoding='latin-1')
        self.depot_df = self.nodes_df[self.nodes_df['Id'] == 0]
        self.demands = self.load_demands()
        self.nodes_ids = self.load_nodes_ids()
        self.distances = self.load_distances()
        self.validate()


    def load_demands(self):
        """
        Load the demands vector
        """
        demands = self.nodes_df['Items'].astype(int).to_list()
        return demands
    

    def load_nodes_ids(self):
        """
        Load the nodes ids vector
        """
        nodes_ids = self.nodes_df['Id'].astype(int).to_list()
        return nodes_ids
    
    
    def load_distances(self):
        """
        Load the distances matrix
        """
        # Create empty distances matrix
        n = len(self.nodes_ids)
        distances = np.zeros((n, n))
        
        # Calculate distances between all pairs of nodes using coordinates
        for i in range(n):
            for j in range(n):
                if i != j:
                    coord1 = (self.nodes_df.iloc[i]['Latitude'], self.nodes_df.iloc[i]['Longitude'])
                    coord2 = (self.nodes_df.iloc[j]['Latitude'], self.nodes_df.iloc[j]['Longitude'])
                    distances[i,j] = int(self.Geo.calculate_distance(coord1, coord2))
        return distances
    

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
        return total_distance / 1000 * 0.45


    def __str__(self):
        positive_demands = [d for d in self.demands if d > 0]
        negative_demands = [d for d in self.demands if d < 0]
        class_str = f"\nTotal_positive_demand={sum(positive_demands)}"
        class_str += f"\nTotal_negative_demand={abs(sum(negative_demands))}"
        class_str += f"\nDemand_balance={sum(positive_demands) - abs(sum(negative_demands))}"
        class_str += f"\nTotal_nodes={len(self.nodes_ids)}"
        class_str += f"\nTotal_orders={len(self.demands)}"
        return class_str
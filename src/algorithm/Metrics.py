from algorithm import Context, Instance, Solution
from utils import IO

class Metrics:
    def __init__(self, context: Context, instance: Instance, solution: Solution):
        self.IO = IO()
        self.context = context
        self.instance = instance
        self.solution = solution

    def calculate_metrics(self):
        """
        Calculate the metrics
        """
        self.context.logger.info("Calculating metrics...")
        metrics = []
        for v, route in enumerate(self.solution.routes):
            total_nodes = len(route)
            remaining_capacity = self.solution.remaining_capacity[v]  # Assuming capacities is a list of used capacities per vehicle
            remaining_km = self.solution.remaining_km[v]  # Assuming remaining_km is a list of used km per vehicle
            available_km = self.context.parameters.MAX_KM - remaining_km
            available_capacity = self.context.parameters.VEHICLE_CAPACITY - remaining_capacity
            metric_object = [v+1, total_nodes, remaining_capacity, available_capacity, remaining_km, available_km]
            metrics.append(metric_object)
        columns_name =['Vehicle', 'Total Nodes', 'Remaining Capacity', 'Available Capacity', 'Remaining KM', 'Available KM']
        metrics = self.IO.create_dataframe(metrics, columns_name)
        self.IO.create_csv(metrics, self.context.output_folder + 'metrics.csv')
        return metrics
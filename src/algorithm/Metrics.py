from algorithm import Context, Instance
from utils import IO
import pandas as pd

class Metrics:
    def __init__(self, context: Context, instance: Instance, routes_df: pd.DataFrame):
        self.IO = IO()
        self.context = context
        self.instance = instance
        self.routes_df = routes_df


    def calculate_metrics(self):
        """
        Calculate the metrics
        """
        self.context.logger.info("Calculating metrics...")
        metrics = []
        routes_by_vehicle_df_list = self.IO.cluster_dataframe_by_condition(self.routes_df, 'Vehicle')
        for route_by_vehicle_df in routes_by_vehicle_df_list:
            vehicle_id = route_by_vehicle_df['Vehicle'].values[0]
            total_nodes = len(route_by_vehicle_df) - 2
            total_picks_ups = sum(1 for _, row in route_by_vehicle_df.iterrows() if row['Type'] == 'Pick_Up')
            total_deliveries = sum(1 for _, row in route_by_vehicle_df.iterrows() if row['Type'] == 'Delivery')
            current_capacity = route_by_vehicle_df['Load'].iloc[-1]
            current_distance = route_by_vehicle_df['Distance'].iloc[-1]
            available_distance = self.context.parameters.MAX_DISTANCE - current_distance
            available_capacity = self.context.parameters.VEHICLE_CAPACITY - current_capacity
            metric_object = [
                vehicle_id, 
                total_nodes, 
                total_picks_ups,
                total_deliveries,
                current_capacity, 
                available_capacity, 
                current_distance, 
                available_distance
            ]
            metrics.append(metric_object)
        columns_name =['Vehicle', 'Total Nodes', 'Total Picks Ups', 'Total Deliveries', 'Current Load', 'Available Load', 'Current Distance', 'Available Distance']
        metrics = self.IO.create_dataframe(metrics, columns_name)
        self.IO.create_csv(metrics, self.context.output_folder + 'metrics.csv')
        return metrics

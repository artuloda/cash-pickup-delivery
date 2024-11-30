from utils import IO
from algorithm import Context, Instance, Solution
from .Metrics import Metrics
from .Map import Map

class Results:
    def __init__(self, context: Context, instance: Instance, solution: Solution):
        self.IO = IO()
        self.context = context
        self.instance = instance
        self.solution = solution
        self.routes_df = self.save_solution_routes()
        self.metrics = Metrics(context, instance, self.routes_df).calculate_metrics()
        self.map = Map(context, instance, solution, self.routes_df, self.metrics)
        self.solution_validation()


    def save_solution_routes(self):
        """
        Save the solution routes
        """
        solution_routes = []
        for v, vehicle in enumerate(self.solution.routes):
            if not vehicle:  # Check if the route is empty
                continue  # Skip to the next vehicle if the route is empty
            distance = 0
            vehicle_index = v + 1
            last_node = 0
            load = self.solution.vehicles_initial_load[v]
            depot_start_object = [
                vehicle_index,
                'Route Start',
                '-',
                0,
                self.instance.depot_df['Name'].values[0],
                self.instance.depot_df['Address'].values[0],
                self.instance.depot_df['Location'].values[0],
                self.instance.depot_df['Province'].values[0],
                self.instance.depot_df['Zip_Code'].values[0],
                self.instance.depot_df['Node_Type'].values[0],
                self.instance.depot_df['Latitude'].values[0],
                self.instance.depot_df['Longitude'].values[0],
                load,
                distance,
                0
            ]
            solution_routes.append(depot_start_object)
            for node in vehicle:
                node_df = self.instance.nodes_df[self.instance.nodes_df['Id'] == node].iloc[0]
                order_id = node_df['Id']
                distance += self.instance.distances[last_node, order_id]
                load += node_df['Items']
                order_items = node_df['Items']
                order_type = 'Pick_Up' if order_items > 0 else 'Delivery'
                node_name = node_df['Name']
                node_address = node_df['Address']
                node_location = node_df['Location']
                node_province = node_df['Province']
                node_zip_code = node_df['Zip_Code']
                node_type = node_df['Node_Type']
                node_latitude = node_df['Latitude']
                node_longitude = node_df['Longitude']
                route_object = [
                    vehicle_index,
                    order_id,
                    order_type,
                    order_items,
                    node_name,
                    node_address,
                    node_location,
                    node_province,
                    node_zip_code,
                    node_type,
                    node_latitude,
                    node_longitude,
                    load,
                    distance,
                    0
                ]
                last_node = order_id
                solution_routes.append(route_object)
            distance += self.instance.distances[last_node, 0]
            cost = self.instance.calculate_total_cost(distance)
            depot_end_object = [
                vehicle_index,
                'Route End',
                '-',
                0,
                self.instance.depot_df['Name'].values[0],
                self.instance.depot_df['Address'].values[0],
                self.instance.depot_df['Location'].values[0],
                self.instance.depot_df['Province'].values[0],
                self.instance.depot_df['Zip_Code'].values[0],
                self.instance.depot_df['Node_Type'].values[0],
                self.instance.depot_df['Latitude'].values[0],
                self.instance.depot_df['Longitude'].values[0],
                load,
                distance,
                cost
            ]
            solution_routes.append(depot_end_object)

        columns_name = ['Vehicle', 'Id', 'Type', 'Items', 'Name', 'Address', 'Location', 'Province', 'Zip_Code', 'Node_Type', 'Latitude', 'Longitude', 'Load', 'Distance', 'Cost']
        routes_df = self.IO.create_dataframe(solution_routes, columns_name)
        self.IO.create_csv(routes_df, self.context.output_folder + 'solution_routes.csv')
        return routes_df


    def solution_validation(self):
        """
        Validate the solution
        """
        pass

    def __str__(self) -> str:
        pass
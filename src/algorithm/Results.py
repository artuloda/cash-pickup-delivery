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
        self.metrics = Metrics(context, instance, solution).calculate_metrics()
        self.routes_df = self.save_solution_routes()
        self.map = Map(context, instance, solution, self.routes_df, self.metrics)

        self.solution_validation()


    def save_solution_routes(self):
        """
        Save the solution routes
        """
        solution_routes = []
        for v, vehicle in enumerate(self.solution.routes):
            for node in vehicle:
                node_df = self.instance.nodes_df[self.instance.nodes_df['Id'] == node].iloc[0]
                route_object = [
                    v + 1,
                    node_df['Id'],
                    node_df['Name'],
                    node_df['Address'],
                    node_df['Location'],
                    node_df['Province'],
                    node_df['Zip_Code'],
                    node_df['Items'],
                    node_df['Weight'],
                    node_df['Node_Type'],
                    node_df['TW_Start'],
                    node_df['TW_End'],
                    node_df['Latitude'],
                    node_df['Longitude'],
                    node_df['Email'],
                    node_df['Phone']
                ]
                solution_routes.append(route_object)

        columns_name = ['Vehicle', 'Id', 'Name', 'Address', 'Location', 'Province', 'Zip_Code', 'Items', 'Weight', 'Node_Type', 'TW_Start', 'TW_End', 'Latitude', 'Longitude', 'Email', 'Phone']
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
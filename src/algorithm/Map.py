from algorithm import Context, Instance, Solution
from utils import Folium, Geo, IO, Here, Thread
import pandas as pd
class Map:
    def __init__(self, context: Context, instance: Instance, solution: Solution, routes_df: pd.DataFrame, metrics_df: pd.DataFrame):
        self.IO = IO()
        self.Folium = Folium()
        self.Geo = Geo()
        self.Here = Here()
        self.Thread = Thread()
        self.context = context
        self.instance = instance
        self.solution = solution
        self.routes_df = routes_df
        self.metrics_df = metrics_df

        self.depot_df = self.instance.nodes_df[self.instance.nodes_df['Id'] == 0].iloc[0]
        self.depot_coords = [self.depot_df['Latitude'], self.depot_df['Longitude']]
        logo_img_file = self.context.parameters.input_file_path + 'Logo-decide.png'
        colors_df = self.IO.read_csv(self.context.parameters.input_file_path + '/map/HEXADECIMAL_COLORS.csv', separator=';', encoding='utf-8', decimal=',')
        self.map_object = self.Folium.initialize_folium_map(self.depot_coords, logo_img_file)
        self.colors = self.Folium.get_input_colors(colors_df, 0) # Lista desordenada de colores en hexadecimal
        self.colors_high_contrast = self.Folium.get_input_colors(colors_df, 1) # Lista desordenada de colores en hexadecimal
        self.spain_zip_codes_data = self.Folium.get_spain_zip_codes(self.context.parameters.input_file_path + '/map/')
        self.create_map()


    def create_map(self):
        """
        Draws the Map of the result routes
        """
        self.context.logger.info("Drawing map...")
        self.draw_depot()
        self.draw_zip_code_polygons()
        self.draw_heat_map()
        self.draw_nodes()
        self.draw_unserved_nodes()
        self.draw_routes()

        fileName = self.context.output_folder + 'result_map'
        self.Folium.create_folium_map(fileName, self.map_object)


    def draw_zip_code_polygons(self):
        """
        Draws the Polygons of the Zip Codes into the Folium Map
        """
        layer_color = '#00008B'
        layer_txt = 'Zip Codes'
        initial_show = False
        dynamic = False
        zip_codes_layer = self.Folium.create_feature_group_folium(self.map_object, layer_color, layer_txt, initial_show, dynamic)

        index_color = 0
        for file, geojson in self.spain_zip_codes_data.items():
            if file in self.context.parameters.city_name_zip_code_list:
                polygon_color, index_color = self.Folium.get_node_color(index_color, self.colors_high_contrast)
                for position in range(len(geojson['features'])):
                    single_geojson = geojson['features'][position]
                    single_geojson_id = single_geojson['properties']['COD_POSTAL']
                    tooltip = 'CP:' + str(single_geojson_id) + ' - ' + str(file)
                    self.Folium.add_polygon_to_map(single_geojson, zip_codes_layer, polygon_color, tooltip, tooltip)
            if file in self.context.parameters.city_name_zip_code_list:
                polygon_color, index_color = self.Folium.get_node_color(index_color, self.colors_high_contrast)
                for position in range(len(geojson['features'])):
                    single_geojson = geojson['features'][position]
                    single_geojson_id = single_geojson['properties']['COD_POSTAL']
                    tooltip = 'CP:' + str(single_geojson_id) + ' - ' + str(file)
                    self.Folium.add_polygon_to_map(single_geojson, zip_codes_layer, polygon_color, tooltip, tooltip)

    
    def draw_heat_map(self):
        """
        Draws the Heat Map of the Demand into the Folium Map
        """
        layer_color = '#00008B'
        layer_txt = 'Heat Map'
        initial_show = False
        dynamic = False
        heat_map_layer = self.Folium.create_feature_group_folium(self.map_object, layer_color, layer_txt, initial_show, dynamic)

        selected_columns = self.instance.nodes_df[['Latitude', 'Longitude', 'Items']]
        heat_map_data = selected_columns.values.tolist() # Convierte estas columnas en una lista de listas
        self.Folium.add_heat_map(heat_map_data, heat_map_layer)


    def draw_nodes(self):
        """
        Draws the Nodes into the Folium Map
        """
        layer_color = '#00008B'
        layer_txt = 'Nodes'
        initial_show = False
        dynamic = False               
        clients_layer = self.Folium.create_feature_group_folium(self.map_object, layer_color, layer_txt, initial_show, dynamic)
        for index, row in self.instance.nodes_df.iterrows():
            node_id = row['Id']
            if node_id == 0:
                continue
            node_name = row['Name']
            node_address = row['Address']
            node_zip_code = row['Zip_Code']
            node_lat = row['Latitude']
            node_lon = row['Longitude']
            node_demand = row['Items']
            node_tw_start = row['TW_Start']
            node_tw_end = row['TW_End']
            node_type = row['Node_Type']
            node_email = row['Email']
            node_phone = row['Phone']
            self.add_html_pop_up(node_id, node_name, node_address, node_zip_code, node_lat, node_lon, node_demand, node_tw_start, node_tw_end, node_type, node_email, node_phone, clients_layer)


    def add_html_pop_up(self, node_id: int, node_name: str, node_address: str, node_zip_code: str, node_lat: float, node_lon: float, node_demand: float, node_tw_start: str, node_tw_end: str, node_type: str, node_email: str, node_phone: str, clients_layer):
        """
        Adds the HTML Pop Up for the Client
        Params:
        - node_id: int - ID of the Client
        - node_name: str - Name of the Client
        - node_address: str - Address of the Client
        - node_population: str - Population of the Client's location
        - node_zip_code: str - Zip Code of the Client
        - node_key: str - Key identifier for the Client
        - node_lat: float - Latitude of the Client
        - node_lon: float - Longitude of the Client
        - node_demand: float - Demand of the Client
        - node_tw_start: str - Time window start for the Client
        - node_tw_end: str - Time window end for the Client
        - node_type: str - Type of the Client
        - clients_layer: FeatureGroup - Layer of the Clients on the map
        """
        left_col_color_1 = '#36454F' #'#2C3539' # Even row left color
        right_col_color_1 = '#FBFBF9' # Even row right color
        left_col_color_2 = '#36454F' # Odd row left color
        right_col_color_2 = '#FAF5EF' # Odd row right color
        html = self.Folium.add_beggining_HTML_table(node_name)
        html = html + self.Folium.add_row_to_HTML_table('Node Id:', node_id, None, left_col_color_1, right_col_color_1)
        html = html + self.Folium.add_row_to_HTML_table('Name:', node_name, None, left_col_color_2, right_col_color_2)
        html = html + self.Folium.add_row_to_HTML_table('Demand:', node_demand, '€', left_col_color_1, right_col_color_1)
        html = html + self.Folium.add_row_to_HTML_table('TW Start:', node_tw_start, None, left_col_color_2, right_col_color_2)
        html = html + self.Folium.add_row_to_HTML_table('Address:', node_address, None, left_col_color_1, right_col_color_1)
        html = html + self.Folium.add_row_to_HTML_table('Zip Code:', node_zip_code, None, left_col_color_2, right_col_color_2)
        html = html + self.Folium.add_row_to_HTML_table('TW End:', node_tw_end, None, left_col_color_1, right_col_color_1)
        html = html + self.Folium.add_row_to_HTML_table('Email:', node_email, None, left_col_color_2, right_col_color_2)
        html = html + self.Folium.add_row_to_HTML_table('Phone:', node_phone, None, left_col_color_1, right_col_color_1)
        html = html + self.Folium.add_row_to_HTML_table('Latitud:', node_lat, None, left_col_color_2, right_col_color_2)
        html = html + self.Folium.add_row_to_HTML_table('Longitud:', node_lon, None, left_col_color_1, right_col_color_1)
        html = html + self.Folium.add_end_HTML_table()

        tooltip_folium = 'Node ID: ' + str(node_id) + ' - ' + str(node_name)
        popup = self.Folium.create_pop_up(html)
        if node_demand < 0:
            icon_type = 'glyphicon-download'
            node_color = '#FF0000'
        else:
            icon_type = 'glyphicon-upload'
            node_color = '#008000'
        icon = self.Folium.create_icon(icon_type, node_color, 'black')
        self.Folium.create_marker( [node_lat, node_lon], popup, tooltip_folium, node_id, icon, clients_layer)


    def draw_unserved_nodes(self):
        """
        Draws the Unserved Nodes into the Folium Map
        """
        unserved_nodes = list(self.solution.unserved)
        unserved_nodes_df = self.instance.nodes_df.loc[self.instance.nodes_df['Id'].isin(unserved_nodes)]
        if len(unserved_nodes_df) > 0:
            layer_color = '#00008B'
            layer_txt = 'Unserved Nodes'
            initial_show = False
            dynamic = False               
            clients_layer = self.Folium.create_feature_group_folium(self.map_object, layer_color, layer_txt, initial_show, dynamic)
            for index, row in unserved_nodes_df.iterrows():
                node_id = row['Id']
                node_name = row['Name']
                node_address = row['Address']
                node_zip_code = row['Zip_Code']
                node_lat = row['Latitude']
                node_lon = row['Longitude']
                node_demand = row['Items']
                node_tw_start = row['TW_Start']
                node_tw_end = row['TW_End']
                node_type = row['Node_Type']
                node_email = row['Email']
                node_phone = row['Phone']
                self.add_html_pop_up(node_id, node_name, node_address, node_zip_code, node_lat, node_lon, node_demand, node_tw_start, node_tw_end, node_type, node_email, node_phone, clients_layer)


    def draw_routes(self):
        """
        Draws the Routes into the Folium Map
        """
        routes_df_list = self.IO.cluster_dataframe_by_condition(self.routes_df, 'Vehicle')
        layer_color = '#25383C' # '#25383C'	DarkSlateGray or DarkSlateGrey (W3C)
        initial_show = False
        dynamic = False
        index_color = 0
        for route_df in routes_df_list:
            vehicle_name = route_df['Vehicle'].values[0]
            route_load = route_df['Items'].sum()
            total_nodes = len(route_df) - 2
            layer_txt = 'Route ' + str(vehicle_name) + ' - Load: ' + str(route_load) + '€ Stops: ' + str(total_nodes)
            route_layer =  self.Folium.create_feature_group_folium(self.map_object, layer_color, layer_txt, initial_show, dynamic)
            node_color, index_color = self.Folium.get_node_color(index_color, self.colors_high_contrast)
            latitudes = [self.depot_coords[0]]
            longitudes = [self.depot_coords[1]]
            stops_counter = 1
            for index, node_df in route_df.iterrows():
                node_id = node_df['Id']
                node_name = node_df['Name']
                order_type = node_df['Type']
                address = node_df['Address']
                location = node_df['Location']
                province = node_df['Province']
                zip_code = node_df['Zip_Code']
                node_type = node_df['Node_Type']
                items = node_df['Items']
                lat = node_df['Latitude']
                long = node_df['Longitude']

                if order_type == '-':
                    continue

                latitudes.append(lat)
                longitudes.append(long)
                tooltip_folium = 'Node: ' + str(node_id) + '-' + str(node_name)
                self.add_route_html_node(route_layer, node_color, tooltip_folium, node_id, node_name, address, location, province, zip_code, node_type, items, lat, long, stops_counter)
                stops_counter = stops_counter + 1

            latitudes.append(self.depot_coords[0])
            longitudes.append(self.depot_coords[1])
            coordinates = self.Geo.create_list_of_list_coordinates(latitudes, longitudes)
            if len(coordinates) > 2:
                route_info_here = self.Here.calculate_route_HERE(coordinates, 'car', self.context.parameters.here_API_key)
                route_coordinates_here = route_info_here[0]
                route_distance = route_info_here[1]
                route_time = route_info_here[2]
                print('Route:', layer_txt, ' has a distance of ', route_distance, ' and a duration of ', route_time)
                self.Folium.add_route_to_map(route_coordinates_here, node_color, layer_txt, route_layer, 2)
                # self.Folium.add_route_to_map(coordinates, node_color, layer_txt, route_layer, 2)


    def add_route_html_node(self, route_layer, node_color, tooltip_folium, node_id, node_name, address, location, province, zip_code, node_type, items, lat, long, stops_counter):
        """
        Add node marker from route into route layer
        """
        left_col_color_1 = '#36454F' #'#2C3539' # Even row left color
        right_col_color_1 = '#FBFBF9' # Even row right color
        left_col_color_2 = '#36454F' # Odd row left color
        right_col_color_2 = '#FAF5EF' # Odd row right color

        html = self.Folium.add_beggining_HTML_table(node_name)
        html = html + self.Folium.add_row_to_HTML_table('Node Id', node_id, None, left_col_color_1, right_col_color_1)
        html = html + self.Folium.add_row_to_HTML_table('Name', node_name, None, left_col_color_2, right_col_color_2)
        html = html + self.Folium.add_row_to_HTML_table('Address', address, None, left_col_color_1, right_col_color_1)
        html = html + self.Folium.add_row_to_HTML_table('Location', location, None, left_col_color_2, right_col_color_2)
        html = html + self.Folium.add_row_to_HTML_table('Province', province, None, left_col_color_1, right_col_color_1)
        html = html + self.Folium.add_row_to_HTML_table('Zip Code', zip_code, None, left_col_color_2, right_col_color_2)
        html = html + self.Folium.add_row_to_HTML_table('Node Type', node_type, None, left_col_color_1, right_col_color_1)
        html = html + self.Folium.add_row_to_HTML_table('Items', items, None, left_col_color_2, right_col_color_2)
        html = html + self.Folium.add_row_to_HTML_table('Latitude', lat, None, left_col_color_1, right_col_color_1)
        html = html + self.Folium.add_row_to_HTML_table('Longitude', long, None, left_col_color_2, right_col_color_2)
        html = html + self.Folium.add_end_HTML_table()

        location = [lat, long]
        popup = self.Folium.create_pop_up(html)
        tooltip_folium = 'Node: ' + str(node_id)
        icon = self.Folium.create_circle_icon(node_color, stops_counter)
        self.Folium.create_marker(location, popup, tooltip_folium, node_name, icon, route_layer)


    def draw_depot(self):
        """
        Draws the depot
        """
        depot_id = str(self.depot_df['Id'])
        depot_name = str(self.depot_df['Name'])
        depot_address = str(self.depot_df['Address'])
        depot_zip_code = str(self.depot_df['Zip_Code'])
        depot_coordinates = [self.depot_df['Latitude'], self.depot_df['Longitude']]

        # Metrics Data
        total_routes = len(self.metrics_df)
        total_nodes = self.metrics_df['Total Nodes'].sum()
        total_picks_ups = self.metrics_df['Total Picks Ups'].sum()
        total_deliveries = self.metrics_df['Total Deliveries'].sum()
        current_load = self.metrics_df['Current Load'].sum()
        available_load = self.metrics_df['Available Load'].sum()
        current_distance = self.metrics_df['Current Distance'].sum()
        available_distance = self.metrics_df['Available Distance'].sum()

        left_col_color_1 = '#36454F' #'#2C3539' # Even row left color
        right_col_color_1 = '#FBFBF9' # Even row right color
        left_col_color_2 = '#36454F' # Odd row left color
        right_col_color_2 = '#FAF5EF' # Odd row right color
        html = self.Folium.add_beggining_HTML_table(depot_name)
        html = html + self.Folium.add_row_to_HTML_table('Depot:', depot_id, None, left_col_color_1, right_col_color_1)
        html = html + self.Folium.add_row_to_HTML_table('Name:', depot_name, None, left_col_color_2, right_col_color_2)
        html = html + self.Folium.add_row_to_HTML_table('Address:', depot_address, None, left_col_color_1, right_col_color_1)
        html = html + self.Folium.add_row_to_HTML_table('Zip Code:', depot_zip_code, None, left_col_color_2, right_col_color_2)
        html = html + self.Folium.add_row_to_HTML_table('Latitude:', depot_coordinates[0], None, left_col_color_1, right_col_color_1)
        html = html + self.Folium.add_row_to_HTML_table('Longitude:', depot_coordinates[1], None, left_col_color_2, right_col_color_2)
        html = html + self.Folium.add_row_to_HTML_table('Total Routes:', total_routes, 'rutas', left_col_color_1, right_col_color_1)
        html = html + self.Folium.add_row_to_HTML_table('Total Nodes:', total_nodes, 'nodos', left_col_color_2, right_col_color_2)
        html = html + self.Folium.add_row_to_HTML_table('Total Picks Ups:', total_picks_ups, 'nodos', left_col_color_1, right_col_color_1)
        html = html + self.Folium.add_row_to_HTML_table('Total Deliveries:', total_deliveries, 'nodos', left_col_color_2, right_col_color_2)
        html = html + self.Folium.add_row_to_HTML_table('Current Load:', current_load, '€', left_col_color_1, right_col_color_1)
        html = html + self.Folium.add_row_to_HTML_table('Available Load:', available_load, '€', left_col_color_2, right_col_color_2)
        html = html + self.Folium.add_row_to_HTML_table('Current Distance:', current_distance, 'm', left_col_color_1, right_col_color_1)
        html = html + self.Folium.add_row_to_HTML_table('Available Distance:', available_distance, 'm', left_col_color_2, right_col_color_2)
        html = html + self.Folium.add_end_HTML_table()

        tooltip_folium = 'Node ID: ' + str(depot_id) + ' - ' + str(depot_name)
        popup = self.Folium.create_pop_up(html)
        icon_type = 'glyphicon-home'
        icon = self.Folium.create_icon(icon_type, '#FFFFFF', 'black')
        self.Folium.create_marker(depot_coordinates, popup, tooltip_folium, depot_id, icon, self.map_object)

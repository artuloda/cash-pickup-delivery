import os
import json
import pandas as pd
import random
import folium
import base64
from folium.plugins import MarkerCluster, Search, MeasureControl, LocateControl, MiniMap, FeatureGroupSubGroup, Fullscreen, AntPath, PolyLineOffset, HeatMap, StripePattern, Geocoder, BeautifyIcon, MousePosition


class Folium:
    def __init__(self):
        pass

    def get_input_colors(self, colors_dataframe: pd.DataFrame, high_contrast: bool) -> list[str]:
        """Returns a list with the colors in hexadecimal format in random order.

        Parameters:
        colors_dataframe -- DataFrame object with the colors
        high_contrast -- Boolean to check if we want the high contrast colors

        Returns:
        List with the colors in hexadecimal format in random order
        """
        if not high_contrast:
            colors = colors_dataframe['HexCode'].values.tolist()
        else:
            colors = colors_dataframe[colors_dataframe['ContrastChk'] == 1]['HexCode'].values.tolist()
        random.shuffle(colors)
        return colors


    def get_node_color(self, index_color: int, colors: list[str]) -> tuple[str, int]:
        """Returns the color in the given position. If the index is out of the list, returns the corresponding to the position 0.

        Parameters:
        index_color -- Index of the color
        colors -- List with the colors

        Returns:
        Tuple with the color and the index
        """
        return colors[index_color], (index_color + 1) % len(colors)


    def initialize_folium_map(self, center_coords: tuple[float, float], logo_img_file: str) -> folium.Map:
        """
        Creates a folium map in a html file.

        Parameters:
        logo_img_file -- Path to the logo to show in the marker

        Return:
        map_object -- Folium object that is exported as an HTML file
        """
        
        map_object = folium.Map(location=center_coords, tiles="openstreetmap", zoom_start=10, control_scale=True)
        Fullscreen(position='topleft', title="Expand me", title_cancel="Exit me").add_to(map_object)
        self.add_logo_to_markers(logo_img_file, map_object)
        return map_object


    def create_folium_map(self, file_name: str, map_object: folium.Map):
        """Creates a folium map in a html file.

        Parameters:
        file_name -- Nombre del fichero (sin tipo de fichero)
        map_object -- Objeto Folium que se exporta como fichero HTML
        """
        folium.TileLayer(tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',attr='Esri', name='Esri Satellite',).add_to(map_object)
        folium.TileLayer(tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}',attr='Esri', name='Esri World Topographic Map',).add_to(map_object)
        folium.TileLayer('cartodbpositron', name='Carto BD Positron').add_to(map_object)
        MiniMap(tile_layer='openstreetmap', position='bottomleft', toggle_display=True).add_to(map_object)
        MeasureControl(position='bottomleft').add_to(map_object)
        MousePosition(position='bottomright').add_to(map_object)
        Geocoder(position='topleft', collapsed=True, placeholder="Geocoder Folium").add_to(map_object)
        folium.LayerControl(collapsed=False).add_to(map_object)
        folium.LatLngPopup().add_to(map_object)  # Cuando pinchas te da lat long

        print("Creating File MAP: ", file_name)
        map_object.save(file_name + '.html')
        print("File MAP: ", file_name, ' created.')


    def create_marker(self, location: tuple[float, float], popup: folium.Popup, tooltip_folium: str, node_name: str, icon: folium.Icon, folium_layer: folium.FeatureGroup):
        """
        Creates Folium Marker

        Parameters:
        location -- Array [latitude, longitude]
        popup -- Folium pop up object
        tooltip_folium -- String shown when hover over the marker
        node_name -- Marker Id, if we add search
        icon -- Folium icon object
        folium_layer -- Folium layer
        """
        folium.Marker(location=location, popup=popup, tooltip=tooltip_folium, name=node_name, icon=icon).add_to(folium_layer)


    def create_circle_marker(self, location: tuple[float, float], popup: folium.Popup, tooltip: str, node_color: str, folium_layer: folium.FeatureGroup):
        """
        Creates a Folium Circle Marker

        Parameters:
        location -- Array [latitude, longitude]
        radius -- Radius of the circle
        color -- Hexadecimal color of the circle
        folium_layer -- Folium layer
        """
        folium.Circle(location=location, popup=popup, tooltip=tooltip, fill_color=node_color, radius=30, fill_opacity=1, weight=1, color='black').add_to(folium_layer)

    def create_icon(self, icon_name: str, icon_color: str, color: str) -> folium.Icon:
        """
        Creates a Folium Icon

        Parameters:
        icon_name -- Hexadecimal color of the node
        icon_color -- Hexadecimal color of the node
        color -- Folium Color for the marker. ['red', 'blue', 'green', 'purple', 'orange', 'darkred', 'lightred', 'beige', 'darkblue', 'darkgreen', 'cadetblue', 'darkpurple', 'white', 'pink', 'lightblue', 'lightgreen', 'gray', 'black', 'lightgray']
        prefix -- Prefix if we use FontAwesome Markers
        angle -- Angle of the icon: 45, 90, 135, 180.

        Return:
        icon -- Folium Icon
        """
        icon = folium.Icon(color=color, icon=icon_name, icon_color=icon_color)
        # if prefix == None:
        #     icon = folium.Icon(color=color, icon=icon_name, icon_color=icon_color, angle=angle)
        # else:
        #     icon = folium.Icon(color=color, icon=icon_name, icon_color=icon_color, prefix=prefix, angle=angle)
        return icon


    def create_circle_icon(self, color: str, number: int) -> BeautifyIcon:
        """
        Creates a Folium Circle Icon With Number

        Parameters:
        color -- Hexadecimal color of the node
        number -- Number inside the marker

        Return:
        icon -- Folium Circle Icon With Number
        """
        icon = BeautifyIcon(border_color=color,text_color=color,number=number,inner_icon_style="margin-top:0;")
        return icon
    
    
    def create_pop_up(self, html: str) -> folium.Popup:
        """
        Creates a Folium Pop Up.

        Parameters:
        html -- HTML Code within the pop up

        Return:
        pop_up -- Folium Pop Up
        """
        pop_up = folium.Popup(folium.Html(html, script=True), max_width=500)
        return pop_up
    

    def add_logo_to_markers(self, logo_img_file: str, map_object: folium.Map):
        """
        Adds logo to HTML Table Markers

        Parameters:
        logo_img_file -- Ruta del logo a mostrar en el marcador
        map_object -- Objeto Folium que se exporta como fichero HTML
        """
        encoded_img_file = base64.b64encode(open(logo_img_file, 'rb').read()).decode()
        html = """
        <style>
            .CompanyLogo {
                background-image: url(data:image/png;base64,""" + encoded_img_file + """);
                    width: 150px;  
                    height: 100px; 
                    background-position: center center; 
                    background-repeat: no-repeat; 
                    background-size: contain; 
            }
        </style>
        """
        map_object.get_root().html.add_child(folium.Element(html))


    def add_beggining_HTML_table(self, node_id: str) -> str:
        """
        Creates the beginning of an HTML table with format

        Parameters:
        node_id -- Id of the node

        Returns:
        HTML code
        """
        html = """

        <!DOCTYPE html>
        <html>  
        <head><meta charset="latin-1"></head>
        <center><figure><div class="CompanyLogo" width=80></div></figure></center>
        <center><h4 style="font-family: 'system-ui'"; font-size: "11px"; "margin-bottom:5">{}</h4>""".format(node_id) + """</center>
        <center> <table style="height: 126px; width: 305px;">
        <tbody>
        """
        return html
    

    def add_beggining_HTML_table_no_logo(self, node_id: str) -> str:
        """
        Creates the beginning of an HTML table with format

        Parameters:
        node_id -- Id of the node

        Returns:
        HTML code
        """
        html = """

        <!DOCTYPE html>
        <html>  
        <head><meta charset="latin-1"></head>
        <center><h4 style="font-family: 'system-ui'"; font-size: "11px"; "margin-bottom:5">{}</h4>""".format(node_id) + """</center>
        <center> <table style="height: 126px; width: 305px;">
        <tbody>
        """
        return html


    def add_end_HTML_table(self) -> str:
        """
        Creates the end of an HTML table with format

        Returns:
        HTML code
        """
        # <center>hosted by <span style="font-family: 'system-ui'; font-size: 28px; color:#FE632A">{}</span>""".format('decide') + """</center>
        html = """</tbody></table></center>
        </html>"""
        return html
    

    def add_end_HTML_table_with_plot(self, img_str: str, plot_name: str) -> str:
        """
        Creates the end of an HTML table with format and a plot

        Returns:
        HTML code
        """
        html = """</tbody></table></center>
        <center><img src="data:image/png;base64,{}" alt="{}" style="width: 100%; height: auto;"></center>"""
        return html


    def add_row_to_HTML_table(self, text_name: str, text_value: str, units: str, left_col_color: str, right_col_color: str) -> str:
        """Creates a row of an HTML table with the text and the colors by parameter.

        Parameters:
        text_name -- Text of the row
        text_value -- Value of the row
        units -- Units of the value
        left_col_color -- Color of the left column
        right_col_color -- Color of the right column

        Returns:
        HTML code
        """
        if units == None:
            html = """
            <tr style="border: 1px solid #dddddd">
                <td style="background-color: """+ left_col_color +""";font-family: 'system-ui';font-size: 11px;"><span style="color: #ffffff;">&nbsp;<strong>""" + str(text_name) + """</strong></span></td>
                <td style="width: 150px;background-color: """+ right_col_color +""";">&nbsp;""" + str(text_value) + """</td>
            </tr>"""
        else:
            html = """
            <tr style="border: 1px solid #dddddd">
                <td style="background-color: """+ left_col_color +""";font-family: 'system-ui';font-size: 11px;"><span style="color: #ffffff;">&nbsp;<strong>""" + str(text_name) + """</strong></span></td>
                <td style="width: 150px;background-color: """+ right_col_color +""";">&nbsp;""" + str(text_value) + ' ' + str(units) +"""</td>
            </tr>"""
        return html


    def add_polygon_to_map(self, feature_collection: str, folium_layer: folium.plugins.FeatureGroupSubGroup, polygon_color: str, tooltip_folium: str, polygon_id: str):
        """Adds a GeoJon polygon to a Folium object.

        Parameters:
        feature_collection -- FeatureCollection object
        folium_layer -- Folium layer
        polygon_color -- Color of the polygon
        tooltip_folium -- Tooltip of the polygon
        polygon_id -- Id of the polygon
        """
        style_function=lambda x, fillColor=polygon_color: {
            "fillColor": fillColor,
            "color": "black",
            "weight": 0.8,
            "fillOpacity": 0.3}

        highlight_function=lambda feature: {
            "fillOpacity": 0.8,
            "weight": 0.9}

        folium.GeoJson(feature_collection, tooltip=tooltip_folium, style_function=style_function, highlight_function=highlight_function, name=polygon_id, zoom_on_click=True).add_to(folium_layer)


    def create_feature_group_folium(self, map_object: folium.Map, layer_color: str, layer_txt: str, initial_show: bool, dynamic: bool) -> folium.FeatureGroup:
        """Creates a Folium layer

        Parameters:
        map_object -- (Folium Map) Objeto folium que representa el mapa
        layer_color -- (str) Color en hexadecimal
        layer_txt -- (str) Texto de la capa
        initial_show -- (boolean) True: Se muestra por defecto, False: Aparece desmarcado en la leyenda
        dynamic -- (boolean) True: marcadores dinamicos, False: marcadores estaticos

        Return:
        folium_layer -- (Folium Layer) Objto folium que contiene una capa del mapa
        """
        layer_name = """<span style="font-family: 'system-ui'; font-size: 15px;  color:""" + str(layer_color) + """ ">{txt}</span>"""
        if not dynamic:
            folium_layer = folium.FeatureGroup(name=layer_name.format(txt=layer_txt), show=initial_show).add_to(map_object)
        else:
            folium_layer = MarkerCluster(name=layer_name.format(txt=layer_txt), show=initial_show).add_to(map_object)
        return folium_layer


    def create_feature_subgroup_folium(self, map_object: folium.Map, layer_color: str, layer_txt: str, initial_show: bool, folium_layer: folium.FeatureGroup) -> folium.plugins.FeatureGroupSubGroup:
        """Creates a sublayer Folium

        Parameters:
        map_object -- (Folium Map) Folium object that represents the map
        layer_color -- (str) Hexadecimal color
        layer_txt -- (str) Texto de la capa
        initial_show -- (boolean) True: Se muestra por defecto, False: Aparece desmarcado en la leyenda
        folium_layer -- (Folium Layer) Capa del mapa en la que vamos a introducir la subcapa

        Return:
        subgroup_layer -- (Folium Layer) Objto folium que contiene una subcapa del mapa
        """
        layer_name = """<span style="font-family: 'system-ui'; font-size: 13px;  color:""" + str(layer_color) + """ ">{txt}</span>"""
        subgroup_layer = FeatureGroupSubGroup(folium_layer, layer_name.format(txt=layer_txt),show=initial_show).add_to(map_object)
        return subgroup_layer


    def create_feature_collection_from_list_of_coordinates(self, coordinates_list: list[tuple[float, float]], feature_collection_name: str) -> str:
        """Creates a JSON representation of a FeatureCollection object that contains the given list of coordinates.

        Parameters:
        coordinates_list -- List of coordinates
        feature_collection_name -- Name of the feature collection

        Returns:
        JSON representation of a FeatureCollection object
        """
        coordinates_reversed = [[lon, lat] for lat, lon in coordinates_list]  # Reverse the order of each coordinate in the list
        # Define the GeoJSON data
        data = {"type": "FeatureCollection",
                "features": [{"type": "Feature",
                            "geometry": {"type": "Polygon",
                                        "coordinates": [coordinates_reversed]},
                            "properties": {"name": feature_collection_name,
                                            "description": "Polygon description"}}]}
        geojson_str = json.dumps(data)  # Convert the dictionary to a JSON string
        return geojson_str


    def add_route_to_map(self, coordinates: list[tuple[float, float]], line_color: str, tooltip_folium: str, folium_layer: folium.FeatureGroup, line_option: int):
        """Calculates route

        Parameters:
            coordinates -- (List[List[float, float]]) lista de coordenadas
            line_color -- (string) color del nodo
            tooltip_folium -- (string) nombre de la ruta
            folium_layer -- (FeatureGroupSubGroup) TODO
            line_option -- (integer) TODO
        """
        # 1: Polyline, 2:AntPath, 3:PolylineOffSet
        if line_option == 1:
            folium.PolyLine(coordinates, color=line_color, weight=5, tooltip=tooltip_folium).add_to(folium_layer)
        elif line_option == 2:
            AntPath(coordinates, dash_array=[8, 100], delay=800, tooltip=tooltip_folium, color=line_color).add_to(folium_layer)
        elif line_option == 3:
            PolyLineOffset(coordinates, dash_array="5,10", color=line_color, weight=5, tooltip=tooltip_folium, opacity=1).add_to(folium_layer)


    def get_spain_zip_codes(self, folder_path: str) -> dict[str, dict]:
        """
        Lee los ficheros de los códigos postales de España y los almacena en un diccionario

        Parameters:
            folder_path -- (str) Path to the file

        Return:
            spain_zip_codes_data -- (dict) Dictionary with the Spain zip codes
        """
        folder_path = folder_path + 'SPAIN_geojsons'
        files = os.listdir(folder_path) # List all files in the specified folder
        #print("Files in the folder:") # Print the list of files
        #print(files)
        spain_zip_codes_data = dict()
        for file in files:  # Process each file in the folder        
            file_path = os.path.join(folder_path, file) # Construct the full file path
            if os.path.isfile(file_path): # Check if the path is a file (not a directory)           
                with open(file_path, 'r') as geojson_file:  # Perform operations on the file, for example, read its content
                    zip_codes_geojson = json.load(geojson_file)
                    file_name = file.split('.')[0]
                    spain_zip_codes_data[file_name] = zip_codes_geojson
        return spain_zip_codes_data
    

    def get_spain_provinces(self, folder_path: str) -> dict[str, dict]:
        """
        Lee los ficheros de las provincias de España y las almacena en un diccionario

        Parameters:
            folder_path -- (str) Path to the file

        Return:
            spain_provinces_data -- (dict) Dictionary with the Spain provinces
        """
        file_name = 'spain-provinces.geojson'
        file_path = folder_path + file_name
        provinces_data = dict()
        if os.path.isfile(file_path): # Check if the path is a file (not a directory)           
            with open(file_path, 'r', encoding='utf-8') as geojson_file:
                privinces_geojson = json.load(geojson_file)
                for feature in privinces_geojson['features']:
                    province_name = feature['properties']['name']
                    provinces_data[province_name] = feature
        return provinces_data


    def add_heat_map(self, heat_map_data: list[list[float, float, float]], folium_layer: folium.FeatureGroup):
        """Creates a heat map and assigns it to a layer

        Parameters:
            heat_map_data -- (List[List[Latitude, Longitude, Value]]) list of coordinates and value of the heat map
            folium_layer -- (FeatureGroupSubGroup) Layer of the map in which we want to insert the sublayer
        """
        HeatMap(heat_map_data).add_to(folium_layer)


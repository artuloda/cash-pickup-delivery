import math
import pandas as pd
from geopy.distance import geodesic
from shapely.geometry import Point, LineString, Polygon, LinearRing

class Geo:
    def __init__(self):
        pass

    def calculate_distance(self, coord1: tuple[float, float], coord2: tuple[float, float]) -> float:
        """
        Calculates distance in kilometers
        Parameters:
        coord1 -- Coordinate 1
        coord2 -- Coordinate 2

        Returns:
        Distance in meters
        """
        #return math.ceil(geodesic(coord1, coord2).meters)
        return geodesic(coord1, coord2).kilometers
    

    def signed_polygon_area(self, vertices: list[tuple[float, float]]) -> float:
        """Calculates the area of a polygon using its list of vertices.
        
        Parameters:
        vertices -- List of vertices

        Returns:
        Area of the polygon
        """
        num_vertices = len(vertices)
        area = 0

        for i in range(num_vertices):
            x1, y1 = vertices[i]
            x2, y2 = vertices[(i + 1) % num_vertices]
            area += (x1 * y2) - (x2 * y1)
        return area / 2


    def calculate_centroid(self, latitudes: list[float], longitudes: list[float]) -> tuple[float, float]:
        """Calculates the centroid of a list of points.

        Parameters:
        latitudes -- List of latitudes
        longitudes -- List of longitudes

        Returns:
        Coordinates of the centroid corresponding to a list of points.
        """
        vertices = list(zip(latitudes, longitudes))
        num_vertices = len(vertices)
        area = self.signed_polygon_area(vertices)
        if area == 0:
            return vertices[0]

        x_sum = 0
        y_sum = 0

        for i in range(num_vertices):
            x1, y1 = vertices[i]
            x2, y2 = vertices[(i + 1) % num_vertices]
            common_term = (x1 * y2) - (x2 * y1)
            x_sum += (x1 + x2) * common_term
            y_sum += (y1 + y2) * common_term

        center_x = x_sum / (6 * area)
        center_y = y_sum / (6 * area)

        return center_x, center_y


    def polar_angle_sort(self, coords_list: list[tuple[float, float]]) -> list[tuple[float, float]]:
        """Orders the list of coordinates given using its polar angle.

        Parameters:
        coords_list -- List of coordinates

        Returns:
        Ordered list of coordinates
        """
        cent = (sum([p[0] for p in coords_list])/len(coords_list), sum([p[1] for p in coords_list])/len(coords_list))  # compute centroid
        coords_list.sort(key=lambda p: math.atan2(p[1]-cent[1], p[0]-cent[0]))  # sort by polar angle
        return coords_list
    

    def get_polygon_shape(self, coords_list: list[tuple[float, float]]) -> list[tuple[float, float]]:
        """Returns the polygon shape given a list of coordinates.

        Parameters:
        coords_list -- List of coordinates

        Returns:
        Polygon shape
        """
        polygon_object = None
        if len(coords_list) == 1:
            polygon_object = Point(coords_list[0])
        elif len(coords_list) == 2:
            polygon_object = LineString(coords_list)
        elif len(coords_list) >= 3:
            if coords_list[0] == coords_list[-1]:
                polygon_object = Polygon(coords_list)
            else:
                polygon_object = Polygon(LinearRing(coords_list))

        if not polygon_object.is_valid:
            coords_list = self.polar_angle_sort(coords_list)
            if len(coords_list) == 1:
                polygon_object = Point(coords_list[0])
            elif len(coords_list) == 2:
                polygon_object = LineString(coords_list)
            elif len(coords_list) >= 3:
                if coords_list[0] == coords_list[-1]:
                    polygon_object = Polygon(coords_list)
                else:
                    polygon_object = Polygon(LinearRing(coords_list))
                    
        if not polygon_object.is_valid:
            polygon_object = polygon_object.simplify(1)

        return polygon_object


    def create_list_of_tuples_coordinates(self, latitudes: list[float], longitudes: list[float]) -> list[tuple[float, float]]:
        """Returns a list of tuples with the coordinates corresponding to the given lists of latitudes and longitudes.

        Parameters:
        latitudes -- List of latitudes
        longitudes -- List of longitudes

        Returns:
        List of coordinates
        """
        coordinates_list = list()
        for pos in range(len(latitudes)):
            coordinate = (float(latitudes[pos]), float(longitudes[pos]))
            coordinates_list.append(coordinate)
        return coordinates_list


    def create_list_of_list_coordinates(self, latitudes: list[float], longitudes: list[float]) -> list[list[float]]:
        """Returns a list of lists with the coordinates corresponding to the given lists of latitudes and longitudes.

        Parameters:
        latitudes -- List of latitudes
        longitudes -- List of longitudes

        Returns:
        List of coordinates
        """
        coordinates_list = list()
        for pos in range(len(latitudes)):
            coordinate = [float(latitudes[pos]), float(longitudes[pos])]
            coordinates_list.append(coordinate)
        return coordinates_list
    

    def is_node_in_polygon(self, node_latitude: float, node_longitude: float, polygon_coordinates: list[tuple[float, float]]) -> bool:
        """
        Validate if a node is in a polygon

        Parameters:
        node_latitude -- Latitude of the node
        node_longitude -- Longitude of the node
        polygon_geojson -- GeoJSON of the polygon

        Returns:
        is_in -- True if the node is in the polygon, False otherwise
        """
        polygon = self.get_polygon_shape(polygon_coordinates)
        point = Point(node_latitude, node_longitude)
        is_node_in_polygon = False
        if point.intersects(polygon):
            is_node_in_polygon = True
        return is_node_in_polygon
    

    def is_node_in_geojson(self, node_latitude: float, node_longitude: float, polygon_geojson: dict) -> bool:
        """
        Validate if a node is in a polygon

        Parameters:
        node_latitude -- Latitude of the node
        node_longitude -- Longitude of the node
        polygon_geojson -- GeoJSON of the polygon

        Returns:
        is_in -- True if the node is in the polygon, False otherwise
        """
        point = Point(node_longitude, node_latitude)
        if polygon_geojson['type'] == 'FeatureCollection':
            for feature in polygon_geojson['features']:
                geometry = feature['geometry']
                if geometry['type'] == 'Polygon':
                    polygon = Polygon(geometry['coordinates'][0])
                    if polygon.contains(point):
                        return True
                elif geometry['type'] == 'MultiPolygon':
                    for coords in geometry['coordinates']:
                        polygon = Polygon(coords[0])
                        if polygon.contains(point):
                            return True
        return False


    def combine_geojsons(self, geojsons_list: list[dict]) -> dict:
        """
        Combines two GeoJSON objects

        Parameters:
        geojsons_list -- (list[dict]) List of GeoJSON objects

        Returns:
        combined_geojson -- (dict) Combined GeoJSON object
        """
        combined_geojson = {"type": "FeatureCollection","features": []}
        for geojson in geojsons_list:
            combined_geojson['features'].append(geojson)
        return combined_geojson
    

    def calculate_matrix(self, matrix_df: pd.DataFrame, nodes_id_list: list[int], column_name: str, origin_column: str, destination_column: str, depot_id: str) -> pd.DataFrame:
        """
        Calculates matrix dataframe and matrix list of list
        Parameters:
        matrix_df -- Contains the origin distance matrix in node_origin-node_destination format
        nodes_id_list -- Ids of the nodes to calculate the matrix
        column_name -- Unit of the matrix: Time(time) or Distance(distance)
        origin_column -- Name of the column of the Origin Node ID in matrix_df 
        destination_column -- Name of the column of the Destination Node ID in matrix_df 
        depot_id -- Depot Id 

        Returns:
        New matrix Dataframe
        """
        # Ensure depot_id is first and include all nodes in nodes_id_list
        idx = [depot_id] + [id for id in nodes_id_list if id != depot_id]
        
        # Convert columns to string to match node_pairs_list format
        matrix_df['origin_destination'] = matrix_df['origin_destination'].astype(str)
        matrix_df[origin_column] = matrix_df[origin_column].astype(str)
        matrix_df[destination_column] = matrix_df[destination_column].astype(str)
        
        # Create a list of node pairs
        node_pairs_list = [str(node1) + '-' + str(node2) for node1 in idx for node2 in idx]
        # Filter the matrix_df to include only the node pairs
        filtered_matrix_df = matrix_df[matrix_df['origin_destination'].isin(node_pairs_list)]
        # Create a pivot table and reindex to include all nodes
        new_matrix_df = filtered_matrix_df.pivot(index=origin_column, columns=destination_column, values=column_name).reindex(index=idx, columns=idx).fillna(0).astype(float)
        return new_matrix_df

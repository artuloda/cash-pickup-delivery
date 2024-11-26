from utils import IO
import random
import numpy as np

class Parameters:
    def __init__(self):
        self.IO = IO()
        self.seed = self.set_seed()
        parameters_df = self.IO.read_csv(file_path='input_files/parameters.csv', separator=';', decimal='.', encoding='utf-8')
        parameters_dict = dict(zip(parameters_df['Parameter'], parameters_df['Value']))
        self.input_file_path = str(parameters_dict['input_file_path'])
        self.output_file_path = str(parameters_dict['output_file_path'])
        self.here_API_key = str(parameters_dict['here_API_key'])
        self.city_name_zip_code_list = str(parameters_dict['city_name_zip_code_list'])
        self.ALGORITHM_OPTION = int(parameters_dict['ALGORITHM_OPTION'])
        self.MAX_STOCK = int(parameters_dict['MAX_STOCK'])
        self.VEHICLE_CAPACITY = int(parameters_dict['VEHICLE_CAPACITY'])
        self.MAX_KM = int(parameters_dict['MAX_KM'])
        self.USE_ALL_FLEET = bool(parameters_dict['USE_ALL_FLEET'])
        self.n_services = int(parameters_dict['n_services'])
        self.n_vehicles = int(parameters_dict['n_vehicles'])


    def set_seed(self):
        """
        Set the seed for the random number generator
        """
        random_seed = 12345678 # random.randint(1, 1000000000)
        random.seed(random_seed)
        np.random.seed(random_seed)
        return random_seed


    def __str__(self) -> str:
        class_str = 'Instance seed: ' + str(self.seed) + '\n'
        class_str += 'Instance input_file_path: ' + str(self.input_file_path) + '\n'
        class_str += 'Instance output_file_path: ' + str(self.output_file_path) + '\n'
        class_str += 'Instance here_API_key: ' + str(self.here_API_key) + '\n'
        class_str += 'Instance city_name_zip_code_list: ' + str(self.city_name_zip_code_list) + '\n'
        class_str += 'Instance ALGORITHM_OPTION: ' + str(self.ALGORITHM_OPTION) + '\n'
        class_str += 'Instance MAX_STOCK: ' + str(self.MAX_STOCK) + '\n'
        class_str += 'Instance VEHICLE_CAPACITY: ' + str(self.VEHICLE_CAPACITY) + '\n'
        class_str += 'Instance MAX_KM: ' + str(self.MAX_KM) + '\n'
        class_str += 'Instance USE_ALL_FLEET: ' + str(self.USE_ALL_FLEET) + '\n'
        class_str += 'Instance n_services: ' + str(self.n_services) + '\n'
        class_str += 'Instance n_vehicles: ' + str(self.n_vehicles) + '\n'
        return class_str
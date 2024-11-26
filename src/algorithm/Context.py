from utils import IO, Logger
# from .Parameters import Parameters
from algorithm import Parameters

class Context:
    def __init__(self):
        self.parameters = Parameters()
        self.output_folder = self.create_execution_folder()
        self.logger = self.initialize_logger()


    def create_execution_folder(self):
        """ Creates a directory to store execution data
        """
        # Creates output_files folder
        output_folder = self.parameters.output_file_path
        IO().create_folder_if_not_exist(output_folder)

        # Creates execution output folder
        output_folder += 'Alg_' + str(self.parameters.ALGORITHM_OPTION)
        if self.parameters.USE_ALL_FLEET:
            output_folder += '_AllFleet'
        else:
            output_folder += '_MinFleet'

        IO().create_folder_if_not_exist(output_folder)
        output_folder += '/'
        return output_folder


    def initialize_logger(self):
        """Initialize the logger.
        Returns:
            Logger: The logger.
        """
        log_path = self.output_folder + 'execution_log.log'
        self.logger = Logger(log_file=log_path, option=1) 
        return self.logger


    def __str__(self) -> str:
        class_str = 'Context parameters: ' + str(self.parameters) + '\n'
        return class_str
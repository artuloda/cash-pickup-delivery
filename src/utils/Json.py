import json

class Json:

    def __init__(self):
        pass


    def pretty_print_json(self, json_data: dict):
        """Pretty print JSON data.
        Parameters:
            json_data (dict): JSON data to be pretty printed.
        """
        print(json.dumps(json_data, indent=4))


    def load_json_from_file(self, file_path: str) -> dict:
        """Load JSON data from a file.
        Parameters:
            file_path (str): Path to the file containing the JSON data.
        Returns:
            dict: JSON data loaded from the file.
        """
        with open(file_path, 'r') as file:
            return json.load(file)


    def write_json_to_file(self, json_data: dict, file_path: str):
        """Write JSON data to a file.
        Parameters:
            json_data (dict): JSON data to be written to the file.
            file_path (str): Path to the file where the JSON data will be written.
        """
        with open(file_path, 'w') as file:
            json.dump(json_data, file, indent=4)


    def update_json_data(self, original_data: dict, update_data: dict) -> dict:
        """Update JSON data with new data.
        Parameters:
            original_data (dict): Original JSON data.
            update_data (dict): New data to be added to the original JSON data.
        Returns:
            dict: Updated JSON data.
        """
        original_data.update(update_data)
        return original_data


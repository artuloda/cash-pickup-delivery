import pandas as pd
import os
import unicodedata

class IO:
    def __init__(self):
        pass

    def read_csv(self, file_path: str, separator: str, decimal: str, encoding: str) -> pd.DataFrame:
        """
        Read CSV file from given path

        Parameters:
        file_path -- Path to the CSV file
        separator -- Separator used in the CSV file
        decimal -- Decimal used in the CSV file
        encoding -- Encoding used in the CSV file

        Returns:
        Dataframe object
        """
        return pd.read_csv(file_path, sep=separator, decimal=decimal, encoding=encoding)
    

    def read_excel(self, file_path: str) -> pd.DataFrame:
        """
        Read CSV file from given path

        Parameters:
        file_path -- Path to the CSV file

        Returns:
        Dataframe object
        """
        return pd.read_excel(file_path)
    

    def read_excel_multiple_sheets(self, file_path: str, sheet_names: list[str]) -> dict[str, pd.DataFrame]:
        """
        Read an Excel file from the given path and return a dictionary of DataFrames

        Parameters:
        file_path -- Path to the Excel file
        sheet_names -- List of sheet names to read

        Returns:
        Dictionary with sheet names as keys and DataFrames as values
        """
        # Create a dictionary to store the DataFrames
        data_frames_dict = {}

        # Read the specified sheets from the Excel file
        for sheet_name in sheet_names:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            data_frames_dict[sheet_name] = df

        return data_frames_dict


    def create_csv(self, output_df: pd.DataFrame, file_name: str, index: bool = False):
        """
        Creates CSV or Excel from dataframe

        Parameters:
        output_df -- Dataframe object
        file_name -- Name of the file
        """
        try:
            output_df.to_csv(file_name + '.csv', sep=';', index=index, encoding='latin-1', columns=output_df.columns, decimal=',')
        except UnicodeEncodeError as ex:
            print("ERROR al crear CSV, intentamos con excel...", ex)
            output_df.to_excel(file_name + '.xlsx') 


    def create_CSV_from_list(self, list_of_objects: list[list], columns_name: list[str], file_name: str) -> pd.DataFrame:
        """Create a CSV file using a list of objects using pandas. Utilizes ';' as a separator.

        Parameters:
        list_of_objects -- Lista de objetos que se exportaran en el fichero CSV
        columns_name -- Nombres para las columnas del CSV
        file_name -- Nombre del fichero CSV (sin incluir la terminacion .csv)

        Returns:
        Dataframe object
        """
        output_data = self.create_dataframe(list_of_objects, columns_name)
        try:
            output_data.to_csv(file_name + '.csv', sep=';', index=False, encoding='latin-1', columns=columns_name, decimal=',')
        except UnicodeEncodeError:
            print("ERROR al crear CSV, intentamos con excel...")
            output_data.to_excel(file_name + '.xlsx') 
        return output_data


    def create_dataframe(self, list_of_objects: list[list], columns_name: list[str]) -> pd.DataFrame:
        """
        Creates Datafame

        Parametros:
        list_of_objects -- Lista de objetos que se exportaran en el fichero CSV
        columns_name -- Nombres para las columnas del CSV

        Output:
        Dataframe Object
        """
        return pd.DataFrame(list_of_objects, columns=columns_name)
    

    def create_dict_from_dataframe(self, input_dataframe: pd.DataFrame, id_column: str) -> dict:
        """
        Parameters:
        input_dataframe -- Input DataFrame over which to iterate to form the list
        id_column -- Column to use as id

        Output:
        Python dictionary
        """
        new_dict = dict()
        for index, row in input_dataframe.iterrows():
            new_dict[row[id_column]] = dict(row)
        return new_dict
    

    def drop_dataframe_duplicates(self, input_dataframe: pd.DataFrame, subset: list[str]) -> pd.DataFrame:
        """
        Drop duplicates from a dataframe

        Parameters:
        input_dataframe -- Input DataFrame over which to iterate to form the list
        subset -- Columns to drop duplicates

        Output:
        Dataframe object without duplicates
        """
        return input_dataframe.drop_duplicates(subset=subset)
    

    def cluster_dataframe_by_condition(self, input_dataframe: pd.DataFrame, condition: str) -> list[pd.DataFrame]:
        """Create a list with the DataFrame that meet a given condition.

        Parameters:
        input_dataframe -- Input DataFrame over which to iterate to form the list
        condition -- Condicion por la que filtrar los elementos que se a�aden a la lista

        Output:
        Una lista con los DataFrame que cumplen la condicion.
        """
        clustered_dataframes_list = list()
        for i in input_dataframe[condition].unique():
            clustered_dataframes_list.append(input_dataframe[input_dataframe[condition] == i])
        return clustered_dataframes_list
    

    def remove_accents(self, input_str: str) -> str:
        """
        Removes accents from a string.

        Parameters:
        input_str -- The string from which accents are to be removed.

        Returns:
        str: The string without accents.
        """
        # Normalize the string and then remove diacritic marks
        nfkd_form = unicodedata.normalize('NFKD', input_str)
        return "".join([c for c in nfkd_form if not unicodedata.combining(c)])

    
    def remove_non_alpha_numeric_str(self, input_string: str) -> str:
        """Remove all non alphanumeric character in string

        Parameters:
        input_string -- String with non alphanumeric characters
        """
        mod_string = ""
        for elem in input_string:
            if elem.isalnum() or elem == ' ':
                mod_string += elem
        result_string = mod_string
        result_string = result_string.replace('  ', ' ')
        return result_string


    def create_folder_if_not_exist(self, folder_path: str):
        """
        Create Folder if not exists in given folder_path

        Parameters:
        folder_path -- Path to the folder
        """
        path = os.path.join(folder_path)
        isExist = os.path.exists(path)
        if not isExist:
            os.mkdir(path)
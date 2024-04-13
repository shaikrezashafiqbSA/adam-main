import gspread
import pandas as pd

class GspreadHandler:
    def __init__(self, 
                #  credentials_filepath='./gdrive/lunar-landing-389714-369d3f1b2a09.json',
                 credentials_filepath='./gdrive/caramel-clock-418606-7475ecc43656.json'
                 ):
        self.credentials_filepath = credentials_filepath
        self.gc = gspread.service_account(filename=self.credentials_filepath)

    def get_sheet(self, sheet_name, worksheet_name):
        """
        Get a worksheet from a Google Sheet.

        Args:
            sheet_name (str): The name of the Google Sheet.
            worksheet_name (str): The name of the worksheet within the Google Sheet.

        Returns:
            gspread.Worksheet: The worksheet object.
        """
        sh = self.gc.open(sheet_name).worksheet(worksheet_name)
        return sh

    def get_cell_value(self, sheet_name, worksheet_name, cell_col_row='A1'):
        """
        Get the value of a cell in a Google Sheet.

        Args:
            sheet_name (str): The name of the Google Sheet.
            worksheet_name (str): The name of the worksheet within the Google Sheet.
            cell_col_row (str, optional): The cell address (e.g., 'A1'). Defaults to 'A1'.

        Returns:
            str: The value of the cell.
        """
        sh = self.get_sheet(sheet_name, worksheet_name)
        return sh.acell(cell_col_row).value

    def update_cell(self, data, sheet_name, worksheet_name, cell_col_row='A1'):
        """
        Update a cell in a Google Sheet with new data.

        Args:
            data (str): The data to be written to the cell.
            sheet_name (str): The name of the Google Sheet.
            worksheet_name (str): The name of the worksheet within the Google Sheet.
            cell_col_row (str, optional): The cell address (e.g., 'A1'). Defaults to 'A1'.
        """
        sh = self.get_sheet(sheet_name, worksheet_name)
        sh.update(cell_col_row, data)
        print(f"Data written to '{sheet_name}' - '{worksheet_name}' - '{cell_col_row}'")

    def update_cols(self, data, sheet_name, worksheet_name):
        """
        Update columns in a Google Sheet with data from a DataFrame.

        Args:
            data (pd.DataFrame): The DataFrame containing the data to be written.
            sheet_name (str): The name of the Google Sheet.
            worksheet_name (str): The name of the worksheet within the Google Sheet.

        Raises:
            ValueError: If the columns in the DataFrame do not match the columns in the worksheet.
        """
        sh = self.get_sheet(sheet_name, worksheet_name)
        existing_columns = sh.row_values(1)

        if not all(column in existing_columns for column in data.columns):
            raise ValueError("The columns in the DataFrame do not match the columns in the worksheet.")

        data_list = data.values.tolist()
        next_row = len(sh.col_values(1)) + 1
        sh.update(f'A{next_row}', data_list)
        print(f"Data appended to '{sheet_name}' - '{worksheet_name}'")

    def append_column(self, data, sheet_name, worksheet_name, column='A'):
        """
        Append data to the next empty row in a specified column.

        Args:
            data (str): The data to append.
            sheet_name (str): The name of the Google Sheet.
            worksheet_name (str): The name of the worksheet within the Google Sheet.
            column (str, optional): The column to append the data to. Defaults to 'A'.
        """
        sh = self.get_sheet(sheet_name, worksheet_name)
        next_row = len(sh.col_values(ord(column) - ord('A') + 1)) + 1
        sh.update(f'{column}{next_row}', [[data]])
        print(f"Data '{data}' appended to column '{column}' in '{sheet_name}' - '{worksheet_name}'")

    def clear_sheet(self, sheet_name, worksheet_name):
        """
        Clear the data in a Google Sheet worksheet.

        Args:
            sheet_name (str): The name of the Google Sheet.
            worksheet_name (str): The name of the worksheet within the Google Sheet.
        """
        sh = self.get_sheet(sheet_name, worksheet_name)
        sh.clear()
        print(f"Data cleared from '{sheet_name}' - '{worksheet_name}'")

    def get_sheet_as_df(self, sheet_name, worksheet_name):
        """
        Get the entire data from a Google Sheet worksheet as a pandas DataFrame.

        Args:
            sheet_name (str): The name of the Google Sheet.
            worksheet_name (str): The name of the worksheet within the Google Sheet.

        Returns:
            pd.DataFrame: The worksheet data as a DataFrame.
        """
        sh = self.get_sheet(sheet_name, worksheet_name)
        data = sh.get_all_values()
        headers = data.pop(0)
        df = pd.DataFrame(data, columns=headers)
        return df
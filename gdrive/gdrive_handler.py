import gspread
import pandas as pd

class GspreadHandler:
    def __init__(self, credentials_filepath='./gdrive/lunar-landing-389714-369d3f1b2a09.json'):
        self.credentials_filepath = credentials_filepath

    def get(self, 
            sheet_name,
            worksheet_name):
        """
        Writes data to a Google Sheet.

        Args:
            data (list): A list of lists representing the data to be written.
            sheet_name (str): The name of the Google Sheet.
            worksheet_name (str): The name of the worksheet within the Google Sheet.
            credentials_file (str, optional): The path to the JSON file containing Google Drive API credentials.

        Returns:
            None
        """

        gc = gspread.service_account(filename=self.credentials_filepath)

        sh = gc.open(sheet_name).worksheet(worksheet_name)

        print(sh.sheet1.get('A1'))
        return sh.sheet1.get('A1')
    

    def update_cell(self, 
                data:str, 
                sheet_name,
                worksheet_name,
                cell_col_row = 'A1'):

        gc = gspread.service_account(filename=self.credentials_filepath)
        sh = gc.open(sheet_name).worksheet(worksheet_name)

        # Write the new data to the worksheet
        sh.update(cell_col_row, data)

        print(f"Data written to '{sheet_name}' - '{worksheet_name}'")


    def update_cols(self, 
                    data, 
                    sheet_name, 
                    worksheet_name):
            """
            Updates a Google Sheet with data from a DataFrame. Checks if the column names exist in the sheet.

            Args:
                data (pd.DataFrame): The DataFrame containing the data to be written.
                sheet_name (str): The name of the Google Sheet.
                worksheet_name (str): The name of the worksheet within the Google Sheet.

            Raises:
                ValueError: If the columns in the DataFrame do not match the columns in the worksheet.
            """
            gc = gspread.service_account(filename=self.credentials_filepath)
            sh = gc.open(sheet_name).worksheet(worksheet_name)

            # Get the existing column names from the worksheet
            existing_columns = sh.row_values(1)

            # Check if the DataFrame columns exist in the worksheet
            if not all(column in existing_columns for column in data.columns):
                raise ValueError("The columns in the DataFrame do not match the columns in the worksheet.")

            # Convert DataFrame to a list of lists
            data_list = data.values.tolist()

            # Find the next empty row in the worksheet
            next_row = len(sh.col_values(1)) + 1

            # Append the data to the worksheet
            sh.update(f'A{next_row}', data_list)

            print(f"Data appended to '{sheet_name}' - '{worksheet_name}'")

    def append(self, 
               data, 
               sheet_name, 
               worksheet_name, 
               column='A'):
        """
        Appends data to the next empty row in a specified column.

        Args:
            data (str): The data to append.
            sheet_name (str): The name of the Google Sheet.
            worksheet_name (str): The name of the worksheet within the Google Sheet.
            column (str, optional): The column to append the data to. Defaults to 'A'.

        Returns:
            None
        """
        gc = gspread.service_account(filename=self.credentials_filepath)
        sh = gc.open(sheet_name).worksheet(worksheet_name)

        # Find the next empty row in the specified column
        next_row = len(sh.col_values(ord(column) - ord('A') + 1)) + 1

        # Append the data to the next row
        sh.update(f'{column}{next_row}', [[data]])

        print(f"Data '{data}' appended to column '{column}' in '{sheet_name}' - '{worksheet_name}'")


    def clear(self,
              sheet_name,
              worksheet_name):
        
        gc = gspread.service_account(filename=self.credentials_filepath)
        sh = gc.open(sheet_name).worksheet(worksheet_name)
        # Clear the existing data in the worksheet
        sh.clear()




if __name__ == '__main__':
    sample_data = [
    ["Name", "Age", "City"],
    ["John Doe", 32, "New York"],
    ["Jane Smith", 28, "London"],
    ["Bob Johnson", 45, "Tokyo"]
    ]
    write_to_google_sheet(sample_data, 'test sheet', 'Sheet1', 'lunar-landing-389714-369d3f1b2a09.json')
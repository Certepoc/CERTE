import pandas as pd
import sqlite3


def upload_data_to_db(excel_file_path, table_name):
    """
    Upload data from an Excel file to a specified SQLite table.

    :param excel_file_path: Path to the Excel file to upload.
    :param table_name: Name of the SQLite table to insert data into.
    :return: None
    """
    # Connect to the SQLite database
    conn = sqlite3.connect('C:\\Users\\10821476\\PycharmProjects\\pythonProject\\CERTE\\db.sqlite3')

    try:
        # Read the Excel file
        df = pd.read_excel(excel_file_path)

        # Insert data into the specified table
        df.to_sql(table_name, conn, if_exists='append', index=False)

    except Exception as e:
        print(f"Error uploading data: {e}")
    finally:
        conn.close()
import duckdb as duckdb
import pandas as pd
import os


class DuckDBManager:
    def __init__(self, db_dir: str = "database", db_name: str = "fit.db") -> None:
        """
        Initialize DuckDBManager.

        Args:
            db_dir (str): Directory where the database file is stored.
            db_name (str): Name of the database file.
        """
        self.db_dir = db_dir
        self.db_name = db_name
        self.db_path = os.path.join(db_dir, db_name)
        os.makedirs(db_dir, exist_ok=True)

    def _connect_to_database(self):
        """
        Helper method to connect to the DuckDB database.
        """
        return duckdb.connect(self.db_path)

    def _handle_error(self, message: str, error: Exception):
        """
        Helper method to handle errors.
        """
        print(f"Error: {message} - {error}")

    def setup_table(self, table_name: str, df: pd.DataFrame, schema: dict = None) -> None:
        """
        Setup a table in DuckDB.

        Args:
            table_name (str): Name of the table.
            df (pd.DataFrame): DataFrame to register as a table.
            schema (Optional[Dict[str, str]]): Dictionary specifying the column names and their types.

        Returns:
            None
        """
        if df.empty:
            raise ValueError("df must be a non-empty DataFrame")

        try:
            with self._connect_to_database() as con:
                con.register(table_name, df)

                if schema:
                    columns_with_types = ", ".join(
                        f"{col} {dtype}" for col, dtype in schema.items()
                    )
                    con.execute(
                        f"CREATE OR REPLACE TABLE {table_name} ({columns_with_types}) AS SELECT * FROM {table_name}"
                    )
                else:
                    con.execute(
                        f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM {table_name}"
                    )
        except Exception as e:
            self._handle_error(f"Error setting up DuckDB table: {e}")

    def get_data(self, table_name: str = None, query: str = None) -> pd.DataFrame:
        """
        Retrieve data from DuckDB.

        Args:
            table_name (str): Name of the table.
            query (str): SQL query to execute.

        Returns:
            pd.DataFrame: DataFrame containing the retrieved data.
        """
        try:
            with self._connect_to_database() as con:
                if query is None:
                    query = f"SELECT * FROM {table_name}"
                df = con.execute(query).fetchdf()
                return df
        except Exception as e:
            self._handle_error(f"Error fetching data from DuckDB: {e}")

    def execute_query(self, query: str) -> None:
        """
        Execute a SQL query in DuckDB.

        Args:
            query (str): SQL query to execute.

        Returns:
            None
        """
        try:
            with self._connect_to_database() as con:
                con.execute(query)
        except Exception as e:
            self._handle_error(f"Error executing DuckDB query: {e}")

    def append_to_table(self, df: pd.DataFrame, table_name: str) -> None:
        """
        Append data to a table in DuckDB.

        Args:
            df (pd.DataFrame): DataFrame containing data to append.
            table_name (str): Name of the table.

        Returns:
            None
        """
        try:
            with self._connect_to_database() as con:
                if df.empty:
                    print("Error: The DataFrame df is empty.")
                    return

                con.register("temp_table", df)
                con.execute(f"INSERT INTO {table_name} SELECT * FROM temp_table")
        except Exception as e:
            self._handle_error(f"Error appending to DuckDB table: {e}")

if __name__ == "__main__":

    # Create an instance of DuckDBManager
    db_manager = DuckDBManager()

    # db_manager.setup_table(table_name="exercises", df=exercises_df)

    # Fetch data from the table
    data = db_manager.get_data(table_name="exercises")
    print(data)

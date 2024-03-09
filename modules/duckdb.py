import duckdb as duckdb
import pandas as pd
import os
from typing import Optional, Dict


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

    def setup_table(self, table_name: str, df: pd.DataFrame, schema: Optional[Dict[str, str]] = None) -> None:
        """
        Setup a table in DuckDB.

        Args:
            table_name (str): Name of the table.
            df (pd.DataFrame): DataFrame to register as a table.
            schema (Optional[Dict[str, str]]): Dictionary specifying the column names and their types.

        Returns:
            None
        """
        if not isinstance(table_name, str) or not table_name:
            raise ValueError("table_name must be a non-empty string")

        if not isinstance(df, pd.DataFrame) or df.empty:
            raise ValueError("df must be a non-empty DataFrame")

        if schema is not None:
            if not isinstance(schema, dict) or not schema:
                raise ValueError("schema must be a non-empty dictionary")

        try:
            with duckdb.connect(self.db_path) as con:
                if df is not None:
                    con.register(table_name, df)

                    if schema is not None:
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
            print(f"Error setting up DuckDB table: {e}")

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
            with duckdb.connect(self.db_path) as con:
                if query is None:
                    query = f"SELECT * FROM {table_name}"
                df = con.execute(query).fetchdf()
                return df
        except Exception as e:
            print(f"Error fetching data from DuckDB: {e}")

    def execute_query(self, query: str) -> None:
        """
        Execute a SQL query in DuckDB.

        Args:
            query (str): SQL query to execute.

        Returns:
            None
        """
        try:
            with duckdb.connect(self.db_path) as con:
                con.execute(query)
        except Exception as e:
            print(f"Error executing DuckDB query: {e}")

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
            with duckdb.connect(self.db_path) as con:
                if df is not None and not df.empty:
                    con.register("temp_table", df)
                    con.execute(f"INSERT INTO {table_name} SELECT * FROM temp_table")
                else:
                    print("Error: The DataFrame df is empty or None.")
        except Exception as e:
            print(f"Error appending to DuckDB table: {e}")


if __name__ == "__main__":

    # Create an instance of DuckDBManager
    db_manager = DuckDBManager()

    # db_manager.setup_table(table_name="exercises", df=exercises_df)

    # Fetch data from the table
    data = db_manager.get_data(table_name="exercises")
    print(data)

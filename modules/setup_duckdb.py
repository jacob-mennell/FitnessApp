import duckdb as duckdb
import pandas as pd
import os
import streamlit as st
import sys


class DuckDBManager:
    def __init__(self, db_dir="database", db_name="fit.db"):
        self.db_dir = db_dir
        self.db_name = db_name
        self.db_path = os.path.join(db_dir, db_name)
        os.makedirs(db_dir, exist_ok=True)

    def setup_table(self, table_name: str, df: pd.DataFrame, schema=None):
        try:
            with duckdb.connect(self.db_path) as con:
                if df is not None:
                    con.register(table_name, df)

                    # Create the table with the defined schema if provided
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

                    print(f"Table {table_name} has been successfully set up in DuckDB.")
                else:
                    print("Error: The DataFrame df is empty.")
        except Exception as e:
            print(f"Error setting up DuckDB table: {e}")

    def get_data(self, table_name: str, query=None):
        try:
            with duckdb.connect(self.db_path) as con:
                if query is None:
                    query = f"SELECT * FROM {table_name}"
                df = con.execute(query).fetchdf()
                return df
        except Exception as e:
            print(f"Error fetching data from DuckDB: {e}")

    def append_to_table(self, df: pd.DataFrame, table_name: str):
        try:
            with duckdb.connect(self.db_path) as con:
                if df is not None and not df.empty:
                    con.register("temp_table", df)
                    con.execute(f"INSERT INTO {table_name} SELECT * FROM temp_table")
                    print(
                        f"Data has been successfully appended to the {table_name} table in DuckDB."
                    )
                else:
                    print("Error: The DataFrame df is empty or None.")
        except Exception as e:
            print(f"Error appending to DuckDB table: {e}")


if __name__ == "__main__":
    # Create an instance of DuckDBManager
    db_manager = DuckDBManager()

    db_manager.setup_table(table_name="historic_exercises", df=df)

    # Fetch data from the table
    data = db_manager.get_data(table_name="historic_exercises")
    print(data)

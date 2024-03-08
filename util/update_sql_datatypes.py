from modules.duckdb import DuckDBManager


db_manager = DuckDBManager()

table_name = "historic_exercises"

query = f"""
    CREATE OR REPLACE TABLE {table_name} AS
    SELECT
        CAST("Day" AS DATE) AS "Day",
        CAST("Exercise" AS VARCHAR) AS "Exercise",
        CAST("Weight" AS DECIMAL) AS "Weight",
        CAST("Reps" AS INTEGER) AS "Reps",
        CAST("Sets" AS INTEGER) AS "Sets",
        CAST("Notes" AS VARCHAR) AS "Notes",
        CAST("User" AS VARCHAR) AS "User"
    FROM {table_name}
"""

# execute_query
db_manager.execute_query(query=query)

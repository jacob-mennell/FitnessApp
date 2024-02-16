import duckdb


def check_table_existence(database_path, table_name):
    con = None
    try:
        # Connect to the DuckDB database
        con = duckdb.connect(database_path)

        # Check if the table exists
        query = f"SELECT 1 FROM information_schema.tables WHERE table_name = {repr(table_name)} LIMIT 1"
        result = con.execute(query).fetchall()

        if result:
            print(f"Table '{table_name}' exists in the database.")
        else:
            print(f"Table '{table_name}' does not exist in the database.")
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        # Close the connection if it's not None
        if con is not None:
            con.close()


def list_tables(database_path):
    con = None
    try:
        # Connect to the DuckDB database
        con = duckdb.connect(database_path)

        # Query to list all tables
        query = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'main'"
        result = con.execute(query).fetchdf()

        if not result.empty:
            print("Tables in the database:")
            for table in result["table_name"]:
                print(table)
        else:
            print("No tables found in the database.")
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        # Close the connection if it's not None
        if con is not None:
            con.close()


# Specify the database path and table name
database_path = "test.db"
table_name = "historic_exercises"

# Call the function to check table existence
# check_table_existence(database_path, table_name)

# Comment out the function to list tables
list_tables(database_path)

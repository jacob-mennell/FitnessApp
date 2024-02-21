import pytest
import duckdb


def check_table_existence(database_path, table_name):
    con = duckdb.connect(database_path)
    query = f"SELECT 1 FROM information_schema.tables WHERE table_name = {repr(table_name)} LIMIT 1"
    result = con.execute(query).fetchall()
    con.close()
    return bool(result)


def test_check_table_existence():
    database_path = "database/fit.db"
    table_name = "historic_exercises"
    assert check_table_existence(database_path, table_name) == True


def list_tables(database_path):
    con = duckdb.connect(database_path)
    query = (
        "SELECT table_name FROM information_schema.tables WHERE table_schema = 'main'"
    )
    result = con.execute(query).fetchdf()
    con.close()
    return result["table_name"].tolist()


def test_list_tables():
    database_path = "database/fit.db"
    expected_tables = ["historic_exercises"]
    assert list_tables(database_path) == expected_tables

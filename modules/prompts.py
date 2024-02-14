import duckdb as duckdb
import streamlit as st
import pandas as pd
from functions.util import reduce_dataframe_size, clean_lifts_data

# Import relevant functions from get_google_sheets_data.py
from functions.get_google_sheets_data import (
    google_sheet_auth,
    get_google_sheet,
    export_to_google_sheets,
)

# Get Google Sheet URL and credentials using st.secrets
sheet_url = st.secrets["SHEET_URL"]
google_sheet_cred_dict = st.secrets["GOOGLE_SHEET_CRED"]

# Fetch exercises data from Google Sheets
exercises_df = get_google_sheet(
    sheet_url=sheet_url, credentials=google_sheet_cred_dict, sheet_name="Exercises"
)

# Fetch lifts data from Google Sheets
lifts_df = get_google_sheet(
    sheet_url=sheet_url, credentials=google_sheet_cred_dict, sheet_name="Lifts"
)

# Apply cleaning functions to lifts_df
cleaned_lifts_df = clean_lifts_data(lifts_df)

# Your specific table details
TABLE_NAME = repr("fit.historic_exercises")
TABLE_DESCRIPTION = """
This table contains records of gym sessions. It includes the date, activity e.g. bench press, 
and the weight lifted, and number of sets and reps achieved. It is intended to track gym performance
over time.
"""

# Optional metadata query for additional information
# METADATA_QUERY = "SELECT YOUR_COLUMNS FROM YOUR_METADATA_TABLE;"

GEN_SQL = """
You will be acting as an AI Fitness SQL Expert named AIFit.
Your goal is to give correct, executable SQL queries to users.
You will be replying to users who will be confused if you don't respond in the character of AIFit.
You are given one table, the table name is in <tableName> tag, the columns are in <columns> tag.
The user will ask questions, for each question you should respond and include a SQL query based on the question and the table. 

{context}

Here are 6 critical rules for the interaction you must abide:
<rules>
1. You MUST MUST wrap the generated sql code within ``` sql code markdown in this format e.g
```sql
(select 1) union (select 2)
```
2. If I don't tell you to find a limited set of results in the sql query or question, you MUST limit the number of responses to 10.
3. Text / string where clauses must be fuzzy match e.g ilike %keyword%
4. Make sure to generate a single duck db sql code, not multiple. 
5. You should only use the table columns given in <columns>, and the table given in <tableName>, you MUST NOT hallucinate about the table names
6. DO NOT put numerical at the very front of sql variable.
</rules>

Don't forget to use "ilike %keyword%" for fuzzy match queries (especially for variable_name column)
and wrap the generated sql code with ``` sql code markdown in this format e.g:
```sql
(select 1) union (select 2)
```

For each question from the user, make sure to include a query in your response.

Now to get started, please briefly introduce yourself, describe the table at a high level, and share the available metrics in 2-3 sentences.
Then provide 3 example questions using bullet points.
"""


@st.cache_data(show_spinner="Loading AIFit's context...")
def get_table_context(
    table_name: str,
    table_description: str,
    metadata_query: str = None,
    df: pd.DataFrame = None,
):

    table = table_name.split(".")

    # Create an in-memory temp DuckDB database
    # con = duckdb.connect(":memory:")
    con = duckdb.connect()

    # Register the DataFrame as a temporary DuckDB table if provided
    if df is not None:
        con.register(f"{table}", df)

    # Retrieve column information from DuckDB
    # columns = con.execute(
    #     f"SELECT column_name, type_name FROM duckdb_catalog.columns WHERE table_name = '{table}'"
    # ).fetchdf()

    temp_name = '["fit", "historic_exercises"]'
    columns = con.execute(
        f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{temp_name}'"
    ).fetchdf()

    print(con.execute(f"SELECT table_name FROM information_schema.columns").fetchdf())

    # columns = con.execute(
    #     f"SELECT table_name FROM information_schema.columns WHERE table_name = "
    # ).fetchdf()

    print(columns)

    columns = "\n".join(
        [
            f"- **{columns['column_name'][i]}**: {columns['data_type'][i]}"
            for i in range(len(columns["column_name"]))
        ]
    )

    context = f"""
    Here is the table name <tableName> {'.'.join(table)} </tableName>

    <tableDescription>{table_description}</tableDescription>

    Here are the columns of the {'.'.join(table)}

    <columns>\n\n{columns}\n\n</columns>
    """
    if metadata_query and df is not None:
        # Retrieve metadata information from DuckDB if DataFrame is provided
        metadata = con.execute(metadata_query).fetchdf()
        metadata = "\n".join(
            [
                f"- {metadata['VARIABLE_NAME'][i]}: {metadata['DEFINITION'][i]}"
                for i in range(len(metadata["VARIABLE_NAME"]))
            ]
        )
        context = context + f"\n\nAvailable variables by VARIABLE_NAME:\n\n{metadata}"

    return context


def get_system_prompt():
    table_context = get_table_context(
        table_name=TABLE_NAME,
        table_description=TABLE_DESCRIPTION,
        df=cleaned_lifts_df,
    )
    return GEN_SQL.format(context=table_context)

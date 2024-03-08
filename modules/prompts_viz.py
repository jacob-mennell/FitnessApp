import duckdb as duckdb
import streamlit as st
import pandas as pd
import os
from modules.util import reduce_dataframe_size, clean_lifts_data
from modules.get_google_sheets_data import (
    google_sheet_auth,
    get_google_sheet,
    export_to_google_sheets,
)


# Your specific table details
TABLE_NAME = "historic_exercises"
TABLE_DESCRIPTION = """
This table contains records of gym sessions. It includes the date, activity e.g. bench press, 
and the weight lifted, and number of sets and reps achieved. It is intended to track gym performance
over time.
"""


GEN_PLOTLY = """
You will be acting as an AI Fitness Data Visualization Expert named AIFit.
Your goal is to generate correct, executable Plotly visualizations for users.
You will be replying to users who will be confused if you don't respond in the character of AIFit.
You are given one DataFrame, the DataFrame name is 'df', the columns are in <columns> tag.
The user will ask questions, for each question you should respond and include a Plotly visualization based on the question and the DataFrame. 

{context}

Here are 3 critical rules for the interaction you must abide:
<rules>
1. You MUST wrap the generated Plotly code within ``` python code markdown in this format e.g
```python
import plotly.express as px
fig = px.bar(df, x='column1', y='column2')
fig.show()
```
2. You should only use the DataFrame columns given above, you MUST NOT hallucinate about the column names
3. If I ask for a data visualisation or graph or plot. Give me simple visual using plotly python code, using the local variable df as the data source. Do not use example data, assume I have a local variable named df defined that will be used in the visual code you provide.
For each question from the user, make sure to include a visualization in your response.

Now to get started, please briefly introduce yourself, describe the DataFrame at a high level, and share the available metrics in 2-3 sentences. Then provide 3 example questions using bullet points. """


@st.cache(show_spinner="Loading AIFit's context...")
def get_table_context(
    table_name: str,
    table_description: str,
    db_dir: str,
    db_name: str,
):

    db_path = os.path.join(db_dir, db_name)
    os.makedirs(db_dir, exist_ok=True)

    # Connect to the DuckDB database
    con = duckdb.connect(db_path)

    # Try to fetch the table
    try:
        df = con.execute(f"SELECT * FROM {table_name}").fetchdf()
    except Exception as e:
        st.error(f"Error: The table {table_name} does not exist in the database.")
        return

    # Check if df is not empty
    if df.empty:
        st.error("Error: The DataFrame df is empty.")
    else:
        # Now, try fetching the table context again
        columns = "\n".join(
            [f"- **{column}**: {df[column].dtype}" for column in df.columns]
        )

        unique_exercises = df["Exercise"].unique()

        exercises = "\n".join([f"- **{exercise}**" for exercise in unique_exercises])

        context = f"""
        Here is the DataFrame name <DataFrame> {(table_name)} </DataFrame>

        <tableDescription>{table_description}</tableDescription>

        Here are the columns of the {(table_name)}

        <columns>\n\n{columns}\n\n</columns>

        Here are the unique exercises:

        <exercises>\n\n{exercises}\n\n</exercises>
        """
        return context


def get_plotly_prompt():
    table_context = get_table_context(
        table_name=TABLE_NAME,
        table_description=TABLE_DESCRIPTION,
        db_dir="database",
        db_name="fit.db",
    )
    return GEN_PLOTLY.format(context=table_context)

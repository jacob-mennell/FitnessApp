from openai import OpenAI
import streamlit as st
from modules.prompts_sql import get_system_prompt
from modules.util import (
    reduce_dataframe_size,
    clean_lifts_data,
    check_password,
    execute_sql_query,
)
import duckdb as duckdb
import re
import os

DB_DIR = "database"
DB_NAME = "fit.db"


st.title("AI Fitness Advisor 🏋️‍♂️")

st.markdown(
    "Welcome to the AI Fitness Advisor! I am here to assist and provide insights into your fitness journey."
)
st.markdown(
    "My purpose is to analyze your gym data, offer recommendations, and answer questions related to your workouts."
)
st.markdown(
    "You can ask me about your progress, areas for improvement, personalized workout plans, and more."
)
st.markdown(
    "Feel free to explore your fitness data and inquire about any aspect of your training."
)
st.markdown("Here are three example questions to get you started:")
st.markdown("- Where am I progressing the best?")
st.markdown("- What exercises do I need to improve?")
st.markdown("- Can you suggest a workout routine based on my recent lifts?")

if check_password():
    # Initialize the chat messages history
    if "messages" not in st.session_state.keys():
        st.session_state.messages = [
            {"role": "assistant", "content": get_system_prompt()}
        ]

    # Prompt for user input and save
    if prompts := st.chat_input():
        st.session_state.messages.append({"role": "user", "content": prompts})

    # display the existing chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # If last message is not from assistant, we need to generate a new response
    if st.session_state.messages[-1]["role"] != "assistant":
        # Call LLM
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                r = OpenAI().chat.completions.create(
                    messages=[
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state.messages
                    ],
                    model="gpt-3.5-turbo",
                )
                response = r.choices[0].message.content
                st.write(response)

        message = {"role": "assistant", "content": response}

        # Use regular expression to search for a SQL query pattern in the 'response' string
        sql_match = re.search(r"```sql\n(.*)\n```", response, re.DOTALL)

        # Use regular expression to search for a SQL query pattern in the 'response' string
        python_match = re.search(r"```python\n(.*)\n```", response, re.DOTALL)

        # Check if a SQL query is found in the response
        if sql_match:
            # Extract the SQL
            sql = sql_match.group(1)
            st.write(sql)

            # Execute the SQL query using DuckDB connection and store the results
            message["results"] = execute_sql_query(
                sql=sql, db_name=DB_NAME, db_dir=DB_DIR
            )

            # Display the results
            if message["results"] is not None:
                st.dataframe(message["results"])

    # Append the assistant's message (including SQL results) to the chat messages
    st.session_state.messages.append(message)

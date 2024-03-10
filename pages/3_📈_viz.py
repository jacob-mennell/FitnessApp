from openai import OpenAI
import streamlit as st
from modules.prompts_viz import get_plotly_prompt
from modules.duckdb import DuckDBManager
from modules.util import reduce_dataframe_size, clean_lifts_data, check_password
import duckdb as duckdb
import re
import os

st.title("AI Fitness Data Visualization Expert 📈")

st.markdown(
    "Welcome to the AI Fitness Data Visualization Expert! I am here to assist and provide insights into your fitness journey through data visualizations."
)
st.markdown(
    "My purpose is to analyze your gym data, generate Plotly visualizations, and answer questions related to your workouts."
)
st.markdown(
    "You can ask me about your progress, areas for improvement, personalized workout plans, and more. I will respond with a relevant Plotly visualization."
)
st.markdown(
    "Feel free to explore your fitness data and inquire about any aspect of your training. I am here to turn your data into insights."
)
st.markdown("Here are three example questions to get you started:")
st.markdown("- Can you show me a bar chart of my BENCH PRESS progress over time?")
st.markdown("- Can you visualize the exercises where I need to improve?")

if check_password():
    # Initialize the chat messages history
    if "messages" not in st.session_state.keys():
        st.session_state.messages = [
            {"role": "assistant", "content": get_plotly_prompt()}
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
        python_match = re.search(r"```python\n(.*)\n```", response, re.DOTALL)

        # Execute the SQL query using DuckDB connection and store the results
        df = DuckDBManager().get_data(table_name="historic_exercises")

        # Prepare a dictionary to capture local variables after exec
        local_vars = {"df": df}
        global_vars = {}

        # List of Plotly-specific keywords
        plotly_keywords = ["plotly", "px", "go", "fig"]

        # Check for Python code
        if python_match:
            # Extract Python
            python_code = python_match.group(1)

            # Check if the Python code contains Plotly-specific keywords
            if any(keyword in python_code for keyword in plotly_keywords):

                # Execute Python
                exec(python_code, global_vars, local_vars)

                # Check if 'fig' variable (commonly used for Plotly figures) is in local variables
                if "fig" in local_vars:
                    # Display the figure in Streamlit
                    st.plotly_chart(local_vars["fig"])
            else:
                st.error(
                    "The provided code does not seem to be a Plotly visualization. Please provide valid Plotly code."
                )

        # Append the assistant's message (including SQL results) to the chat messages
        st.session_state.messages.append(message)

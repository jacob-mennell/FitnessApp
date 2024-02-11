import streamlit as st
import pandas as pd


def add_dfForm():
    """Sets keys to add pd dataframe to session state data"""
    row = pd.DataFrame(
        {
            "Day": [st.session_state.input_date],
            "Exercise": [st.session_state.input_exercise],
            "Weight": [st.session_state.input_weight],
            "Reps": [st.session_state.input_reps],
            "Sets": [st.session_state.input_sets],
            "Notes": [st.session_state.input_notes],
            "User": [st.session_state.input_name],
        }
    )
    st.session_state.data = pd.concat([st.session_state.data, row])


def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == st.secrets["PASSWORD"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.text_input(
            "Need Password to input data",
            type="password",
            on_change=password_entered,
            key="password",
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input(
            "Need Password to input data",
            type="password",
            on_change=password_entered,
            key="password",
        )
        st.error("😕 Password incorrect")
        return False
    else:
        # Password correct.
        return True


def clean_lifts_data(lifts_df):
    # Data cleaning operations
    lifts_df["Weight"] = lifts_df["Weight"].astype(float)
    lifts_df["Reps"] = lifts_df["Reps"].astype(str)
    lifts_df["Sets"] = lifts_df["Sets"].astype(int)
    lifts_df["Notes"] = lifts_df["Notes"].astype(str)
    lifts_df["Day"] = pd.to_datetime(lifts_df["Day"], format="%d/%m/%Y").dt.date
    return lifts_df


def reduce_dataframe_size(lifts_df):
    # Drop exact duplicates
    lifts_df.drop_duplicates(inplace=True)

    # Drop duplicates based on specified columns and keep the latest run
    lifts_df.sort_values(
        by=["Weight", "Reps", "Sets", "Exercise", "Day"],
        ascending=[False, False, False, True, False],
        inplace=True,
    )
    lifts_df.drop_duplicates(
        subset=["Weight", "Reps", "Sets", "Exercise"], keep="first", inplace=True
    )

    return lifts_df

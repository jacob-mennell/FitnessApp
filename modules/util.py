import streamlit as st
import pandas as pd
import plotly.express as px
from modules.get_google_sheets_data import get_google_sheet, export_to_google_sheets
from modules.duckdb import DuckDBManager
import hashlib
from typing import Optional, Union, Tuple, List
import os


def clean_lifts_data(lifts_df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans the lifts data.

    Parameters:
    lifts_df (pd.DataFrame): The DataFrame to clean.

    Returns:
    pd.DataFrame: The cleaned DataFrame.
    """

    try:
        # Data cleaning operations
        lifts_df = lifts_df.copy()
        columns_to_dtype = {
            "Weight": float,
            "Exercise": str,
            "Reps": str,
            "Sets": int,
            "Notes": str,
        }
        lifts_df = lifts_df.astype(columns_to_dtype)
        lifts_df["Day"] = pd.to_datetime(lifts_df["Day"], format="%d/%m/%Y").dt.date
    except Exception as e:
        print(f"Error in cleaning data: {e}")
        return None

    return lifts_df


def reduce_dataframe_size(lifts_df: pd.DataFrame) -> pd.DataFrame:
    """
    Reduces the size of the DataFrame by dropping duplicates.

    Parameters:
    lifts_df (pd.DataFrame): The DataFrame to reduce.

    Returns:
    pd.DataFrame: The reduced DataFrame.
    """
    if not isinstance(lifts_df, pd.DataFrame):
        raise ValueError("Input should be a pandas DataFrame")

    try:
        # Drop exact duplicates
        lifts_df = lifts_df.drop_duplicates()

        # Drop duplicates based on specified columns and keep the latest run
        lifts_df = lifts_df.sort_values(
            by=["Weight", "Reps", "Sets", "Exercise", "Day"],
            ascending=[False, False, False, True, False],
        )
        lifts_df = lifts_df.drop_duplicates(
            subset=["Weight", "Reps", "Sets", "Exercise"], keep="first"
        )
    except Exception as e:
        print(f"Error in reducing DataFrame size: {e}")
        return None

    return lifts_df


def add_df_to_session_state() -> None:
    """Adds a pandas DataFrame to the session state data."""
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


def hash_password(password: str) -> str:
    """Hashes a password using SHA256.

    Args:
        password: The password to hash.

    Returns:
        The hashed password.
    """
    return hashlib.sha256(password.encode()).hexdigest()


def check_password() -> bool:
    """Checks whether a password entered by the user is correct.

    Returns:
        True if the password is correct, False otherwise.
    """

    def password_entered() -> None:
        """Checks whether a password entered by the user is correct."""
        try:
            entered_password = hashlib.sha256(
                st.session_state.get("password").encode()
            ).hexdigest()
            stored_password = st.secrets.get("PASSWORD")
            if entered_password == stored_password:
                st.session_state["password_correct"] = True
                del st.session_state["password"]  # don't store password
            else:
                st.session_state["password_correct"] = False
                st.error("😕 Password incorrect")
        except KeyError:
            st.error("Password not set in secrets")

    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    # First run, show input for password.
    st.text_input(
        "Need Password to input data",
        type="password",
        on_change=password_entered,
        key="password",
    )

    return st.session_state["password_correct"]


def load_sheets_data(
    sheet_url: str, google_sheet_cred_dict: dict
) -> Tuple[pd.DataFrame, pd.DataFrame, list]:
    """
    Load data from Google Sheets.

    Parameters:
    sheet_url (str): The URL of the Google Sheet.
    google_sheet_cred_dict (dict): The credentials for accessing the Google Sheet.

    Returns:
    Tuple[pd.DataFrame, pd.DataFrame, list]: A tuple containing two dataframes and a list of unique exercises.
    """
    try:
        # Load data from Google Sheets
        lifts_df = get_google_sheet(
            sheet_url=sheet_url, credentials=google_sheet_cred_dict, sheet_name="Lifts"
        )
        exercises_df = get_google_sheet(
            sheet_url=sheet_url,
            credentials=google_sheet_cred_dict,
            sheet_name="Exercises",
        )
        exercise_list_master = exercises_df["Exercise"].unique()

        return lifts_df, exercises_df, exercise_list_master
    except Exception as e:
        print(f"An error occurred: {e}")
        return pd.DataFrame(), pd.DataFrame(), []


def load_data(
    duckdb_manager: Optional[DuckDBManager] = None,
) -> Tuple[pd.DataFrame, pd.DataFrame, list]:
    """
        Load data using the DuckDB manager.

        Parameters:
        duckdb_manager (DuckDBManager, optional): The DuckDB manager. If None, a new DuckDB manager is created.
    s
        Returns:
        Tuple[pd.DataFrame, pd.DataFrame, list]: A tuple containing two dataframes and a list of unique exercises.
    """
    try:
        if duckdb_manager is None:
            duckdb_manager = DuckDBManager()

        lifts_df = duckdb_manager.get_data(table_name="historic_exercises")
        exercises_df = duckdb_manager.get_data(table_name="exercises")

        exercise_list_master = (
            exercises_df["Exercise"].unique() if not exercises_df.empty else []
        )

        return lifts_df, exercises_df, exercise_list_master
    except Exception as e:
        print(f"An error occurred: {e}")
        return pd.DataFrame(), pd.DataFrame(), []


def load_data_to_duckdb(
    lifts_df: pd.DataFrame,
    exercises_df: pd.DataFrame,
    duckdb_manager: Optional[DuckDBManager] = None,
) -> None:
    """
    Load data to DuckDB using the DuckDB manager.

    Parameters:
    lifts_df (pd.DataFrame): The dataframe containing lift data.
    exercises_df (pd.DataFrame): The dataframe containing exercise data.
    duckdb_manager (DuckDBManager, optional): The DuckDB manager. If None, a new DuckDB manager is created.
    """
    try:
        if duckdb_manager is None:
            duckdb_manager = DuckDBManager()

        duckdb_manager.setup_table("historic_exercises", lifts_df)
        duckdb_manager.setup_table("exercises", exercises_df)
    except Exception as e:
        print(f"An error occurred: {e}")


def select_session(exercises_df: pd.DataFrame) -> str:
    """
    Select a session from the exercises dataframe.

    Parameters:
    exercises_df (pd.DataFrame): The dataframe containing exercise data.

    Returns:
    str: The selected session.
    """
    try:
        session_list = exercises_df["Day"].drop_duplicates().to_list()
        session_choice = st.selectbox("Select session:", session_list)
        return session_choice
    except Exception as e:
        print(f"An error occurred: {e}")
        return ""


def select_exercise(exercises_df: pd.DataFrame, session_choice: str) -> str:
    """
    Select an exercise from the exercises dataframe for a given session.

    Parameters:
    exercises_df (pd.DataFrame): The dataframe containing exercise data.
    session_choice (str): The selected session.

    Returns:
    str: The selected exercise.
    """
    try:
        exercises_df = exercises_df.loc[exercises_df["Day"] == session_choice]
        exercise_list = exercises_df["Exercise"].drop_duplicates().to_list()
        make_choice = st.selectbox("Select your Gym Exercise:", exercise_list)
        return make_choice
    except Exception as e:
        print(f"An error occurred: {e}")
        return ""


def select_user(lifts_df: pd.DataFrame) -> str:
    """
    Select a user from the lifts dataframe.

    Parameters:
    lifts_df (pd.DataFrame): The dataframe containing lift data.

    Returns:
    str: The selected user.
    """
    try:
        user_list = lifts_df["User"].drop_duplicates().to_list()
        user_choice = st.selectbox("Select lifter:", user_list)
        return user_choice
    except Exception as e:
        print(f"An error occurred: {e}")
        return ""


def add_misc_exercise(
    sheet_url: Optional[str] = None,
    google_sheet_cred_dict: Optional[dict] = None,
    duckdb: bool = True,
    sheets: bool = False,
    duckdb_manager: Optional[DuckDBManager] = None,
) -> None:
    """
    Add a miscellaneous exercise.

    Parameters:
    sheet_url (str, optional): The URL of the Google Sheet.
    google_sheet_cred_dict (dict, optional): The credentials for accessing the Google Sheet.
    duckdb (bool, optional): Whether to use DuckDB. Default is True.
    sheets (bool, optional): Whether to use Google Sheets. Default is False.
    duckdb_manager (DuckDBManager, optional): The DuckDB manager. If None, a new DuckDB manager is created.
    """
    try:
        session_choice = "MISC"
        new_exercise_misc = st.text_input("Add exercise into MISC day:", "INSERT HERE")
        data = pd.DataFrame({"Day": [session_choice], "Exercise": [new_exercise_misc]})

        if new_exercise_misc != "INSERT HERE":
            if sheets:
                export_to_google_sheets(
                    sheet_url=sheet_url,
                    df_new=data,
                    credentials=google_sheet_cred_dict,
                    sheet_name="Exercises",
                )
            elif duckdb:
                if duckdb_manager is None:
                    duckdb_manager = DuckDBManager()

                # Add data to DuckDB
                duckdb_manager.append_to_table(df=data, table_name="exercises")

        st.write("New exercise to be added:", new_exercise_misc)
    except Exception as e:
        print(f"An error occurred: {e}")


def create_form(exercise_list: List[str]) -> None:
    """
    Create a form with Streamlit.

    Parameters:
    exercise_list (List[str]): The list of exercises.
    """
    try:
        dfForm = st.form(key="dfForm")
        with dfForm:
            dfColumns = st.columns(7)
            with dfColumns[0]:
                st.date_input("Day", key="input_date")
            with dfColumns[1]:
                st.selectbox("Exercise", exercise_list, key="input_exercise")
            with dfColumns[2]:
                st.number_input(
                    "Weight",
                    key="input_weight",
                    min_value=1,
                    max_value=250,
                    value=100,
                    step=1,
                )
            with dfColumns[3]:
                st.number_input(
                    "Reps",
                    key="input_reps",
                    min_value=1,
                    max_value=20,
                    value=8,
                    step=1,
                    format="%d",
                )
            with dfColumns[4]:
                st.number_input(
                    "Sets",
                    key="input_sets",
                    min_value=1,
                    max_value=5,
                    value=3,
                    step=1,
                    format="%d",
                )
            with dfColumns[5]:
                st.text_input("Notes", key="input_notes")
            with dfColumns[6]:
                st.text_input("User", key="input_name", value="JM")

            st.form_submit_button(on_click=add_df_to_session_state)
    except Exception as e:
        print(f"An error occurred: {e}")


def record_sets(
    lifts_df: pd.DataFrame,
    exercises_df: pd.DataFrame,
    duckdb_manager: Optional[DuckDBManager] = None,
    sheets: bool = False,
    duckdb: bool = True,
    sheet_url: Optional[str] = None,
    google_sheet_cred_dict: Optional[dict] = None,
) -> None:
    """
    Record sets of exercises.

    Parameters:
    lifts_df (pd.DataFrame): The dataframe containing lift data.
    exercises_df (pd.DataFrame): The dataframe containing exercise data.
    duckdb_manager (DuckDBManager, optional): The DuckDB manager. If None, a new DuckDB manager is created.
    sheets (bool, optional): Whether to use Google Sheets. Default is False.
    duckdb (bool, optional): Whether to use DuckDB. Default is True.
    sheet_url (str, optional): The URL of the Google Sheet.
    google_sheet_cred_dict (dict, optional): The credentials for accessing the Google Sheet.
    """
    try:
        if not sheets and not duckdb:
            raise ValueError("At least one of 'sheets' or 'duckdb' must be True.")

        if sheets and (sheet_url is None or google_sheet_cred_dict is None):
            raise ValueError(
                "If 'sheets' is True, 'sheet_url' and 'google_sheet_cred_dict' cannot be None."
            )

        if duckdb and duckdb_manager is None:
            duckdb_manager = DuckDBManager()

        lifts_df = clean_lifts_data(lifts_df)
        session_choice = select_session(exercises_df)
        make_choice = select_exercise(exercises_df, session_choice)
        user_choice = select_user(lifts_df)

        if session_choice == "MISC":
            add_misc_exercise()

        if "data" not in st.session_state:
            data = pd.DataFrame(
                {
                    "Day": [],
                    "Exercise": [],
                    "Weight": [],
                    "Reps": [],
                    "Sets": [],
                    "Notes": [],
                    "User": [],
                }
            )
            st.session_state.data = data

        data = st.session_state.data

        # If make_choice is a string, put it in a list
        if isinstance(make_choice, str):
            make_choice = [make_choice]

        create_form(make_choice)

        if sheets:
            export_to_google_sheets(
                sheet_url=sheet_url,
                df_new=data,
                credentials=google_sheet_cred_dict,
                sheet_name="Lifts",
            )

        if duckdb:
            # Add data to DuckDB
            duckdb_manager.append_to_table(df=data, table_name="historic_exercises")
    except Exception as e:
        print(f"An error occurred: {e}")


def performance_tracking(lifts_df: pd.DataFrame, exercise_list_master: list) -> None:
    """
    Track the performance of exercises.

    Parameters:
    lifts_df (pd.DataFrame): The dataframe containing lift data.
    exercise_list_master (list): The list of exercises.
    """
    # Filter data for performance tracking
    selected_exercise = st.selectbox(
        "Select an exercise for performance tracking:",
        exercise_list_master,
    )
    selected_lifts = lifts_df[lifts_df["Exercise"] == selected_exercise]

    # Plotting the performance tracking chart
    fig = px.line(
        selected_lifts,
        x="Day",
        y="Weight",
        color="Reps",
        markers=True,
        hover_data=["Weight", "Notes", "User"],
        title=f"Performance Tracking: {selected_exercise}",
    )
    fig.update_traces(marker=dict(size=10))
    st.plotly_chart(fig, use_container_width=True)


def user_pb_comparison(lifts_df: pd.DataFrame, exercise_list_master: list) -> None:
    """
    Compare the personal bests of users.

    Parameters:
    lifts_df (pd.DataFrame): The dataframe containing lift data.
    exercise_list_master (list): The list of exercises.
    """
    # Filter data for user PB comparison
    selected_exercises = st.multiselect(
        "Select exercises for PB comparison:",
        exercise_list_master,
        default=["BENCH PRESS", "SQUAT", "DEADLIFT"],
    )
    selected_lifts = lifts_df[lifts_df["Exercise"].isin(selected_exercises)]

    # Sorting and dropping duplicates to get user's all-time PBs
    user_pbs = selected_lifts.sort_values(
        by=["User", "Exercise", "Weight", "Day"], ascending=[False, False, False, True]
    ).drop_duplicates(["User", "Exercise"])

    # Plotting the user PB comparison chart
    fig = px.bar(
        user_pbs,
        x="Exercise",
        y="Weight",
        hover_data=["Day", "Exercise", "Weight", "Reps", "Notes"],
        color="User",
        barmode="group",
        title="User PB Comparison - Hover for number of reps",
    )
    fig.update_yaxes(dtick=20)
    st.plotly_chart(fig, use_container_width=True)

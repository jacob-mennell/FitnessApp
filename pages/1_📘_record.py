import streamlit as st
import pandas as pd
import plotly.express as px
import pandas as pd
from functions.get_google_sheets_data import get_google_sheet, export_to_google_sheets

# from functions.app import add_dfForm, check_password

# format
st.set_page_config(layout="wide")


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
        if st.session_state.get("password") == st.secrets["PASSWORD"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    # First run, show input for password.
    st.text_input(
        "Need Password to input data",
        type="password",
        on_change=password_entered,
        key="password",
    )

    if not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.error("😕 Password incorrect")

    return st.session_state["password_correct"]


def load_data(sheet_url, google_sheet_cred_dict):
    # Load data from Google Sheets
    lifts_df = get_google_sheet(
        sheet_url=sheet_url, credentials=google_sheet_cred_dict, sheet_name="Lifts"
    )
    exercises_df = get_google_sheet(
        sheet_url=sheet_url, credentials=google_sheet_cred_dict, sheet_name="Exercises"
    )
    exercise_list_master = exercises_df["Exercise"].drop_duplicates().to_list()
    return lifts_df, exercises_df, exercise_list_master


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


def select_session(exercises_df):
    session_list = exercises_df["Day"].drop_duplicates().to_list()
    session_choice = st.selectbox("Select session:", session_list)
    return session_choice


def select_exercise(exercises_df, session_choice):
    exercises_df = exercises_df.loc[exercises_df["Day"] == session_choice]
    exercise_list = exercises_df["Exercise"].drop_duplicates().to_list()
    make_choice = st.selectbox("Select your Gym Exercise:", exercise_list)
    return make_choice


def select_user(lifts_df):
    user_list = lifts_df["User"].drop_duplicates().to_list()
    user_choice = st.selectbox("Select lifter:", user_list)
    return user_choice


def add_misc_exercise(sheet_url, google_sheet_cred_dict):
    session_choice = "MISC"
    new_exercise_misc = st.text_input("Add exercise into MISC day:", "INSERT HERE")
    data = pd.DataFrame({"Day": [session_choice], "Exercise": [new_exercise_misc]})
    if new_exercise_misc != "INSERT HERE":
        export_to_google_sheets(
            sheet_url=sheet_url,
            df_new=data,
            credentials=google_sheet_cred_dict,
            sheet_name="Exercises",
        )
    st.write("New exercise to be added:", new_exercise_misc)


def create_form(exercise_list):
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
                "Reps", key="input_reps", min_value=1, max_value=20, value=8, step=1
            )
        with dfColumns[4]:
            st.number_input(
                "Sets", key="input_sets", min_value=1, max_value=5, value=3, step=1
            )
        with dfColumns[5]:
            st.text_input("Notes", key="input_notes")
        with dfColumns[6]:
            st.text_input("User", key="input_name", value="JM")

        st.form_submit_button(on_click=add_dfForm)


def record_sets(lifts_df, exercises_df, sheet_url, google_sheet_cred_dict):
    lifts_df = clean_lifts_data(lifts_df)
    session_choice = select_session(exercises_df)
    make_choice = select_exercise(exercises_df, session_choice)
    user_choice = select_user(lifts_df)

    if session_choice == "MISC":
        add_misc_exercise(sheet_url, google_sheet_cred_dict)

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
    create_form(make_choice)

    export_to_google_sheets(
        sheet_url=sheet_url,
        df_new=data,
        credentials=google_sheet_cred_dict,
        sheet_name="Lifts",
    )


def performance_tracking(lifts_df, exercises_df):
    # Filter data for performance tracking
    selected_exercise = st.selectbox(
        "Select an exercise for performance tracking:",
        exercises_df["Exercise"].unique(),
    )
    selected_lifts = lifts_df[lifts_df["Exercise"] == selected_exercise]

    # Plotting the performance tracking chart
    fig = px.line(
        selected_lifts,
        x="Day",
        y="Weight",
        color="Reps",
        markers=True,
        hover_data=["Weight", "Notes"],
        title=f"Performance Tracking: {selected_exercise}",
    )
    fig.update_traces(marker=dict(size=10))
    st.plotly_chart(fig, use_container_width=True)


def user_pb_comparison(lifts_df, exercise_list_master):
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


def main():
    # using st.secrets
    sheet_url = st.secrets["SHEET_URL"]
    google_sheet_cred_dict = st.secrets["GOOGLE_SHEET_CRED"]

    # set streamlit app headers
    st.header("Gym Performance Tracker")
    st.write("Input user gym performance and visualize historic performance.")

    # programme background
    st.write(
        "Rationale: Programme consists of a strong foundation of compound lifts with"
        " a smaller amount of isolated exercises with added "
        "drop sets to increase overall volume. "
    )

    st.write(
        "Stick to one number of reps on each exercise and try to reduce "
        "the RPE to at least 5-7 before increasing load."
    )

    # Load data
    lifts_df, exercises_df, exercise_list_master = load_data(
        sheet_url, google_sheet_cred_dict
    )

    # Record sets
    st.subheader("Record Sets")

    if check_password():
        record_sets(lifts_df, exercises_df, sheet_url, google_sheet_cred_dict)

    # Display fetched data and exercise list
    st.subheader("Performance Tracking")
    performance_tracking(lifts_df, exercises_df)

    # User PB Comparison
    st.subheader("User PB Comparison")
    user_pb_comparison(lifts_df, exercise_list_master)


if __name__ == "__main__":
    main()

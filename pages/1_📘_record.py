import streamlit as st
import pandas as pd
from modules.get_google_sheets_data import get_google_sheet, export_to_google_sheets
from modules.util import (
    clean_lifts_data,
    reduce_dataframe_size,
    add_dfForm,
    check_password,
    load_data,
    select_session,
    select_exercise,
    select_user,
    add_misc_exercise,
    create_form,
    record_sets,
    performance_tracking,
    user_pb_comparison,
)


# format
st.set_page_config(layout="wide")


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
    lifts_df, exercise_list_master = load_data()

    # Record sets
    st.subheader("Record Sets")

    if check_password():
        record_sets(lifts_df, exercise_list_master, sheet_url, google_sheet_cred_dict)

    # Display fetched data and exercise list
    st.subheader("Performance Tracking")
    performance_tracking(lifts_df, exercise_list_master)

    # User PB Comparison
    st.subheader("User PB Comparison")
    user_pb_comparison(lifts_df, exercise_list_master)


if __name__ == "__main__":
    main()

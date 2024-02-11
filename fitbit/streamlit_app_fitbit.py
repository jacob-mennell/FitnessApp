import numpy as np
import altair as alt
import pandas as pd
import streamlit as st
import os
from functions.get_google_sheets_data import get_google_sheet
from fitbit.get_fitbit_data import FitbitAnalysis
from fitbit.gather_keys_oauth2 import OAuth2Server
import datetime
import json
import ast

# get credentials for api and google sheet
# with open('cred.json') as data_file:
#     data = json.load(data_file)

# using st.secrets
client_id = st.secrets["CLIENT_ID"]
client_secret = st.secrets["CLIENT_SECRET"]
sheet_url = st.secrets["SHEET_URL"]
google_sheet_cred_dict = st.secrets["GOOGLE_SHEET_CRED"]

############################## streamlit app #############################

# set streamlit app headers
st.header("Fitness Monitoring App")
st.write("App looks at Gym Performance and Fitbit Activity over user defined period")
# user date input
today = datetime.date.today()
tomorrow = today + datetime.timedelta(days=1)
start_date = st.sidebar.date_input("Start date", (today - datetime.timedelta(days=60)))
end_date = st.sidebar.date_input("End date", tomorrow)
if start_date < end_date:
    st.success("Start date: `%s`\n\nEnd date:`%s`" % (start_date, end_date))
else:
    st.error("Error: End date must fall after start date.")

################### historical lifts from google sheets ##################

# set headers
st.subheader("Gym Strength Data")
st.write("Gym History Table")

# get data using gspread
lifts_df = get_google_sheet(
    sheet_url=sheet_url, credentials=google_sheet_cred_dict, sheet_name="Lifts"
)
pb_df = get_google_sheet(
    sheet_url=sheet_url, credentials=google_sheet_cred_dict, sheet_name="PB"
)

# minor cleaning
lifts_df["Weight"] = lifts_df["Weight"].astype(float)
lifts_df["Reps"] = lifts_df["Reps"].astype(str)
lifts_df["Sets"] = lifts_df["Sets"].astype(int)
lifts_df["Notes"] = lifts_df["Notes"].astype(str)
lifts_df["Day"] = pd.to_datetime(lifts_df["Day"], format="%d/%m/%Y").dt.date

# add filter for exercise
# exercise_list_master = lifts_df['Exercise'].drop_duplicates()
make_choice = st.sidebar.selectbox(
    "Select your Gym Exercise:", ["BENCH PRESS", "SQUAT", "DEADLIFT"]
)
st.write("You selected:", make_choice)
lifts_filt_df = lifts_df.loc[lifts_df["Exercise"] == make_choice]
lifts_filt_df = lifts_filt_df.loc[lifts_filt_df["Day"] >= start_date]
lifts_filt_df = lifts_filt_df.loc[lifts_filt_df["Day"] <= end_date]

# create and write graph
c = (
    alt.Chart(lifts_filt_df)
    .mark_line(point=alt.OverlayMarkDef(color="white"))
    .encode(x="Day", y="Weight", color="Reps")
    .properties(width=600, height=300)
    .configure_point(size=150)
)
st.write(c)

# Looking at PBs
st.write("Gym PBs")
pb_df = lifts_df[lifts_df["Exercise"].isin(["BENCH PRESS", "SQUAT", "DEADLIFT"])]
pb_df["Weight"] = pb_df["Weight"].astype(float)
pb_df = pb_df.sort_values(
    by=["Exercise", "Weight", "Day"], ascending=[False, False, True]
).drop_duplicates(["Exercise"])

# formatting for graph
pb_df["Reps"] = pb_df["Reps"].astype(str)
fig = px.bar(
    pb_df,
    x="Exercise",
    y="Weight",
    hover_data=["Day", "Exercise", "Weight", "Reps"],
    color="Reps",
    barmode="group",
    title="All Time PB - Varying Reps ",
)
st.write(fig)

############################### fitbit data ##############################

# set header
st.subheader("General Activity Data")

### code for FitBit API Analysis class ###
# fitinst = FitbitAnalysis(client_id, client_secret)
# activity_df = fitinst.get_x_days_activity(30)
# sleep_df = fitinst.get_x_days_sleep_agg(30)

# read from pkl file as API not working in streamlit currently
activity_df = pd.read_pickle("activity.pkl")
activity_list = activity_df["Name"].drop_duplicates().to_list()

# filter activities
activity_choice = st.sidebar.multiselect("Select your Activity", activity_list)
st.write("You selected:", activity_choice)

if not activity_choice:
    activity_filt_df = activity_df.copy()
else:
    activity_filt_df = activity_df.loc[activity_df["Name"].isin(activity_choice)]

# filter dates
activity_filt_df["Start_Date"] = pd.to_datetime(
    activity_filt_df["Start_Date"], format="%d/%m/%Y"
).dt.date
activity_filt_df = activity_filt_df.loc[activity_filt_df["Start_Date"] >= start_date]
activity_filt_df = activity_filt_df.loc[activity_filt_df["Start_Date"] <= end_date]

# create and write graph
st.write("Calories Burnt")
# c = alt.Chart(activity_filt_df).mark_bar().encode(
#      x='Start_Date', y='Calories').properties(width=600, height=300)
cal_fig = px.bar(
    activity_filt_df, x="Start_Date", y="Calories", color="Name", barmode="group"
)
st.write(cal_fig)

# create and write graph
st.write("Steps During Activity")
# c = alt.Chart(activity_filt_df).mark_bar().encode(
#      x='Start_Date', y='Steps').properties(width=600, height=300)
steps_fig = px.bar(
    activity_filt_df, x="Start_Date", y="Steps", color="Name", barmode="group"
)
st.write(steps_fig)

# sleep data

# read from pkl file as API not working in streamlit currently
sleep_df = pd.read_pickle("sleep.pkl")

# filter dates
sleep_df["dateOfSleep"] = pd.to_datetime(sleep_df["dateOfSleep"]).dt.date
sleep_filt_df = sleep_df.loc[sleep_df["dateOfSleep"] >= start_date]
sleep_filt_df = sleep_filt_df.loc[sleep_filt_df["dateOfSleep"] <= end_date]

# create and write graph
st.write("Sleep Data")
sleep_fig = px.line(sleep_filt_df, x="dateOfSleep", y="minutesAsleep")
st.write(sleep_fig)

import time
import numpy as np
import pandas as pd 
import plotly.express as px  
import streamlit as st  
from streamlit_pills import pills
import sqlite3 
# import datetime
import datetime


dashboard_pages = ["Workout", "Nutrition", "Personal Tracker", "Knowledge"]
popular_exercises = ["Bench Press", "Squat", "Deadlift"]


def connect_db():
    conn = sqlite3.connect("personal.sqlite3")
    return conn

def get_list_of_dates():
    # Get workout data
    conn = connect_db()
    workout_df = pd.read_sql_query("SELECT * FROM exercise", conn)
    
    # Get list of dates
    workout_df["exercise_date"] = pd.to_datetime(workout_df["exercise_date"]).dt.date
    list_of_dates = workout_df["exercise_date"].unique()
    
    return list_of_dates

def create_workout_dashboard(workout_config, date_picker):
    # Get workout data
    conn = connect_db()
    workout_df = pd.read_sql_query("SELECT * FROM exercise", conn)
    
    # Filter workouts based on exercise date
    workout_df["exercise_date"] = pd.to_datetime(workout_df["exercise_date"]).dt.date
    filtered_workouts_df = workout_df[workout_df["exercise_date"] == date_picker]
    
    # Get entry rows where exercise is in popular_exercises
    if workout_config[0] == "All":
        popular_workouts_df = filtered_workouts_df
    else:
        popular_workouts_df = filtered_workouts_df[filtered_workouts_df["exercise_name"].isin(workout_config)]

    return popular_workouts_df

def create_nutrition_dashboard():
    # Get nutrition data
    conn = connect_db()
    nutrition_df = pd.read_sql_query("SELECT * FROM food", conn)
    
    # Barchart of calories per day, grouped by date, sum of calories, and reset index so date is a column
    # Time is x axis, calories is y axis,
    calories_df = nutrition_df[["food_date", "calories"]].copy()
    calories_df["food_date"] = pd.to_datetime(calories_df["food_date"])
    # Remove the time from the date
    calories_df["food_date"] = calories_df["food_date"].dt.date
    
    calories_df = calories_df.groupby("food_date").sum().reset_index()
    calories_df.set_index("food_date", inplace=True)
    
    return nutrition_df, calories_df

def create_personal_tracker_dashboard():
    # Get personal tracker data
    conn = connect_db()
    personal_tracker_df = pd.read_sql_query("SELECT * FROM personal_tracker", conn)
    
    # Get date from record_date, and weight from weight
    # record_date as x axis, weight as y axis
    weight_tracker_df = personal_tracker_df[["record_date", "weight"]].copy()
    weight_tracker_df["record_date"] = pd.to_datetime(weight_tracker_df["record_date"])
    weight_tracker_df = weight_tracker_df.set_index("record_date")
    
    # Get body fat from body_fat
    body_fat_df = personal_tracker_df[["record_date", "body_fat"]].copy()
    body_fat_df["record_date"] = pd.to_datetime(body_fat_df["record_date"])
    body_fat_df = body_fat_df.set_index("record_date")
    
    return weight_tracker_df, body_fat_df

# 获取用户personal_tracker表中的数据
def get_personal_tracker_data():
    conn = connect_db()
    personal_tracker_df = pd.read_sql_query("SELECT * FROM personal_tracker", conn)
    return personal_tracker_df


def get_previous_after_date(date_picker):
    # Calculate previous and next dates based on list of dates
    list_of_dates = get_list_of_dates()
    # print(list_of_dates)
    print(date_picker)
  
    # Find the next date with a workout
    next_date = None
    for date in list_of_dates:
        if date > date_picker:
            next_date = date
            break
    
    # Find the previous date with a workout
    previous_date = None
    for date in reversed(list_of_dates):
        if date < date_picker:
            previous_date = date
            break
        
    print("Previous date", previous_date)
    print("Next date", next_date)
    
    return next_date, previous_date

def main():
    st.set_page_config(page_title="Dashboard", page_icon="📈", layout="wide")
    st.title("📈 Dashboard")
    
    # TODO Use st.data_editor to edit the database
    
    if "selected_date" not in st.session_state:
        st.session_state.selected_date = datetime.date.today()
        print("Today's date is", st.session_state.selected_date)
        
        st.session_state.next_workout_date = None
        st.session_state.previous_workout_date = None
        
        st.session_state.next_workout_date, st.session_state.previous_workout_date = get_previous_after_date(st.session_state.selected_date)
        
    
    job_filter = st.selectbox("Select the dashboard page", dashboard_pages)
    
    
        
        
    ###################################
    if job_filter == "Workout":
        # Three columns with middle one being wider
        col1, col2, col3 = st.columns([1, 4, 1], gap="small")
        
        with col1:
            previous_button = st.button("PREV", key="previous_button", disabled=st.session_state.previous_workout_date is None, use_container_width=True)
        
        with col2:
            date_picker = st.date_input("Select the date", value=st.session_state.selected_date, label_visibility="collapsed")
            
        with col3:
            next_button = st.button("NEXT", key="next_button", disabled=st.session_state.next_workout_date is None, use_container_width=True)
            
        
        if date_picker != st.session_state.selected_date:
            print("Picked a new date")
            st.session_state.selected_date = date_picker
            st.session_state.next_workout_date, st.session_state.previous_workout_date = get_previous_after_date(st.session_state.selected_date)
        
    
        if next_button:
            st.session_state.selected_date = st.session_state.next_workout_date
            st.session_state.next_workout_date, st.session_state.previous_workout_date = get_previous_after_date(st.session_state.selected_date)
            st.experimental_rerun()
            
    
        if previous_button:
            st.session_state.selected_date = st.session_state.previous_workout_date
            st.session_state.next_workout_date, st.session_state.previous_workout_date = get_previous_after_date(st.session_state.selected_date)
            st.experimental_rerun()

        selected = pills("Workout Type", ["All", "Bench Press", "Squat", "Deadlift"], ["👻","🍀", "🎈", "🌈"])
        
        pop_work_df = create_workout_dashboard([selected], st.session_state.selected_date)
        st.table(pop_work_df)
        # Create 
        
    if job_filter == "Nutrition":
        nut_df, cal_df = create_nutrition_dashboard()
        st.write("Nutrition")
        st.table(nut_df)
        
        # Barchart of calories per day
        st.write("Calories per day")
        st.bar_chart(cal_df)
        
    if job_filter == "Personal Tracker":
        weight_df, bf_df = create_personal_tracker_dashboard()
        st.write("Tracking Personal Weight Over Time")
        st.line_chart(weight_df)
        
        st.write("Tracking Personal Body Fat Over Time")
        st.line_chart(bf_df)

if __name__ == "__main__":
    main()
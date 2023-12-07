import time  # to simulate a real time data, time loop

import numpy as np
import pandas as pd 
import plotly.express as px  
import streamlit as st  
from streamlit_pills import pills
import sqlite3 

dashboard_pages = ["Workout", "Nutrition", "Personal Tracker", "Knowledge"]
popular_exercises = ["Bench Press", "Squat", "Deadlift"]


def connect_db():
    conn = sqlite3.connect("personal.sqlite3")
    return conn

def create_workout_dashboard(workout_config):
    # Get workout data
    conn = connect_db()
    workout_df = pd.read_sql_query("SELECT * FROM exercise", conn)
    
    # Get entry rows where exercise is in popular_exercises
    if workout_config[0] == "All":
        popular_workouts_df = workout_df
    else:
        popular_workouts_df = workout_df[workout_df["exercise_name"].isin(workout_config)]

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

def main():
    st.set_page_config(page_title="Dashboard", page_icon="📈", layout="wide")
    st.title("📈 Dashboard")
    
    job_filter = st.selectbox("Select the dashboard page", dashboard_pages)
    
    if job_filter == "Workout":
        selected = pills("Workout Type", ["All", "Bench Press", "Squat", "Deadlift"], ["👻","🍀", "🎈", "🌈"])
        pop_work_df = create_workout_dashboard([selected])
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
        st.write("Weight")
        st.line_chart(weight_df)
        
        st.write("Body Fat")
        st.line_chart(bf_df)
        
        
        
        
    
    
    
if __name__ == "__main__":
    main()
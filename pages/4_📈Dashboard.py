import time
import numpy as np
import pandas as pd 
import plotly.express as px  
import streamlit as st  
from streamlit_pills import pills
import sqlite3 
# import datetime
import datetime


dashboard_pages = ["Workout", "Nutrition", "Personal Tracker"]
popular_exercises = ["Bench Press", "Squat", "Deadlift"]


def connect_db(database_name):
    conn = sqlite3.connect(database_name)
    return conn

def get_list_of_dates(table_name="exercise"):
    # Get workout data
    conn = connect_db("./database/personal_db.sqlite3" if table_name == "exercise" else "./database/nutrition_db.sqlite3")
    workout_df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    
    # Get list of dates
    workout_df[f"{table_name}_date"] = pd.to_datetime(workout_df[f"{table_name}_date"]).dt.date
    list_of_dates = workout_df[f"{table_name}_date"].unique()
    
    return list_of_dates

def create_workout_dashboard(workout_config, date_picker):
    # Get workout data
    conn = connect_db("./database/personal_db.sqlite3")
    workout_df = pd.read_sql_query("SELECT * FROM exercise", conn)
    
    # Filter workouts based on exercise date
    workout_df["exercise_date"] = pd.to_datetime(workout_df["exercise_date"]).dt.date
    filtered_workouts_df = workout_df[workout_df["exercise_date"] == date_picker]
    
    filtered_workouts_df = filtered_workouts_df[["id", "exercise_name", "exercise_date", "exercise_type", "sets", "reps", "weight_kg", "notes"]].copy()
    
    # Get entry rows where exercise is in popular_exercises
    if workout_config[0] == "All":
        popular_workouts_df = filtered_workouts_df
    else:
        popular_workouts_df = filtered_workouts_df[filtered_workouts_df["exercise_name"].isin(workout_config)]

    return popular_workouts_df

def create_nutrition_dashboard(date_picker):
    # Get nutrition data
    conn = connect_db("./database/nutrition_db.sqlite3")
    nutrition_df = pd.read_sql_query("SELECT * FROM food", conn)
    
    # Filter nutrition based on food date
    nutrition_df["food_date"] = pd.to_datetime(nutrition_df["food_date"]).dt.date
    filtered_nutrition_df = nutrition_df[nutrition_df["food_date"] == date_picker]
    
    # Return only certain columns
    filtered_nutrition_df = filtered_nutrition_df[["id", "food_name", "food_date", "calories_kcal", "carbohydrates_g", "fat_g", "protein_g", "sodium_mg", "sugar_g", "notes"]].copy()
    
    calories_df = filtered_nutrition_df[["food_date", "calories_kcal"]].copy()    
    calories_df = calories_df.groupby("food_date").sum().reset_index()
    calories_df.set_index("food_date", inplace=True)
    
    conn.close()
    
    return filtered_nutrition_df, calories_df

def create_personal_tracker_dashboard():
    # Get personal tracker data
    conn = connect_db("./database/personal_db.sqlite3")
    personal_tracker_df = pd.read_sql_query("SELECT * FROM personal_tracker", conn)
    
    # Get date from record_date, and weight from weight
    # record_date as x axis, weight as y axis
    weight_tracker_df = personal_tracker_df[["record_date", "weight_kg"]].copy()
    weight_tracker_df["record_date"] = pd.to_datetime(weight_tracker_df["record_date"])
    weight_tracker_df = weight_tracker_df.set_index("record_date")
    
    # Get body fat from body_fat
    body_fat_df = personal_tracker_df[["record_date", "body_fat"]].copy()
    body_fat_df["record_date"] = pd.to_datetime(body_fat_df["record_date"])
    body_fat_df = body_fat_df.set_index("record_date")
    
    # Disconnect from database
    conn.close()
    
    return weight_tracker_df, body_fat_df

# 获取用户personal_tracker表中的数据
def get_personal_tracker_data():
    conn = connect_db("./database/personal_db.sqlite3")
    personal_tracker_df = pd.read_sql_query("SELECT * FROM personal_tracker", conn)
    return personal_tracker_df


def get_previous_after_date(date_picker, table_name):
    # Calculate previous and next dates based on list of dates
    list_of_dates = get_list_of_dates(table_name)
    
    # print("Table name", table_name)
    # print("List of dates", list_of_dates)
      
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
    st.subheader('Select the dashboard page')
    job_filter = st.selectbox("Select the dashboard page", dashboard_pages, label_visibility="collapsed")
    
    if "selected_date" not in st.session_state:
        st.session_state.selected_date = datetime.date.today()
        print("Today's date is", st.session_state.selected_date)
        
        st.session_state.next_workout_date = None
        st.session_state.previous_workout_date = None
    
    if job_filter == "Workout" or job_filter == "Nutrition":
        print("Job filter is", job_filter)
        st.session_state.next_workout_date, st.session_state.previous_workout_date = get_previous_after_date(st.session_state.selected_date, table_name="exercise" if job_filter == "Workout" else "food")
            
        st.write("Workout Date")
            
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
            st.session_state.next_workout_date, st.session_state.previous_workout_date = get_previous_after_date(st.session_state.selected_date, table_name="exercise" if job_filter == "Workout" else "food")
        
    
        if next_button:
            st.session_state.selected_date = st.session_state.next_workout_date
            st.session_state.next_workout_date, st.session_state.previous_workout_date = get_previous_after_date(st.session_state.selected_date, table_name="exercise" if job_filter == "Workout" else "food")
            st.rerun()
            
    
        if previous_button:
            st.session_state.selected_date = st.session_state.previous_workout_date
            st.session_state.next_workout_date, st.session_state.previous_workout_date = get_previous_after_date(st.session_state.selected_date, table_name="exercise" if job_filter == "Workout" else "food")
            st.rerun()

    
    ###################################
    if job_filter == "Workout":
        # Add new exercise
        st.write("Add New Exercise")
        
        col1, col2, col3, col4, col5, col6 = st.columns([1, 1, 1, 1, 1, 1], gap="small")
        
        with col1:
            exercise_name = st.text_input("Exercise Name")
        with col2:
            exercise_date = st.date_input("Exercise Date", value=st.session_state.selected_date,)
        with col3:
            exercise_type = st.selectbox("Exercise Type", ["Weightlifting", "Calisthenics", "Cardio"])
        with col4:
            sets = st.number_input("Sets", min_value=0, max_value=100, value=0)
        with col5:
            reps = st.number_input("Reps", min_value=0, max_value=100, value=0)
        with col6:
            weight_kg = st.number_input("Weight (kg)", min_value=0, max_value=1000, value=0)
        
        notes = st.text_area("Notes")
            
        add_button = st.button("Add", key="add_button")
        if add_button:
            conn = connect_db("./database/personal_db.sqlite3")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO exercise (exercise_name, exercise_date, exercise_type, sets, reps, weight_kg, notes) VALUES (?, ?, ?, ?, ?, ?, ?)", (exercise_name, exercise_date, exercise_type, sets, reps, weight_kg, notes))
            conn.commit()
            cursor.close()
            conn.close()
            st.success("Added!")
            st.balloons()
            
            
        selected = pills("Workout Type", ["All", "Bench Press", "Squat", "Deadlift"], ["👻","🍀", "🎈", "🌈"])
        
        pop_work_df = create_workout_dashboard([selected], st.session_state.selected_date)
                             
        edited_df = st.data_editor(
            pop_work_df,
            disabled=["id"],
            hide_index=False,
        )
        
        save_button = st.button("Save", key="save_button")
        if save_button:
            conn = connect_db("./database/personal_db.sqlite3")
            cursor = conn.cursor()
            for index, row in edited_df.iterrows():
                # cursor.execute("UPDATE exercise SET exercise_name = %s, exercise_date = %s, exercise_type = %s, sets = %s, reps = %s, weight_kg = %s, notes = %s WHERE id = %s", (row['exercise_name'], row['exercise_date'], row['exercise_type'], row['sets'], row['reps'], row['weight_kg'], row['notes'], row['id']))
                cursor.execute("UPDATE exercise SET exercise_name = ?, exercise_date = ?, exercise_type = ?, sets = ?, reps = ?, weight_kg = ?, notes = ? WHERE id = ?", (row['exercise_name'], row['exercise_date'], row['exercise_type'], row['sets'], row['reps'], row['weight_kg'], row['notes'], row['id']))

            conn.commit()
            cursor.close()
            conn.close()
            st.success("Saved!")
            st.balloons()
        
        # Create 
        
    if job_filter == "Nutrition":
        selected_2 = pills("Time", ["Daily", "Weekly", "Monthly"], ["👻","🍀", "🎈"])
        nut_df, cal_df = create_nutrition_dashboard(st.session_state.selected_date)
        
        st.write("Nutrition")

        st.write("Add New Exercise")
        
        col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([1, 1, 1, 1, 1, 1, 1, 1], gap="small")
        
        with col1:
            food_name = st.text_input("Food Name", key="food_name")
        with col2:
            food_date = st.date_input("Food date", value=st.session_state.selected_date, key="food_date")
        with col3:
            calories = st.number_input("Calories (Kcal)", key="calories")
        with col4:
            carbohydrates = st.number_input("Carbohydrates(g)", key="carbohydrates")
        with col5:
            fat = st.number_input("Fat(g)", key="fat")
        with col6:
            protein = st.number_input("Protein(g)", key="protein")
        with col7:
            sodium = st.number_input("Sodium(mg)", key="sodium")
        with col8:
            sugar = st.number_input("Sugar(g)", key="sugar")
        
        notes = st.text_area("Notes", key="food_notes")
    
        add_button = st.button("Add", key="add_button")
        if add_button:
            conn = connect_db("./database/nutrition_db.sqlite3")
            cursor = conn.cursor()
            # cursor.execute("INSERT INTO exercise (exercise_name, exercise_date, exercise_type, sets, reps, weight_kg, notes) VALUES (?, ?, ?, ?, ?, ?, ?)", (exercise_name, exercise_date, exercise_type, sets, reps, weight_kg, notes))
            cursor.execute("INSERT INTO food (food_name, food_date, calories_kcal, carbohydrates_g, fat_g, protein_g, sodium_mg, sugar_g, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?) ", (food_name, food_date, calories, carbohydrates, fat, protein, sodium, sugar, notes))
            conn.commit()
            cursor.close()
            conn.close()
            st.success("Added!")
            st.balloons() 
        
        edited_df = st.data_editor(
            nut_df,
            disabled=["id"],
            hide_index=True
        )

        save_button = st.button("Save", key="save_button")
        if save_button:
            conn = connect_db("./database/nutrition_db.sqlite3")
            cursor = conn.cursor()
            for index, row in edited_df.iterrows():
                # cursor.execute("UPDATE exercise SET exercise_name = %s, exercise_date = %s, exercise_type = %s, sets = %s, reps = %s, weight_kg = %s, notes = %s WHERE id = %s", (row['exercise_name'], row['exercise_date'], row['exercise_type'], row['sets'], row['reps'], row['weight_kg'], row['notes'], row['id']))
                cursor.execute("UPDATE exercise SET exercise_name = ?, exercise_date = ?, exercise_type = ?, sets = ?, reps = ?, weight_kg = ?, notes = ? WHERE id = ?", (row['exercise_name'], row['exercise_date'], row['exercise_type'], row['sets'], row['reps'], row['weight_kg'], row['notes'], row['id']))

            conn.commit()
            cursor.close()
            conn.close()
            st.success("Saved!")
            st.balloons()
        
        
        
        # Barchart of calories per day
        st.write("Calories per day")
        st.bar_chart(cal_df, y="calories_kcal")
        
    if job_filter == "Personal Tracker":
        weight_df, bf_df = create_personal_tracker_dashboard()
        st.write("Tracking Personal Weight Over Time")
        st.line_chart(weight_df, y="weight_kg")
        
        st.write("Tracking Personal Body Fat Over Time")
        st.line_chart(bf_df, y="body_fat")

if __name__ == "__main__":
    main()
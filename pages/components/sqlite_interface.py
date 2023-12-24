'''
Title: 
Author:
Description: Code to interact with the Workout SQLite3 database
'''

import os
import ast
from dotenv import load_dotenv
import pandas as pd
import numpy as np
import sqlite3
from langchain.utilities.sql_database import SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain
from langchain.llms.openai import OpenAI
from langchain.prompts import PromptTemplate
from io import StringIO

from pages.components.trainer_prompts import TrainerPrompts



# Load environment variables
load_dotenv()
os.environ["HUGGINGFACEHUB_API_TOKEN"] = os.getenv("HUGGINGFACEHUB_API_TOKEN")
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

def numpy_from_string(string):
    str_data = StringIO(string)
    df = pd.read_csv(str_data, sep="\s+", engine='python')
    
    return df


# 用LLM来获取数据库中的数据，吧问题转换成SQL语句
def question_to_sql(db, question):
    # TODO Set db connection open at start of the app instead of every time a question is asked
    # TODO Prompt some default questions
    # db = SQLDatabase.from_uri("sqlite:///personal.sqlite3")

    # Default 
    prompt = TrainerPrompts().default_sqldatabase_prompt()
    
    llm = OpenAI(model="gpt-3.5-turbo-instruct", temperature=0, max_tokens=1000)
    db_chain = SQLDatabaseChain(
        llm=llm, 
        database=db,
        prompt=prompt,
        verbose=False
    )
    print("Question: " + question)
    
    try:
        # Different additions to the question to get more fined tuned results
        if "graph" in question.lower():
            question = question + " in python dataframe format"
        
        response = db_chain.run(question)
        
        print("^" * 50)
        print("SQL Response:", response)
        print("^" * 50)
    
        workout_df = None
        if "graph" in question.lower():
            workout_df = numpy_from_string(response)
            response = "Here is the graph"
            
        return response, workout_df
    except Exception as e:
        print(str(e))
        formatted_error = "Sorry, I don't understand. Please try again."
        if "You exceeded your current quota" in str(e):
            formatted_error = "You have exceeded your OpenAPI quota. Please try again later."
        if "permission denied" in str(e).lower():
            formatted_error = "Baka, don't do that. You don't have permission to do that."
        return formatted_error, None

  
# 连上数据库
def connect_db(db_name="personal_db.sqlite3"):
    conn = sqlite3.connect(db_name)
    return conn
    
# 从数据库中获取所有的workout_routines id和name  
def get_workout_routines(db_name="personal_db.sqlite3"):
    conn = connect_db(db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT id, routine_name FROM exercise_routine")
    workout_routines = cursor.fetchall()
    conn.close()
    return workout_routines

# 用workout_routine id来获取所有的workout_exercises
def get_workout_routine_exercises(db_name="personal_db.sqlite3", workout_routine_id=0):
    conn = connect_db(db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT id, routine_plan FROM exercise_routine WHERE id = ?", (workout_routine_id,))
    workout_exercises = cursor.fetchall()
    conn.close()
    
    #Regular Pushups, 10 Reps\n2. Wide Pushups, 10 Reps\n3. Diamond Pushups, 10 Reps\n4. Explosive Pushups, 10 Reps\n5. Side-to-Side Pushups, 10 Reps\n6. Clapping Pushups, 10 Reps\n7. Archer Pushups, 10 Reps\n8. Open and Close Pushups, 10 Reps\n9. Typewriter Pushups\n10. Pushup + Shoulder Tap\nNotes: 3 or more sets.
    
    # Workout looks like this
    #Regular Pushups, 10 Reps\n2. Wide Pushups, 10 Reps\n3. Diamond Pushups, 10 Reps\n4. Explosive Pushups, 10 Reps\n5. Side-to-Side Pushups, 10 Reps\n6. Clapping Pushups, 10 Reps\n7. Archer Pushups, 10 Reps\n8. Open and Close Pushups, 10 Reps\n9. Typewriter Pushups\n10. Pushup + Shoulder Tap\nNotes: 3 or more sets.
    
    # Make it into a list string
    workout_exercises = workout_exercises[0][1].split("\\n")
    print(workout_exercises)
    
    workout_exercises = ("\n").join(workout_exercises)
    return workout_exercises
'''
Title: 
Author:
Description: Code to interact with the Workout SQLite3 database
'''

import os
import ast
from dotenv import load_dotenv
import pandas as pd
from langchain.utilities.sql_database import SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain
# from langchain.llms import OpenAI
from langchain.llms.openai import OpenAI



# Load environment variables
load_dotenv()
os.environ["HUGGINGFACEHUB_API_TOKEN"] = os.getenv("HUGGINGFACEHUB_API_TOKEN")
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

def numpy_from_string(string):
    # Create a numpy array from a string using large language model
    # TODO Use LLM to extract dataframe from string for more robustness
    
    # Extract [ to ] from string
    extracted = string[string.find("[")+1:string.find("]")]
    print(extracted)
    workout_data = ast.literal_eval(extracted)
    print(workout_data)
    workout_df = pd.DataFrame(workout_data, columns=["Date", "Weight"])
    return workout_df

def question_to_sql(question):
    # TODO Set db connection open at start of the app instead of every time a question is asked
    # TODO Prompt some default questions
    db = SQLDatabase.from_uri("sqlite:///personal_trainer.db")
    llm = OpenAI(temperature=0, max_tokens=1000)
    db_chain = SQLDatabaseChain(llm=llm, database=db, verbose=False)
    
    try:
        response = db_chain.run(question)
        
        workout_df = None
        if "graph" in question.lower():
            workout_df = numpy_from_string(response)
            
        print(response)

        return response, workout_df
    except Exception as e:
        return "SQL error, try again", None
    
    




    
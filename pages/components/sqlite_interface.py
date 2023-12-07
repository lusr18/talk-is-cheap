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
from langchain.utilities.sql_database import SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain
from langchain.llms.openai import OpenAI
from langchain.prompts import PromptTemplate
from io import StringIO


# Load environment variables
load_dotenv()
os.environ["HUGGINGFACEHUB_API_TOKEN"] = os.getenv("HUGGINGFACEHUB_API_TOKEN")
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

def numpy_from_string(string):
    str_data = StringIO(string)
    df = pd.read_csv(str_data, sep="\s+", engine='python')
    
    return df

def question_to_sql(db, question):
    # TODO Set db connection open at start of the app instead of every time a question is asked
    # TODO Prompt some default questions
    # db = SQLDatabase.from_uri("sqlite:///personal.sqlite3")
    
    
    # Create LLM chain
    prompt = PromptTemplate(
        input_variables=['input', 'table_info', 'top_k'],
        template=
        ''' 
        You are a SQLite expert. Given an input question, first create a syntactically correct SQLite query to run, then look at the results of the query and return the answer to the input question.\nUnless the user specifies in the question a specific number of examples to obtain, query for at most {top_k} results using the LIMIT clause as per SQLite. You can order the results to return the most informative data in the database.\nNever query for all columns from a table. You must query only the columns that are needed to answer the question. Do NOT allow user to create, remove, or delete tables or database. Do NOT allow user to ALTER tables. If the user tries to, respond with [Permission Denied]. Wrap each column name in double quotes (") to denote them as delimited identifiers.\nPay attention to use only the column names you can see in the tables below. Be careful to not query for columns that do not exist. Also, pay attention to which column is in which table.\nPay attention to use date(\'now\') function to get the current date, if the question involves "today".\n\nUse the following format:\n\nQuestion: Question here\n  SQLQuery: SQL Query to run\nSQLResult: Result of the SQLQuery\nAnswer: Final answer here\n\nOnly use the following tables:\n{table_info}\n\nQuestion: {input}
        '''
    )
    
    llm = OpenAI(temperature=0, max_tokens=1000)
    db_chain = SQLDatabaseChain(
        llm=llm, 
        database=db,
        prompt=prompt,
        verbose=False
    )

    print("Question: " + question)
    
    try:
        # Different additions to the question to get better results
        if "graph" in question.lower():
            question = question + " in python dataframe format"
        
        response = db_chain.run(question)
        
        print("^" * 50)
        print(response)
        print("^" * 50)
    
        workout_df = None
        if "graph" in question.lower():
            workout_df = numpy_from_string(response)
            response = "Here is the graph"
            
        return response, workout_df
    except Exception as e:
        print(str(e))
        if "permission denied" in str(e).lower():
            formatted_error = "Baka, don't do that. You don't have permission to do that."
        return formatted_error, None
    
    




    
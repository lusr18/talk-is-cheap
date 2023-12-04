'''
Title: 
Author:
Description: Code to interact with the snowflake database
'''

import os
from dotenv import load_dotenv
from langchain.utilities.sql_database import SQLDatabase
from langchain.llms import OpenAI
from snowflake.snowpark import Session

load_dotenv()
os.environ["SNOWFLAKE_ACCOUNT"] = os.getenv("SNOWFLAKE_ACCOUNT")
os.environ["SNOWFLAKE_USERNAME"] = os.getenv("SNOWFLAKE_USERNAME")
os.environ["SNOWFLAKE_PASSWORD"] = os.getenv("SNOWFLAKE_PASSWORD")
os.environ["SNOWFLAKE_DATABASE"] = os.getenv("SNOWFLAKE_DATABASE")
os.environ["SNOWFLAKE_SCHEMA"] = os.getenv("SNOWFLAKE_SCHEMA")
os.environ["SNOWFLAKE_WAREHOUSE"] = os.getenv("SNOWFLAKE_WAREHOUSE")
os.environ["SNOWFLAKE_ROLE"] = os.getenv("SNOWFLAKE_ROLE")

username = os.getenv("SNOWFLAKE_USERNAME")
password = os.getenv("SNOWFLAKE_PASSWORD")
account = os.getenv("SNOWFLAKE_ACCOUNT")
database = os.getenv("SNOWFLAKE_DATABASE")
schema = os.getenv("SNOWFLAKE_SCHEMA")
warehouse = os.getenv("SNOWFLAKE_WAREHOUSE")
role = os.getenv("SNOWFLAKE_ROLE")

def question_to_snowflake(question):
    snowflake_url = f"snowflake://{username}:{password}@{account}/{database}/{schema}?warehouse={warehouse}@role={role}"
    db = SQLDatabase.from_uri(snowflake_url, sample_rows_in_table_info=1, include_tables=["foods"])
    
    llm = OpenAI(temperature=0)    
    return "Snowflake response"
'''
Title:
Description: Use the AssistantAgent wrapper to create a nutrition assistant
'''

import os
import sqlite3
import requests
from dotenv import load_dotenv

# Langchain
from langchain.vectorstores import Milvus
from langchain.embeddings import OpenAIEmbeddings

# Custom
from .function import Function, Property
from .assistant import AIAssistant


load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
nut_api_key = os.getenv("NINJA_API_KEY")
milvus_host = os.getenv("MILVUS_HOST")
milvus_token = os.getenv("MILVUS_TOKEN")
    
class GetDBSchema(Function):
    def __init__(self):
        super().__init__(
            name="get_db_schema",
            description="Get the schema of the my personal database",
        )
    def function(self):
        # conn = sqlite3.connect('Chinook.sqlite')
        conn = sqlite3.connect('./database/nutrition_db.sqlite3')
        cursor = conn.cursor()
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table';")
        create_statements = cursor.fetchall()
        conn.close()
        return '\n\n'.join([statement[0] for statement in create_statements])
    
class RunSQLQuery(Function):
    def __init__(self):
        super().__init__(
            name="run_sql_query",
            description="Run a SQL query on my personal database",
            parameters=[
                Property(
                    name="query",
                    description="The SQL query to run",
                    type="string",
                    required=True,
                ),
            ]
        )
    def function(self, query):
        conn = sqlite3.connect('./database/nutrition_db.sqlite3')
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        conn.commit()
        conn.close()
        return '\n'.join([str(result) for result in results])
    
class GetNutritionInfo(Function):
    def __init__(self):
        super().__init__(
            name="get_nutrition_info",
            description="Get the nutrition information for a food",
            parameters=[
                Property(
                    name="food",
                    description="The food to get nutrition information for",
                    type="string",
                    required=True,
                ),
            ]
        )  
    def function(self, food):
        api_url = 'https://api.api-ninjas.com/v1/nutrition?query={}'.format(food)
        response = requests.get(api_url, timeout=100, headers={'X-Api-Key': nut_api_key})
        
        response_json = response.json()
        # Reformatting the data
        formatted_data = []
        for food_data in response_json:
            formatted_food_data = {
                "calories": food_data["calories"],
                "carbohydrates_g": food_data["carbohydrates_total_g"],
                "fats_g": food_data["fat_total_g"],  # Renamed key
                "protein_g": food_data["protein_g"],
                "sodium_mg": food_data["sodium_mg"],
                "sugar_g": food_data["sugar_g"]
            }
            formatted_data.append(formatted_food_data)

        return str(formatted_data)
  
class GetPersonBMI(Function):
    def __init__(self):
        super().__init__(
            name="get_bmi",
            description="Get the BMI of a person using their height and weight",
            parameters=[
                Property(
                    name="height",
                    description="The height of the person in meters",
                    type="number",
                    required=True,
                ),
                Property(
                    name="weight",
                    description="The weight of the person in kilograms",
                    type="number",
                    required=True,
                ),
            ]
        )
    def function(self, height, weight):
        bmi = weight / (height ** 2)
        return "The BMI of the person is {:.2f}".format(bmi)

def create_nutrition_agent() -> AIAssistant:
    """ Create a nutrition assistant agent """
    
    instruction = """You are a Nutrition experts. User asks you questions about the nutrition database.
    First obtain the schema of the database to check the tables and columns, then generate SQL queries to answer the questions.
    The user can also query nutrition information for a food.
    If the user asks for the BMI of a person, you can calculate it using the height and weight of the person. But first get the weight and height of the person from the database."""
    
    functions = [GetDBSchema(), RunSQLQuery(), GetNutritionInfo(), GetPersonBMI()]
    
    assistant = AIAssistant(
        instruction=instruction,
        model="gpt-3.5-turbo-1106",
        functions=functions,
        verbose=True,
        use_code_interpreter=True, 
        # use_retrieval=True, 
        use_third_party_retrieval="Milvus",
        auto_delete=True,
    )
    
    return assistant
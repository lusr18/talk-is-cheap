'''
Title:
Description: Use the AssistantAgent wrapper to create a workout assistant
'''

import os
import sqlite3
import requests
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi

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
collection_name = "TranscriptCollection"
    
class GetDBSchema(Function):
    def __init__(self):
        super().__init__(
            name="get_db_schema",
            description="Get the schema of the my personal database",
        )
    def function(self):
        # conn = sqlite3.connect('Chinook.sqlite')
        conn = sqlite3.connect('./database/personal_db.sqlite3')
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
        conn = sqlite3.connect('./database/personal_db.sqlite3')
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        conn.commit()
        conn.close()
        return '\n'.join([str(result) for result in results])
  
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
    
class GetPersonBMR(Function):
    def __init__(self):
        super().__init__(
            name="get_bmr",
            description="Basal Metabolic Rate (BMR) of a person using their weight, height, age, gender using the Mifflin-St Jeor equation",
            parameters = [
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
                Property(
                    name="age",
                    description="The age of the person in years",
                    type="number",
                    required=True,
                ),
                Property(
                    name="gender",
                    description="The gender of a person, male or female",
                    type="string",
                    required=True,
                ),
            ]
        ),
    def function(self, height, weight, age, gender):
        if gender.lower() == 'male':
            return (10 * weight) + (6.25 * height) - (5 * age) + 5
        else:  # 'female'
            return (10 * weight) + (6.25 * height) - (5 * age) - 161
        
class GetYoutubeTranscript(Function):
    def __init__(self):
        super().__init__(
            name="GetYoutubeTranscript",
            description="Get the transcript from a youtube video given the url",
            parameters=[
                Property(
                    name="url",
                    description="The link to the youtube video workout the user wants to follow",
                    type="string",
                    required=True,
                ),
            ]
        )
    def function(self, url):
        # Identify unique url id
        video_id = url.split("=")[1]
        if '&pp' in video_id:
            video_id = video_id.split("&pp")[0]
        # Acquire transcript from url with exception catch for empty transcript
        output = ""
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id,
                                                languages=['en'])
            for i in transcript:
                output = output + i["text"] + "\n"
        except:
            print("Transcript could not be fetched, skipping video.")
            return
        # Write transcript from received object to AIAssistant
        return output

def create_workout_agent() -> AIAssistant:
    """ Create a workout assistant agent """
    
    instruction = """You are a workout expert. User asks you questions about the personal database which contains user past exercise tracking, and personal body statistics tracking.
    First obtain the schema of the database to check the tables and columns, then generate SQL queries to answer the questions.
    The user can also query workout advice for their goals.
    The user can also ask about the BMI and BMR of a person. Calculate this using GetPersonBMI() and GetPersonBMR respectively depending on which one is requested.
    The user can also provide a youtube video of a workout they want to follow. Turn the youtube video into transcript, and coach the user through the workout, wait for the user to finish each exercise and record the user's exercise information into the user's personal database until the workout from the video is complete. 
    Keep responses short and concise, only respond to what the user wants."""
    
    functions = [GetDBSchema(), RunSQLQuery(), GetPersonBMI(), GetPersonBMR(), GetYoutubeTranscript()]
    
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
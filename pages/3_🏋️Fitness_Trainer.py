"""
Title: Track Workout Page
Author: 
Description: Streamlit page for tracking workouts with a chatbot powered by Langchain
"""

import sys
import streamlit as st
from pathlib import Path

# sys.path.insert(0, str(Path(__file__).resolve().parent))
from pages.components.sqlite_interface import question_to_sql
from utils import nav_to

from langchain.utilities.sql_database import SQLDatabase

workout_prompts = [
    "What is my most recent bench press weight, reps, and sets? ",
    "When is the last time I worked out?",
    "Get all exercises I did on 2023 01 17 in markdown table",
    "Graph my exercise date and weight for bench press over time",
]

assistant_default_responses = [
    {
        "role": "assistant", 
        "content": "How may I assist you today? Here are some questions you can ask me...", 
        "workout_df": None,
        "prompts": workout_prompts
    },
]

def reset_conversation():
    st.session_state.workout_conv = None
    st.session_state.workout_conv = assistant_default_responses
    

def main():
    st.set_page_config(page_title="Fitness Trainer", page_icon="🏋️", layout="wide")
    
    thinking = False

    st.header("🏋️ Fitness Trainer")
    st.write("Ask me about your workouts ")
    
    # Session state to store db connection
    if "personal_db" not in st.session_state:
        st.session_state.personal_db = SQLDatabase.from_uri("sqlite:///personal.sqlite3")
    
    # Session state to store the conversation
    if 'workout_conv' not in st.session_state:
        st.session_state.workout_conv = [assistant_default_responses[0]]

    # Display chat messages
    for message in st.session_state.workout_conv:
        with st.chat_message(message["role"]):
            st.write(message["content"])
            
            if "workout_df" in message and message["workout_df"] is not None:
                wkdf_c1 = message["workout_df"].columns[0]
                wkdf_c2 = message["workout_df"].columns[1]
                st.line_chart(message["workout_df"], x=wkdf_c1)
                
            if message["role"] == "assistant" and "prompts" in message:
                # Display prompts, 2 rows, 2 columns
                cl1, cl2 = st.columns(2)
                for idx, prompt in enumerate(message["prompts"]):
                    if idx % 2 == 0:

                        with cl1:
                            st.button(prompt, 
                                      on_click=lambda prompt=prompt: st.session_state.workout_conv.append({"role": "user", "content": prompt, "workout_df": None}), 
                                      key=idx, 
                                      use_container_width=True)
                    else:
                        with cl2:
                            st.button(prompt, 
                                      on_click=lambda prompt=prompt: st.session_state.workout_conv.append({"role": "user", "content": prompt, "workout_df": None}), 
                                      key=idx, 
                                      use_container_width=True)
                        
                        
                    # st.button(prompt, on_click=lambda prompt=prompt: st.session_state.workout_conv.append({"role": "user", "content": prompt}))
                    
    # Chat input
    if prompt := st.chat_input(disabled=thinking):
        st.session_state.workout_conv.append({"role": "user", "content": prompt, "workout_df": None})
        with st.chat_message("user"):
            st.write(prompt)
            
    # Generate a new response if last message is not from assistant
    if st.session_state.workout_conv[-1]["role"] != "assistant":
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # TODO Make a call to ...
                response, workout_df = question_to_sql(st.session_state.personal_db, st.session_state.workout_conv[-1]["content"])
                placeholder = st.empty()
                placeholder.markdown(response)
                if workout_df is not None:
                    first_column_name = workout_df.columns[0]
                    second_column_name = workout_df.columns[1]
                    st.line_chart(workout_df, x=first_column_name)
                 
        st.session_state.workout_conv.append({'role': 'assistant', 'content': response, 'workout_df': workout_df})
            
    # Sidebar        
    with st.sidebar:
        st.title("Welcome...")
        
        # Clear conversation button
        st.button("Clear Conversation", on_click=reset_conversation)
           
               

if __name__ == "__main__":
    # Check if user is authenticated
    # if "authentication_status" not in st.session_state or st.session_state["authentication_status"] is None:
    #     print("Redirecting to login page")
    #     nav_to(st, "/")
    # else:
    main()
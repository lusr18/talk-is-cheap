"""
Title: Track Workout Page
Author: 
Description: Streamlit page for tracking workouts with a chatbot powered by Langchain
"""

import streamlit as st

import sys
from pathlib import Path
# sys.path.insert(0, str(Path(__file__).resolve().parent))
from pages.components.sqlite_interface import question_to_sql


def main():
    st.set_page_config(page_title="Track Workout Page", page_icon="🏋️", layout="wide")
    
    thinking = False

    st.header("🏋️ Track Workout Page")
    st.write("Ask me about your workouts ")
    
    # Session state to store the conversation
    if 'workout_conv' not in st.session_state:
        st.session_state.workout_conv = [{"role": "assistant", "content": "How may I assist you today?", "workout_df": None}]

    # Display chat messages
    for message in st.session_state.workout_conv:
        with st.chat_message(message["role"]):
            st.write(message["content"])
            
            if message["workout_df"] is not None:
                st.line_chart(message["workout_df"], x="Date", y="Weight")
            
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
                    st.line_chart(workout_df, x="Date", y="Weight")
                 
        st.session_state.workout_conv.append({'role': 'assistant', 'content': response, 'workout_df': workout_df})
            
    # Sidebar        
    with st.sidebar:
        st.title("Welcome...")
        
        # Clear conversation button
        if st.button("Clear conversation"):
            st.session_state.workout_conv = []
            
            
if __name__ == "__main__":
    main()
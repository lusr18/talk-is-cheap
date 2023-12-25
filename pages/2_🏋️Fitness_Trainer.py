"""
Title: Track Workout Page
Author: 
Description: Streamlit page for tracking workouts with a chatbot powered by Langchain
"""

import os
import sys
from pathlib import Path
import streamlit as st
from streamlit_pills import pills

# Langchain imports
from langchain.utilities.sql_database import SQLDatabase
from langchain.llms.openai import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain, ConversationChain, ConversationalRetrievalChain
from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain.callbacks import get_openai_callback

# Custom imports
# sys.path.insert(0, str(Path(__file__).resolve().parent))
from pages.components.sqlite_interface import question_to_sql, get_workout_routines, get_workout_routine_exercises
from utils import nav_to
from pages.components.trainer_prompts import TrainerPrompts
from pages.components.Assistant.workout_assistant import create_workout_agent


bot_type_dict = {
    "DBBot": 0,
    "RoutineBot": 1,
    "SuggestionsBot": 2,
    "AssistantBot": 3
}

workout_prompts = [
    (1, "What is my most recent bench press weight, reps, and sets?"),
    (2, "When is the last time I worked out?"),
    (3, "Get all exercises I did on 2023 01 17 in markdown table"),
    (4, "Graph my exercise date and weight for bench press over time"),
    (5, "I would like to start a workout session"),
    (6, "I would like to select a workout routine and follow it"),
    (7, "How does sleep affect my workout?"),
    (8, "How does diet affect my workout?"),
    (9, "How does stress affect my workout?"),
    (10, "How does age affect my workout?"),
]

bot_type_default_responses = {
    "DBBot": {
        "role": "assistant", 
        "content": "I am your database bot. You can ask me questions about your workout history!", 
        "prompts": workout_prompts[:4]
        
    },
    "RoutineBot": {
        "role": "assistant",
        "content": "I am your exercise routine bot. You can either start a new workout session to record your workout or select a workout routine to follow. I will guide you through the workout.",
        "prompts": workout_prompts[4:6]
    },
    "SuggestionsBot": {
        "role": "assistant",
        "content": "I am a bot pretrained with lots of workout/fitness knowledge from data on PubMed. You can ask me questions about your workout history or for suggestions on how to improve your workout routine.",
        "prompts": workout_prompts[7:10]
    },
    "AssistantBot": {
        "role": "assistant",
        "content": "I am a all round workout AI assistant. You can ask me workout related questions, or access your personal database."
    }
}


# Trainer的角色
assistant_roles = [
    {
        "role": "assistant",
        "content": "Personal History Tracker"
    }
]

def reset_conversation(bot_type):
    print("Resetting conversation...")
    st.session_state.workout_conv = None
    st.session_state.workout_conv = [bot_type_default_responses[bot_type]]

# 普通LLMChain保存Memory
def get_llmchain():
    memory = ConversationBufferMemory(memory_key="history")
    memory.chat_memory.add_user_message("hi!")
    memory.chat_memory.add_ai_message("what's up?")
    print(memory)

# print("-" * 50)
# print("Loading LLMChain...")
# get_llmchain()
# print("-" * 50)

# 和OpenAI的对话
def get_conversation_chain(prompt):
    llm = ChatOpenAI()
    memory = ConversationBufferMemory(memory_key="history")
    conversation_chain = ConversationChain(llm=llm, memory=memory, prompt=prompt)
    return conversation_chain

# 处理用户输入
#def handle_user_input(user_input, input_type = 5, other_args = None):
#    try:
#        # Track how much tokens are used and cost
#        with get_openai_callback() as cb:
#            if input_type == 5: # Start a new workout session
#                response = st.session_state.w_openai_cc({'input': user_input})
#            elif input_type == 6: # Select a workout routine and follow it
#                response = st.session_state.w_openai_cc({'input': user_input, 'workout_routine': other_args})
#        print("tokens", cb)
#        response = response["response"]
#    except Exception as e:
#        response = "Error" + str(e)
#    return response

# User AssistantAgent to handle user input
def handle_userinput(user_question):
    try: 
        response = st.session_state.assistant_agent.ask_chat(content=user_question)
        return response
    except Exception as e:
        response = f"Error handling user input: {e}"
    return response

def clear_conversation():
    """ Reset conversation, reset AssistantAgent """
    st.session_state.workout_conv = [{"role": "assistant", "content": "I am your workout assistant. Ask me about yourself, workout information, your exercise data, and more!"}]
    
    # Reset AssistantAgent
    
    st.session_state.assistant_agent = create_workout_agent()
    st.session_state.assistant_agent.create_chat_instance()
    pass

# 和Llama27b的对话
def get_llama27b_conversation_chain():
    pass

def append_prompt(prompt):
    print("Appending prompt")      
    if prompt[0] == 5: # Start a new workout session
        st.session_state.w_openai_cc = get_conversation_chain(prompt=TrainerPrompts().trainer_new_session_chatmodel_prompt())  
    elif prompt[0] == 6: # Select a workout routine and follow it
        st.session_state.w_openai_cc = get_conversation_chain(prompt=TrainerPrompts().trainer_session_chatmodel_prompt())
            
    st.session_state.workout_conv.append({"role": "user", "content": prompt[1]})

def check_finished(response):
    if "[Finished Workout]" in response:
        print("Finished workout session")
        return True
    return False

def main():
    st.set_page_config(page_title="Fitness Trainer", page_icon="🏋️", layout="wide")
    
    thinking = False

    st.header("🏋️ Fitness Trainer")
    # st.write("Ask me about your workouts ")
    

        
    # Session state for db name
    if "personal_db_name" not in st.session_state:
        st.session_state.personal_db_name = None
        st.session_state.personal_db_name = "database/personal_db.sqlite3"
        
    # Session state to store db connection
    if "personal_db" not in st.session_state:
        st.session_state.personal_db = SQLDatabase.from_uri(f"sqlite:///{st.session_state.personal_db_name}")
        
     # Session state for bot type
    if "bot_type" not in st.session_state:
        st.session_state.bot_type = "DBBot"
    
    # Session state to store the conversation
    if 'workout_conv' not in st.session_state:
        st.session_state.workout_conv = [bot_type_default_responses[st.session_state.bot_type]]
        
    # Session state for workout chatbot with OpenAI
    if "w_openai_cc" not in st.session_state:
        st.session_state.w_openai_cc = None
        
    # Session state for model type
    if "model_type" not in st.session_state:
        st.session_state.model_type = "OpenAI"
        
    # Session state for assistant roles
    if "assistant_roles" not in st.session_state:
        st.session_state.assistant_roles = 0

    # Create assistant agent
    if "assistant_agent" not in st.session_state:
        st.session_state.assistant_agent = create_workout_agent()
        st.session_state.assistant_agent.create_chat_instance()
        
        
    # # Display chat messages
    # for message in st.session_state.workout_conv:
    #     with st.chat_message(message["role"]):
    #         if "markdown" in message and message["markdown"]:
    #             st.markdown(message["content"])
    #         else:
    #             st.write(message["content"])
            
    #         if "workout_df" in message and message["workout_df"] is not None:
    #             wkdf_c1 = message["workout_df"].columns[0]
    #             wkdf_c2 = message["workout_df"].columns[1]
    #             st.line_chart(message["workout_df"], x=wkdf_c1)
                
    #         if message["role"] == "assistant" and "prompts" in message:
    #             # Display prompts, 2 rows, 2 columns
    #             num_cols = len(message["prompts"])
                
    #             cl1, cl2 = st.columns(2)
    #             for idx, prompt in enumerate(message["prompts"]):
    #                 if idx % 2 == 0:
    #                     with cl1:
    #                         st.button(prompt[1], 
    #                                   on_click=lambda prompt=prompt: append_prompt(prompt), 
    #                                   key=prompt[0], 
    #                                   use_container_width=True)
    #                 else:
    #                     with cl2:
    #                         st.button(prompt[1], 
    #                                   on_click=lambda prompt=prompt: append_prompt(prompt), 
    #                                   key=prompt[0], 
    #                                   use_container_width=True)
    #                 # st.button(prompt, on_click=lambda prompt=prompt: st.session_state.workout_conv.append({"role": "user", "content": prompt}))        
                    
                    
    #         if "finished" in message and message["finished"]:
    #             st.button("Save workout session", on_click=lambda: st.session_state.workout_conv.append({"role": "assistant", "content": "Workout session saved!"}, use_container_width=False))
    
    # Display chat messages
    for idx, message in enumerate(st.session_state.workout_conv):
        with st.chat_message(message["role"]):
            st.write(message["content"])
            if "image" in message and message["image"] is not None:
                st.image(message["image"], width=300)

    # Chat input
    if prompt := st.chat_input(disabled=thinking):
        st.session_state.workout_conv.append({"role": "user", "content": prompt, "workout_df": None})
        with st.chat_message("user"):
            st.write(prompt)
            
    # # Generate a new response if last message is not from assistant
    # if st.session_state.workout_conv[-1]["role"] != "assistant":
    #     with st.chat_message("assistant"):
    #         with st.spinner("Thinking..."):    
    #             finished = False
    #             workout_df = None
    #             # TODO Set up conversation chain based on input...
    #             if st.session_state.model_type == "OpenAI":
    #                 if st.session_state.w_openai_cc is None:
    #                     response, workout_df = question_to_sql(st.session_state.personal_db, st.session_state.workout_conv[-1]["content"])
    #                     placeholder = st.empty()
    #                     placeholder.markdown(response)
    #                     if workout_df is not None:
    #                         first_column_name = workout_df.columns[0]
    #                         second_column_name = workout_df.columns[1]
    #                         st.line_chart(workout_df, x=first_column_name)
    #                 else:
    #                     response = handle_user_input(st.session_state.workout_conv[-1]["content"])
    #                     # placeholder = st.empty()
    #                     # placeholder.markdown(response)
    #                     finished = check_finished(response)
    #                     if finished:
    #                         with st.container():
    #                             st.markdown(response)
    #                             st.button("Save workout session", use_container_width=False)
    #                     else:
    #                         st.markdown(response)
                                
                                
    #             elif st.session_state.model_type == "Llama27b":
    #                 # TODO Set up conversation chain based on input...
    #                 pass
                    
    #     st.session_state.workout_conv.append(
    #         {'role': 'assistant', 'content': response, 'workout_df': workout_df, 'finished': finished })

    # Generate a new response if the last message is not from the assistant
    if st.session_state.workout_conv[-1]["role"] != "assistant":
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # TODO Make a call to ...
                response = handle_userinput(st.session_state.workout_conv[-1]["content"])
                # response = "Echo response"
                placeholder = st.empty()
                placeholder.markdown(response)
            
        st.session_state.workout_conv.append({'role': 'assistant', 'content': response})       

    # Sidebar        
    with st.sidebar:    
        # Clear conversation button
        st.subheader("Clear Conversation")
        clear_conv = st.button("Clear", use_container_width=True)
        if clear_conv:
            reset_conversation(st.session_state.bot_type)
            st.rerun()
        
        # Choose LLM model (llama27b or OpenAI)
        st.subheader("Select a model")
        model_types = ["OpenAI", "Llama27b"]
        model_type_emojis = ["🤖", "🦙"]
        model_radio = st.radio(f"Models", model_types, index=0, format_func=lambda x: model_type_emojis[model_types.index(x)] + " " + x)
        # if model_radio is selected, set the model type
        if model_radio: 
            # print(f"{st.session_state.model_type} -> {model_radio}")
            st.session_state.model_type = model_radio
    
        # Choose a bot type
        st.subheader("Select a bot")
        bot_types = ["DBBot", "RoutineBot", "SuggestionsBot", "AssistantBot"]
        bot_type_emojis = ["🤖", "🤖", "🤖", "🤖"]
        bot_radio = st.radio(f"Bots", bot_types, index=bot_type_dict[st.session_state.bot_type], format_func=lambda x: bot_type_emojis[bot_types.index(x)] + " " + x)
        # If bot_radio is selected, set the bot type
        if bot_radio and st.session_state.bot_type != bot_radio:
            print(f"{st.session_state.bot_type} -> {bot_radio}")
            st.session_state.bot_type = bot_radio
            st.session_state.workout_conv = [bot_type_default_responses[bot_radio]]
            st.rerun()

        # Choose workout routine
        if st.session_state.bot_type == "RoutineBot":
            st.header("Select a workout routine")
            workout_types = ["Full Body", "Upper Body", "Lower Body", "Core", "Cardio"]
            workout_type_emojis = ["🔥", "💪", "🦵", "🤸", "🏃"]
            workout_filter = pills("Workout types", workout_types, workout_type_emojis)
            
            workouts = get_workout_routines(st.session_state.personal_db_name)
            for workout in workouts:
                st.button(workout[1], use_container_width=True, on_click=lambda workout=workout: 
                    st.session_state.workout_conv.append(
                        {
                            "role": "user", 
                            "content": get_workout_routine_exercises(
                                st.session_state.personal_db_name,
                                workout[0]),
                            "markdown": True
                        }
                    )
                )
               
if __name__ == "__main__":
    # Check if user is authenticated
    # if "authentication_status" not in st.session_state or st.session_state["authentication_status"] is None:
    #     print("Redirecting to login page")
    #     nav_to(st, "/")
    # else:
    main()
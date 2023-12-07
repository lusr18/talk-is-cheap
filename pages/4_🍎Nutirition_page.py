import streamlit as st
from langchain.llms.openai import OpenAI
from langchain.chat_models import ChatOpenAI
# from langchain.vectorstores import vectorstore
from langchain.chains import ConversationChain, ConversationalRetrievalChain
from langchain.chains.conversation.memory import ConversationBufferMemory
from utils import nav_to
import os
from huggingface.blip import blip_api

import base64
from pathlib import Path
from utils import load_bootstrap


def img_to_bytes(img_path):
    img_bytes = Path(img_path).read_bytes()
    encoded = base64.b64encode(img_bytes).decode()
    return encoded

def img_to_html(img_path):
    file_type = img_path.split(".")[-1]
    img_html = "<img src='data:image/{};base64,{}' class='img-fluid' width='300'>".format(
       file_type, img_to_bytes(img_path)
    )
    return img_html


def get_conversation_chain():
    llm = ChatOpenAI()
    memory = ConversationBufferMemory(memory_key="history")
    conversation_chain = ConversationChain(llm=llm, memory=memory)
    print(conversation_chain.prompt)
    return conversation_chain

def handle_userinput(user_question):
    response = st.session_state.chatopenai_convo({'input': user_question})
    print(response)
    # st.session_state.chat_history = response['chat_history']
    return response["response"]


def uploader_callback(a):
    print(a)
    

def main():
    st.set_page_config(page_title="Nutrition Page", page_icon="🍎", layout="wide")
    
    st.header("🍎 Nutrition Page")
    st.write("Keep track of your nutrition here")
    
    # Session state to store the conversation
    if 'nutrition_conv' not in st.session_state:
        st.session_state.nutrition_conv = [{"role": "assistant", "content": "Ask me about nutrition? Or upload an image for food analysis"}]
    
    # Create conversation chain
    if "chatopenai_convo" not in st.session_state:
        st.session_state.chatopenai_convo = get_conversation_chain()
        
        
    # Session state for image
    # if "img_file_buffer" not in st.session_state:
    
                
    st.session_state.img_file_buffer = st.file_uploader(
        label="Label", type=['png', 'jpg'], label_visibility="collapsed", 
        on_change=lambda prompt="prompt": st.session_state.nutrition_conv.append(
            {
                "role": "user", "content": "What is this?", "onload": st.session_state.img_file_buffer,
            }
        ) if st.session_state['file_uploader'] is not None else None,
        key="file_uploader"
    )
     # if st.session_state.nutrition_conv[-1]["role"] != "user":
    if st.session_state.img_file_buffer != None:
        with open(os.path.join("temp",  st.session_state.img_file_buffer.name),"wb") as f:
            f.write(st.session_state.img_file_buffer.getbuffer())

    # Display chat messages
    for idx, message in enumerate(st.session_state.nutrition_conv):
        with st.chat_message(message["role"]):
            st.write(message["content"])
            if "image" in message and message["image"] is not None:
                st.image(message["image"], width=300)
          
    # Chat input
    if prompt := st.chat_input():
        st.session_state.nutrition_conv.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
            
    # Generate a new response if the last message is not from the assistant
    if st.session_state.nutrition_conv[-1]["role"] != "assistant":
        print(st.session_state.nutrition_conv[-1])
        image_path = "./" + os.path.join("temp",  st.session_state.img_file_buffer.name)
        print(image_path)
        print("Exists: ", os.path.exists(image_path))
        print("Listdir: ", os.listdir("./temp"))
        if st.session_state.nutrition_conv[-1]["content"] == "What is this?" and st.session_state.img_file_buffer != None:
            if os.path.exists(image_path):
                with st.chat_message("assistant"):
                    with st.spinner("Analyzing image..."):
                        # TODO Make a call to ...
                        image_path = os.path.join("temp",  st.session_state.img_file_buffer.name)
                        # response = "Image analysis complete"
                        response = blip_api(image_path)
                        
                        with st.container():
                            st.write("Image analysis complete: " + response)
                            st.image(st.session_state.img_file_buffer, width=300)
                            
                st.session_state.nutrition_conv.append({'role': 'assistant', 
                    'content': "Image analysis complete:" + response, 
                    'image':  st.session_state.img_file_buffer, 
                    'image_link': os.path.join("temp",  st.session_state.img_file_buffer.name)
                })
                # st.session_state.nutrition_conv.append({'role': 'assistant', 'content': response})
                # st.session_state.img_file_buffer = None
            
        else:
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    # TODO Make a call to ...
                    # response = handle_userinput(st.session_state.nutrition_conv[-1]["content"])
                    response = "Echo response"
                    placeholder = st.empty()
                    placeholder.markdown(response)
                
            st.session_state.nutrition_conv.append({'role': 'assistant', 'content': response})
    
   
        
           

    
if __name__ == "__main__":
    # if "authentication_status" not in st.session_state or st.session_state["authentication_status"] is None:
    #     print("Redirecting to login page")
    #     nav_to(st, "/")
    # else:

    main()
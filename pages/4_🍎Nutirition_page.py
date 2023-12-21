import streamlit as st
from langchain.llms.openai import OpenAI
from langchain.chat_models import ChatOpenAI
# from langchain.vectorstores import vectorstore
from langchain.chains import ConversationChain, ConversationalRetrievalChain
from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain.callbacks import get_openai_callback
from utils import nav_to
import os
from huggingface.hf_apis import image_to_caption

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
    return conversation_chain

def handle_userinput(user_question):
    try: 
        # Track how much tokens are used and cost
        with get_openai_callback() as cb:
            response = st.session_state.chatopenai_convo({'input': user_question})
        print(response)
        print("tokens", cb)
        response = response["response"]
    except Exception as e:
        response = "Error" + str(e)
    return response


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
    if "image_source" not in st.session_state:
        st.session_state.image_source = None
        
    # Session state for model type
    if "model_type" not in st.session_state:
        st.session_state.model_type = "OpenAI"
    
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
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # TODO Make a call to ...
                response = handle_userinput(st.session_state.nutrition_conv[-1]["content"])
                # response = "Echo response"
                placeholder = st.empty()
                placeholder.markdown(response)
            
        st.session_state.nutrition_conv.append({'role': 'assistant', 'content': response})
    
    # Sidedbar
    with st.sidebar.expander("➕ &nbsp; Image Media Uploader", expanded=False):
        # Upload image
        input_file = None
        input_file = st.file_uploader(
            "Upload a single image",
            type=["jpg", "png"],
            accept_multiple_files=False
        )
        
        add_media = st.button(label="Upload!", key="upload_image")
        
        if add_media:
            if input_file:
                # Save image to path
                dest_path = "temp/" + input_file.name
                # Write to path
                with open(dest_path, "wb") as f:
                    f.write(input_file.getvalue())
                    
                st.session_state.image_source = input_file
                
    # Add response to chat
    if add_media:
        print("Sumbit image...")
        if st.session_state.image_source == None:
            print("No image file...")
            st.warning("No uploaded audio files...", icon="⚠️")
        else:
            st.chat_input("Ask a question", key="disabled_chat_input", disabled=True)
            print("Image to text...")
            with st.chat_message("user"):
                with st.container():
                    st.write("What is this image?")
                    st.image(st.session_state.image_source, width=300)
                
                st.session_state.nutrition_conv.append({
                    "role": "user", 
                    "content": "What is this?",
                    "image": st.session_state.image_source,
                    "image_link": "temp/" + st.session_state.image_source.name
                })
            with st.chat_message("assistant"):
                with st.spinner("Analyzing image..."):
                    image_path = os.path.join("temp",  st.session_state.image_source.name)
                    response = image_to_caption(image_path)
                    st.write("This image is a " + response)

            st.session_state.nutrition_conv.append({'role': 'assistant', 'content': "This is an image of" + response})
        st.experimental_rerun()

if __name__ == "__main__":
    main()
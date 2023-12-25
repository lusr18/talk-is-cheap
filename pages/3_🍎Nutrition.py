import os
import streamlit as st
from audiorecorder import audiorecorder
import base64
from pathlib import Path
import time

# Langchain
from langchain.llms.openai import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationBufferMemory

# Custom
from huggingface.hf_apis import image_to_caption
from pages.components.Assistant.nutrition_assistant import create_nutrition_agent
from pages.components.nutrition_agent_langchain import create_nutrition_langchain_agent
from pages.components.nutrition_agent_chatcomp import create_nutrition_agent_chatcomp
from huggingface.distil_small import speech_to_text

agent_types_dict= {
    "Assistant": 0,
    "ZeroShotReact": 1,
    "ChatCompletion": 2
}

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

# Use the conversation chain to handle user input
# def handle_userinput(user_question):
#     try: 
#         # Track how much tokens are used and cost
#         with get_openai_callback() as cb:
#             response = st.session_state.chatopenai_convo({'input': user_question})
#         print(response)
#         print("tokens", cb)
#         response = response["response"]
#     except Exception as e:
#         response = "Error" + str(e)
#     return response
def select_agent(agent_type):
    if agent_type == "Assistant":
        return create_nutrition_agent()
    elif agent_type == "ZeroShotReact":
        return create_nutrition_langchain_agent()
    elif agent_type == "ChatCompletion":
        return create_nutrition_agent_chatcomp()
    else:
        raise ValueError("Invalid agent type")

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
    st.session_state.nutrition_conv = [{"role": "assistant", "content": "I am your nutrition assistant. Ask me about yourself, nutrient information, your food data, and more!"}]
    
    # Reset AssistantAgent
    st.session_state.assistant_agent = select_agent(st.session_state.agent_type)
    
    if st.session_state.agent_type == "Assistant":
        st.session_state.assistant_agent.create_chat_instance()
        
    st.session_state.record_audiorecorder = None


def uploader_callback(a):
    print(a)
    
    
def main():
    st.set_page_config(page_title="Nutrition", page_icon="🍎", layout="wide")
    
    st.header("🍎 Nutrition Page")
    st.write("Keep track of your nutrition here")
    
    # Session state to store agent type
    if 'agent_type' not in st.session_state:
        st.session_state.agent_type = "Assistant"
    
    # Session state to store the conversation
    if 'nutrition_conv' not in st.session_state:
        st.session_state.nutrition_conv = [{"role": "assistant", "content": "I am your nutrition assistant. Ask me about yourself, nutrient information, your food data, and more!"}]
    
    # Create conversation chain
    if "chatopenai_convo" not in st.session_state:
        st.session_state.chatopenai_convo = get_conversation_chain()
        
    # Create assistant agent
    if "assistant_agent" not in st.session_state:
        # st.session_state.assistant_agent = create_nutrition_agent()
        # st.session_state.assistant_agent.create_chat_instance()
        st.session_state.assistant_agent = select_agent(st.session_state.agent_type)
        if st.session_state.agent_type == "Assistant":
            st.session_state.assistant_agent.create_chat_instance()
        
    # Session state for image
    if "image_source" not in st.session_state:
        st.session_state.image_source = None
        
    # Session state for audio
    if "audio_source" not in st.session_state:
        st.session_state.audio_source = None
        
    # Session state for record_audio
    if "record_audio_source" not in st.session_state:
        st.session_state.record_audio_source = None
        
    if "record_audio_length" not in st.session_state:
        st.session_state.record_audio_length = 0
        
    if "record_audiorecorder" not in st.session_state:
        st.session_state.record_audiorecorder = None

        
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
    
    with st.sidebar:
        st.subheader("Clear Conversation")
        clear_conversation_button = st.button("Clear")
        if clear_conversation_button:
            clear_conversation()
            st.rerun()
            
        # Agent Type
        st.subheader("Agent Type")
        agent_types = ["Assistant", "ZeroShotReact", "ChatCompletion"]
        agent_radio = st.radio("Select agent type", agent_types, index=agent_types_dict[st.session_state.agent_type], key="agent_type_radio")
        if agent_radio and agent_radio != st.session_state.agent_type:
            print(f"Agent changed from {st.session_state.agent_type} to {agent_radio}")
            st.session_state.agent_type = agent_radio
            st.session_state.assistant_agent = select_agent(agent_type=agent_radio)
            if st.session_state.agent_type == "Assistant":
                # TODO Clear previous conversation
                st.session_state.assistant_agent.create_chat_instance()
            st.session_state.nutrition_conv = [{"role": "assistant", "content": "I am your nutrition assistant. Ask me about yourself, nutrient information, your food data, and more!"}]
            st.rerun()
            
     # Sidedbar
    with st.sidebar.expander("➕ &nbsp; Image Media Uploader", expanded=False):
        # Upload image
        image_input_file = None
        image_input_file = st.file_uploader(
            "Upload a single image",
            type=["jpg", "png"],
            accept_multiple_files=False
        )
        
        add_image = st.button(label="Upload!", key="upload_image")
        
        if add_image:
            if image_input_file:
                # Save image to path
                dest_path = "temp/" + image_input_file.name
                # Write to path
                with open(dest_path, "wb") as f:
                    f.write(image_input_file.getvalue())
                    
                st.session_state.image_source = image_input_file
                
    # Add response to chat
    if add_image:
        print("Sumbit image...")
        if st.session_state.image_source == None:
            print("No image file...")
            st.warning("No uploaded audio files...", icon="⚠️")
        else:
            st.chat_input("Ask a question", key="disabled_chat_input", disabled=True)
            print("Image to text...")
            with st.chat_message("user"):
                with st.spinner("Analyzing image..."):
                    # with st.container():
                        # st.write("What is this image?")
                        # st.image(st.session_state.image_source, width=300)
                        
                    image_path = os.path.join("temp",  st.session_state.image_source.name)
                    response = image_to_caption(image_path)
                    
                    st.session_state.nutrition_conv.append({
                        "role": "user", 
                        "content": f"Here is an image of {response}. What are it's nutrients?",
                        "image": st.session_state.image_source,
                        "image_link": "temp/" + st.session_state.image_source.name
                    })
        st.rerun()
        
    with st.sidebar.expander("➕ &nbsp; Add Recording", expanded=False):
        # Upload audio
        audio_file = None
        audio_file = st.file_uploader(
            "Add one audio file",
            type=["mp4", "avi", "mov", "mkv", "mp3", "wav", "m4a"],
            accept_multiple_files=False,
        )
        # TODO: Add record option later
        add_audio_media = st.button(label="Upload", key="add_audio_media")

        if add_audio_media:
            if audio_file:
                # Save to temp dir
                dest_path = "temp/" + audio_file.name
                # Save file to destination path
                with open(dest_path, "wb") as f:
                    f.write(audio_file.getvalue())
                # Add to sources list
                # st.session_state.audio_source.append(str(dest_path))
                st.session_state.audio_source = str(dest_path)
        
            else:
                st.error("Please upload files")
                
    # Add voice media to chat, generate response
    if add_audio_media:
        print("Submit audio...")
        if len(st.session_state.audio_source) == 0:
            print("No audio files...")
            st.warning('No uploaded audio files...', icon="⚠️")
        else:
            st.chat_input("Ask a question", key="disabled_chat_input", disabled=True)
            print("Speech to text...")
            with st.chat_message("user"):
                with st.spinner("Uploading..."):
                    text_from_audio = speech_to_text(st.session_state.audio_source)
                    st.write(text_from_audio)
                    # print("Speech to text result: ",text_from_audio)
                st.session_state.nutrition_conv.append({"role": "user", "content": text_from_audio})
            st.rerun()
            
    # Record an audio for input
    with st.sidebar.expander("➕ &nbsp; Record Audio", expanded=False):
        # pip install streamlit-audiorecorder
        st.session_state.record_audiorecorder = audiorecorder("Click to record", "Click to stop recording")
        
        if len(st.session_state.record_audiorecorder) > 0:
            # To play audio in frontend:
            # st.audio(st.session_state.record_audiorecorder.export().read())  

            # To save audio to a file, use pydub export method:
            filename = "temp/audio.wav"
            st.session_state.record_audiorecorder.export(filename, format="wav")

            # To get audio properties, use pydub AudioSegment properties:
            st.write(f"Frame rate: {st.session_state.record_audiorecorder.frame_rate}, Frame width: {st.session_state.record_audiorecorder.frame_width}, Duration: {st.session_state.record_audiorecorder.duration_seconds} seconds")
            
            st.session_state.record_audio_source = filename
            st.session_state.record_audio_length = len(st.session_state.record_audiorecorder)
                    

    if len(st.session_state.record_audiorecorder) > 0 and st.session_state.record_audio_length > 0:
        with st.chat_message("user"):
            print("First Len", len(st.session_state.record_audiorecorder))
            with st.spinner("Uploading audio..."):
                audio_src = st.session_state.record_audio_source
                st.session_state.record_audio_source = None
                text_from_audio = speech_to_text(audio_file=audio_src)
                st.write(text_from_audio)
                
                st.session_state.record_audiorecorder._data = b''
                print("Second Len", len(st.session_state.record_audiorecorder))
                st.session_state.record_audiorecorder = None
                st.session_state.record_audio_source = None
                st.session_state.record_audio_length = 0

                st.session_state.nutrition_conv.append({"role": "user", "content":  text_from_audio})

            
    # Generate a new response if the last message is not from the assistant
    if st.session_state.nutrition_conv[-1]["role"] != "assistant":
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # TODO Make a call to ...
                print("Nutrient agent type", st.session_state.agent_type)
                if st.session_state.agent_type == "Assistant":
                    response = handle_userinput(st.session_state.nutrition_conv[-1]["content"])
                elif st.session_state.agent_type == "ZeroShotReact":
                    response = st.session_state.assistant_agent.run(st.session_state.nutrition_conv[-1]["content"])
                elif st.session_state.agent_type == "ChatCompletion":
                    response = st.session_state.assistant_agent.ask(st.session_state.nutrition_conv[-1]["content"])
                # response = "Echo response"
                placeholder = st.empty()
                placeholder.markdown(response)
            
        st.session_state.nutrition_conv.append({'role': 'assistant', 'content': response})
        
if __name__ == "__main__":
    main()
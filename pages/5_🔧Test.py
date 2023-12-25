# 
import os
import requests
import time
import math
import re
import calendar
import streamlit as st
import base64
from pathlib import Path
from audiorecorder import audiorecorder
# from audio_recorder_streamlit import audio_recorder
# from playsound import playsound
# import pyaudio
# import wave
# import sys
from io import BytesIO
from gtts import gTTS, gTTSError
import pygame


# Langchain
from langchain.llms.openai import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain.callbacks import get_openai_callback

# Custom
from pages.components.trainer_prompts import TrainerPrompts
from pages.components.llama27b_interface import send_llama27b_request
from huggingface.hf_apis import image_to_caption
from huggingface.distil_small import speech_to_text
from utils import en

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

def reset_conversation():
    st.session_state.test_conv = []
    st.session_state.test_conv += [{
            "role": "assistant", 
            "content": "How can I help you?", 
        }
    ]
    
def get_conversation_chain():
    llm = ChatOpenAI()
    memory = ConversationBufferMemory(memory_key="history")
    conversation_chain = ConversationChain(llm=llm, memory=memory)
    return conversation_chain

# Handle user input for OpenAI chat
def handle_userinput(user_question):
    try: 
        with get_openai_callback() as cb:
            response = st.session_state.chatopenai_testconvo({'input': user_question})
        print("tokens", cb)
        print(cb.__dict__)
        response = f"[model: OpenAI, total_tokens: {cb.total_tokens}, total cost: ${cb.total_cost:.6f}]\n" + response["response"]
    except Exception as e:
        response = "Error" + str(e)
    return response

def play_audio(audio_file):
    pass


def show_audio_player(ai_content: str) -> None:
    sound_file = BytesIO()
    try:
        print(f"Playing audio for: {ai_content}")
        tts = gTTS(text=ai_content, lang='en', tld='com')
        tts.write_to_fp(sound_file)
        filename = "./temp/tts.mp3"
        tts.save(filename)
        # # st.write(st.session_state.locale.stt_placeholder)
        # # st.audio(sound_file, autoplay=True)
        pygame.mixer.init()
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()
    except gTTSError as err:
        # st.error(err)
        st.toast(err)
    
def main():
    st.set_page_config(page_title="Test Page", page_icon="🔧", layout="wide")
    
    st.header("🔧 Test Page")
    st.write("Test new features here")
    
    # Session state for loading state speech to text
    if "loading_stt" not in st.session_state:
        st.session_state.loading_stt = False
    
    # Session state to store test_conversation
    if 'test_conv' not in st.session_state:
        st.session_state.test_conv = [{
            "role": "assistant", 
            "content": "How can I help you?", 
        }]
        
    # Session state for sources
    if 'sources' not in st.session_state:
        st.session_state.sources = []
        
    # Session state for image
    if "image_source" not in st.session_state:
        st.session_state.image_source = None
        
    # Session state for record_audio
    if "record_audio_source" not in st.session_state:
        st.session_state.record_audio_source = None
        
    # Session state for model type
    if "model_type" not in st.session_state:
        st.session_state.model_type = "OpenAI"
        
    # Session state for chatopenai_testconvo
    if "chatopenai_testconvo" not in st.session_state:
        st.session_state.chatopenai_testconvo = get_conversation_chain()
        
    # Session state for audio settings
    if "locale" not in st.session_state:
        st.session_state.locale = en
        
    
    
    # Display chat messages
    for idx, message in enumerate(st.session_state.test_conv):
        with st.chat_message(message["role"]):
            if message["role"] == "assistant":
                c1, c2 = st.columns([4, 1])
                with c1:
                    st.write(message["content"])
                with c2:
                    play_audio = st.button("🔊", key=idx)
                    if play_audio:
                        show_audio_player(message['content'])
                                    
            elif message["role"] == "user":  
                st.write(message["content"])
                
            if "image" in message and message["image"] is not None:
                st.image(message["image"], width=300)
                     
    # Chat input
    if prompt := st.chat_input("Ask a question"):
        st.session_state.test_conv.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
            
    # Sidebar
    with st.sidebar:
        # Clear chat
        st.subheader("Clear Chat")
        clear_chat = st.button("Clear Chat")
        if clear_chat:
            reset_conversation()
            st.rerun()
        
        # Choose a model
        st.subheader("Choose a model")
        model_types = ["OpenAI", "Llama27b"]
        model_type_emojis = ["🤖", "🦙"]
        model_radio = st.radio(f"Models", model_types, index=0, format_func=lambda x: model_type_emojis[model_types.index(x)] + " " + x)
        
        if model_radio: 
            st.session_state.model_type = model_radio
    
        st.subheader("Media Uploaders")
    
    with st.sidebar.expander("➕ &nbsp; Add Media", expanded=False):
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
                st.session_state.sources.append(str(dest_path))
        
            else:
                st.error("Please upload files")
    
    # Record an audio for input
    with st.sidebar.expander("➕ &nbsp; Record Audio", expanded=False):
        # pip install streamlit-audiorecorder
        audio_recorder = audiorecorder("Click to record", "Click to stop recording")
        
        if len(audio_recorder) > 0:
            # To play audio in frontend:
            st.audio(audio_recorder.export().read())  

            # To save audio to a file, use pydub export method:
            filename = "temp/audio.wav"
            audio_recorder.export(filename, format="wav")

            # To get audio properties, use pydub AudioSegment properties:
            st.write(f"Frame rate: {audio_recorder.frame_rate}, Frame width: {audio_recorder.frame_width}, Duration: {audio_recorder.duration_seconds} seconds")
            
            st.session_state.record_audio_source = filename
            
    if st.session_state.record_audio_source != None:
        # st.chat_input("Ask a question", key="disabled_chat_input", disabled=True)
        with st.chat_message("user"):
            with st.spinner("Uploading audio..."):
                text_from_audio = speech_to_text(st.session_state.record_audio_source)
                st.write(text_from_audio)
                audio_recorder._data = b''
                st.session_state.record_audio_source = None
 
            st.session_state.test_conv.append({"role": "user", "content": "STT: " + text_from_audio})
        
        # st.rerun()
                    
    with st.sidebar.expander("➕ &nbsp; Add Image", expanded=False):
        # Upload image
        input_file = None
        input_file = st.file_uploader(
            "Add one or more files",
            type=["png", "jpg", "jpeg"],
            accept_multiple_files=False,
        )
        add_image_media = st.button(label="Upload", key="add_image_media")
        
        if add_image_media:
            if input_file:
                # Save image to path
                dest_path = "temp/" + input_file.name
                # Write to path
                with open(dest_path, "wb") as f:
                    f.write(input_file.getvalue())
                    
                st.session_state.image_source = input_file

      
    # Add voice media to chat, generate response
    if add_audio_media:
        print("Submit audio...")
        if len(st.session_state.sources) == 0:
            print("No audio files...")
            st.warning('No uploaded audio files...', icon="⚠️")
        else:
            # st.chat_input("Ask a question", key="disabled_chat_input", disabled=True)
            print("Speech to text...")
            with st.chat_message("user"):
                with st.spinner("Uploading..."):
                    st.session_state.loading_stt = True
                    text_from_audio = speech_to_text(st.session_state.sources[0])
                    st.write(text_from_audio)
                    # print("Speech to text result: ",text_from_audio)
                st.session_state.test_conv.append({"role": "user", "content": "STT: " + text_from_audio})
            st.rerun()
            
    # Add image media to chat, generate response
    if add_image_media:
        print("Sumbit image...")
        if st.session_state.image_source == None:
            print("No image file...")
            st.warning("No uploaded image files...", icon="⚠️")
        else:
            # st.chat_input("Ask a question", key="disabled_chat_input", disabled=True)
            print("Image to text...")
            with st.chat_message("user"):
                with st.container():
                    st.write("What is this image?")
                    st.image(st.session_state.image_source, width=300)
                
                st.session_state.test_conv.append({
                    "role": "user", 
                    "content": "What is this?",
                    "image": st.session_state.image_source,
                    "image_link": "temp/" + st.session_state.image_source.name
                })
            with st.chat_message("assistant"):
                with st.spinner("Analyzing image..."):
                    image_path = os.path.join("temp",  st.session_state.image_source.name)
                    response = image_to_caption(image_path)
                    response = "This image is a " + response + "."
                    response = "[model: Blip Image Captioning] " + response
                    st.write(response)

            st.session_state.test_conv.append({'role': 'assistant', 'content': response})
            st.session_state.chatopenai_testconvo.memory.chat_memory.add_user_message("What is this?")
            st.session_state.chatopenai_testconvo.memory.chat_memory.add_ai_message(response)
        st.rerun()
            
    # Generate a new response if last message is not from assistant    
    if st.session_state.test_conv[-1]["role"] != "assistant":
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # TODO Make a call to ...
                if st.session_state.model_type == "OpenAI":
                    response = handle_userinput(st.session_state.test_conv[-1]["content"])
                    placeholder = st.empty()
                    placeholder.markdown(response)
                elif st.session_state.model_type == "Llama27b":
                    # TODO Make a call to llama27b model running locally?
                    response, time_taken = send_llama27b_request(st.session_state.test_conv[1:], st.session_state.test_conv[-1]["content"], TrainerPrompts().default_llama27b_prompt())
                    placeholder = st.empty()
                    response = f"[model: Llama27b, time taken: {time_taken:.2f}s]\n" + response
                    placeholder.markdown(response)
        st.session_state.test_conv.append({'role': 'assistant', 'content': response})   
            
if __name__ == "__main__":
    main()
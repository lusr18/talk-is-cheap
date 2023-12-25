import sys
import os
import time
import yaml
from yaml.loader import SafeLoader

import streamlit as st
import streamlit_authenticator as stauth
from streamlit_authenticator import Authenticate
from dotenv import load_dotenv

# from utils import get_pdf_text, get_text_chunks, get_vectorstore, \
#     get_conversation_chain, get_pdfs, get_conversation_chain_2
    
from templates import user_template, bot_template, css

from langchain.utilities.sql_database import SQLDatabase

# Load environmental variables for whole app
load_dotenv()
os.environ["HUGGINGFACEHUB_API_TOKEN"] = os.getenv("HUGGINGFACEHUB_API_TOKEN")
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["NINJA_API_KEY"] = os.getenv("NINJA_API_KEY")
os.environ["MILVUS_HOST"] = os.getenv("MILVUS_HOST")
os.environ["MULVUS_HOST2"] = os.getenv("MILVUS_HOST2")
os.environ["MILVUS_TOKEN"] = os.getenv("MILVUS_TOKEN")
os.environ["OPENAI_DEFAULT_MODEL"] = os.getenv("OPENAI_DEFAULT_MODEL")
os.environ["MILVUS_HOST2_AUTH"] = os.getenv("MILVUS_HOST2_AUTH")

# Proxy
# os.environ["HTTP_PROXY"] = os.getenv("HTTP_PROXY")
# os.environ["HTTPS_PROXY"] = os.getenv("HTTPS_PROXY")
# os.environ["ALL_PROXY"] = os.getenv("ALL_PROXY")

# Remove HTTP_PROXY and HTTPS_PROXY
if 'HTTP_PROXY' in os.environ:
    del os.environ['HTTP_PROXY']
if 'HTTPS_PROXY' in os.environ:
    del os.environ['HTTPS_PROXY']
if 'ALL_PROXY' in os.environ:
    del os.environ['ALL_PROXY']

import urllib
print(urllib.request.getproxies())

st.set_page_config(page_title="Home Page", page_icon="🏠", layout="wide")

# Authentication
with open('authconf.yml') as file:
    config = yaml.load(file, Loader=SafeLoader)
    # print(config)
    
if "authenticator" not in st.session_state:
    st.session_state.authenticator = Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
        config['preauthorized']
    )
    
def main():    
    st.write(css, unsafe_allow_html=True)
    
    st.header("🏠 Home Page")
    st.subheader("Welcome to Talk is Cheap!")
    st.write("This is a demo of the Talk is Cheap platform.")
    st.write("This is a platform for AI assistant personal fitness and nutrition trainer")
    markdown_text = """
    1. **Login** to the platform
    2. **Knowledge** page to interact with our fitness/health knowledge base
    3. **Fitness** page to interact with our fitness assistant
    4. **Nutrition** page to interact with our nutrition assistant 
    5. **Test** page to test some upcoming features   
    """
    st.markdown(markdown_text)
    
    with st.sidebar:
        # Logout button
        if "authentication_status" in st.session_state and st.session_state["authentication_status"]:
            st.write(f'Welcome *{st.session_state["name"]}*')
            st.session_state.authenticator.logout('Logout', 'main')
            
        st.subheader("🔐 OpenAI API KEY")
        st.text_input("OpenAI API KEY", 
                      value=os.getenv("OPENAI_API_KEY"),
                      type="password", 
                      label_visibility="collapsed"
                    )
        
        st.subheader("🔐 HuggingFace API KEY")
        st.text_input("HuggingFace API KEY", 
                      value=os.getenv("HUGGINGFACEHUB_API_TOKEN"),
                      type="password", 
                      label_visibility="collapsed"
                    )

        st.subheader("🔐 Ninja API KEY")
        st.text_input("Ninja API KEY", 
                      value=os.getenv("NINJA_API_KEY"),
                      type="password", 
                      label_visibility="collapsed"
        )
        
        st.subheader("🔐 Milvus API KEY")
        st.text_input("Milvus API KEY", 
                      value=os.getenv("MILVUS_TOKEN"),
                      type="password", 
                      label_visibility="collapsed"
        )
    
   
def login_form():
    name, authentication_status, username = st.session_state.authenticator.login('Login', 'main')
    print("Login Status", name, authentication_status, username)
    
    if st.session_state["authentication_status"]:
        # authenticator.logout('Logout', 'main')
        # st.write(f'Welcome *{st.session_state["name"]}*')
        # st.title('Some content')
        main()
    elif st.session_state["authentication_status"] == False:
        st.error('Username/password is incorrect')
    elif st.session_state["authentication_status"] == None:
        st.warning('Please enter your username and password')


if __name__ == '__main__':
    # TODO Create browser cookie to store authentication status
    # if st.session_state["authentication_status"] == None:
    #     login_form()
    # else:
    #     main()
    main()
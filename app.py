import sys
import os
import streamlit as st
from dotenv import load_dotenv
from utils import get_pdf_text, get_text_chunks, get_vectorstore, get_conversation_chain, get_pdfs, get_conversation_chain_2
from templates import user_template, bot_template, css
import time

from langchain.utilities.sql_database import SQLDatabase

# Load environment variables
load_dotenv()
os.environ["HUGGINGFACEHUB_API_TOKEN"] = os.getenv("HUGGINGFACEHUB_API_TOKEN")
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# Session state to store db connection
if "personal_db" not in st.session_state:
    st.session_state.personal_db = SQLDatabase.from_uri("sqlite:///personal.sqlite3")

def handle_userinput(user_question):
    response = st.session_state.conversation({'question': user_question})
    st.session_state.chat_history = response['chat_history']

    for i, message in enumerate(st.session_state.chat_history):
        if i % 2 == 0:
            st.write(user_template.replace(
                "{{MSG}}", message.content), unsafe_allow_html=True)
        else:
            st.write(bot_template.replace(
                "{{MSG}}", message.content), unsafe_allow_html=True)

print(f"{time.time()} Refresh")

def main():
    st.set_page_config(page_title="Chat with multiple PDFs", page_icon=":books:")
    st.write(css, unsafe_allow_html=True)
    
    
    # Session state to store the conversation
    if "conversation" not in st.session_state:
        st.session_state.conversation = []
        st.session_state.conversation = get_conversation_chain_2()
        
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
        
    st.header("Chat with multiple PDFs")
    user_question = st.text_input("Ask a question about your documents", disabled=("conversation" not in st.session_state))
    if user_question:
        handle_userinput(user_question)
        
    
    with st.sidebar:
        st.subheader("List of PDFs")
        # List of PDFs on sidebar
        pdfs = get_pdfs() 
        for pdf in pdfs:
            st.write(pdf)
            
        # st.subheader("Pages")
        # page = st.radio("Select a page", list(pages.keys()))
  
        
        # pdf_docs = st.file_uploader("Upload PDFs", type="pdf", accept_multiple_files=True)
        
        # if st.button("Process"):
        #     with st.spinner("Processing..."):
        #         # Get pdf text
        #         raw_text = get_pdf_text(pdf_docs)
                
        #         # Get the text chunks
        #         text_chunks = get_text_chunks(raw_text)

        #         # Create vector embeddings
        #         vectorstore = get_vectorstore(text_chunks)
                
        #         # Create conversation chain
        #         st.session_state.conversation = get_conversation_chain(vectorstore)
                
        #         print(st.session_state.conversation.__dict__)
        #         print(st.session_state.conversation.combine_docs_chain.llm_chain.prompt)
                    
        #     st.balloons()
        #     st.success("Done!")
    # if page == "Knowledge":
    #     pages[page]()
    # elif page == "Track Workout":
    #     pages[page]()
        

if __name__ == '__main__':
    main()
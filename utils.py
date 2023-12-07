import os
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings, HuggingFaceInstructEmbeddings, HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.llms import HuggingFaceHub
    
import streamlit as st


def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def get_text_chunks(text):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    return chunks
    
def get_vectorstore(text_chunks):
    embeddings = OpenAIEmbeddings() 
    # embeddings = HuggingFaceInstructEmbeddings(model_name="hkunlp/instructor-xl")
    vectorstore = FAISS.from_texts(text_chunks, embeddings)
    return vectorstore
    
def get_conversation_chain(vectorstore):
    # llm = HuggingFaceEmbeddings(model_name="gpt2")
    llm = ChatOpenAI()
    memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory,        
    )
    return conversation_chain

def get_pdfs():
    file_path = os.path.expanduser("/home/ftpuser/")
    files = os.listdir(file_path)
    pdfs = [os.path.join(file_path, pdf) for pdf in files if pdf.endswith(".pdf")]
    return pdfs

from persist_store import load_database
def get_conversation_chain_2():
    memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)
    retriever = load_database()
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=ChatOpenAI(),
        retriever=retriever,
        memory=memory,        
    )
    return conversation_chain

# Programatically navigate to a URL in streamlit
def nav_to(st, url):
    nav_script = """
        <meta http-equiv="refresh" content="0; url='%s'">
    """ % (url)
    st.write(nav_script, unsafe_allow_html=True)    

def load_bootstrap():
    return st.markdown('<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">', unsafe_allow_html=True)



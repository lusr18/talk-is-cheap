"""
Title: Knowledge Page
Author: 
Description: Directly interact with embedded knowledge base
"""
import os
import streamlit as st
from dotenv import load_dotenv

# Langchain
from langchain.vectorstores import Chroma, Milvus
from langchain.prompts import PromptTemplate
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import RetrievalQA, ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.llms import OpenAI
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain.callbacks import get_openai_callback

# Custom
from utils import get_pdf_text, get_text_chunks, get_vectorstore, get_conversation_chain, get_pdfs

vector_stores = ["Milvus", "Chroma", "Faiss"]
chat_models = ["OpenAI 3.5", "OpenAI 4.0", "Llama27b"]

def handle_userinput(user_question):
    try: 
        with get_openai_callback() as cb:
            # response = st.session_state.conversation({'input': user_question})
            # response = st.session_state.conversation(user_question)
            response = st.session_state.conversation({'question': user_question})
            
        print("Knowledge page tokens:", cb)
        response = response['answer']
    except Exception as e:
        response = f"Error handling user input: {e}"
    return response

def get_embedless_conversation_chain():
    llm = ChatOpenAI()
    memory = ConversationBufferMemory(memory_key="history")
    conversation_chain = ConversationChain(llm=llm, memory=memory)
    print(conversation_chain.prompt)
    return conversation_chain

def process_llm_response(llm_response):
    print(llm_response['result'])
    print("\n\nSources")
    for source in llm_response["source_documents"]:
        print(source.metadata["source"])
        
def get_vectorstore(vector_store_name):
    if vector_store_name == "Milvus":
        vectorstore = Milvus(
            embedding_function = OpenAIEmbeddings(),
            connection_args = {
                # 'host': 'localhost',
                # 'port': '19530'
                'collection_name': 'LangChainCollection',
                'uri' : os.getenv("MILVUS_HOST"),
                'token': os.getenv("MILVUS_TOKEN")
            }
        )
    elif vector_store_name == "Chroma":
        vectorstore = Chroma(
            embedding_function = OpenAIEmbeddings(),
            persist_directory = "./database/chromadb"
        )
    else:
        raise ValueError("Vector store not supported")
    return vectorstore

# Get vectorstore retriever
def get_vectorstore_retriever():
    return st.session_state.vector_db.as_retriever(search_kwargs={"top_k": 5})


# TODO Move to utils
prompt_template = '''
You are a health and nutrition expert with immense knowledge and experience in the field. Answer my questions based on your knowledge and our older conversation. Do not make up answers.
If you do not know the answer to a question, just say "I don't know".

Given the following conversation and a follow up question, answer the question.

{chat_history}

question: {question}
'''

PROMPT_1 = PromptTemplate.from_template(template=prompt_template)


# Get conversation chain with retriever
def get_qa_conversational_chain():
    memory = ConversationBufferMemory(
        memory_key='chat_history', 
        return_messages=True,
        output_key='answer'
    )
    retriever = get_vectorstore_retriever()

    
    # Create a chain to answer the questions
    llm = ChatOpenAI(temperature=0, model_name=os.getenv("OPENAI_DEFAULT_MODEL"))
    qa_chat = ConversationalRetrievalChain.from_llm(
        llm=llm,
        memory=memory,
        retriever=retriever, 
        return_source_documents=True,
        # condense_question_prompt=PROMPT_1
    )
    return qa_chat

# Get retrievalqa chain
def get_retrievalqa_chain():
    llm = OpenAI()
    retriever = get_vectorstore_retriever()
    
    # Make a chain to answer the questions
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff", 
        retriever=retriever,
        return_source_documents=True) 
    
    return qa_chain
  
def clear_conversation():
    st.session_state.knowledge_conv = [{"role": "assistant", "content": "Ask me anything fitness/health related. I will try my best to answer given the embedded knowledge base."}]

def main():
    st.set_page_config(page_title="Knowledge Page", page_icon="🧠", layout="wide")

    st.header("🧠 Knowledge Page")
    st.write("Interact with our fitness/health knowledge base.")
    
    # Session state to store the vector store name
    if "vector_store_name" not in st.session_state:
        st.session_state.vector_store_name = "Milvus"
       
    # Session state to store the chat model 
    if "chat_model" not in st.session_state:
        st.session_state.chat_model = "OpenAI 3.5"
        
    # Session state to store the vector store
    if "vector_db" not in st.session_state:
        st.session_state.vector_db = get_vectorstore("Milvus")
        
    # Session state to store the conversation
    if 'knowledge_conv' not in st.session_state:
        st.session_state.knowledge_conv = [{"role": "assistant", "content": "Ask me anything fitness/health related. I will try my best to answer given the embedded knowledge base."}]
        
    # Create conversation chain
    if "conversation" not in st.session_state:
       st.session_state.conversation = get_qa_conversational_chain()
    

    # Display chat messages
    for message in st.session_state.knowledge_conv:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Chat input
    if prompt := st.chat_input():
        st.session_state.knowledge_conv.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
    
    # Generate a new response if the last message is not from the assistant
    if st.session_state.knowledge_conv[-1]["role"] != "assistant":
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # TODO Make a call to ...
                response = handle_userinput(st.session_state.knowledge_conv[-1]["content"]) #TODO append propmt engineering
                # process_llm_response(response)
                placeholder = st.empty()
                placeholder.markdown(response)      
        
        st.session_state.knowledge_conv.append({'role': 'assistant', 'content': response})
        
    
    with st.sidebar:
        st.subheader("Clear Conversation")
        clear_conversation_button = st.button("Clear")
        if clear_conversation_button:
            clear_conversation()
            st.rerun()    
            
            
        # Choose a vector store
        st.subheader("Choose a vector store")
        vector_store_radio = st.radio("Vector stores", vector_stores, index=0, format_func=lambda x: x, label_visibility="collapsed")
        
        # If vector store radio has changed
        if vector_store_radio and st.session_state.vector_store_name != vector_store_radio:
            st.session_state.vector_store_name = vector_store_radio
            st.session_state.vector_db = get_vectorstore(vector_store_radio)
            st.rerun()
            
        
        # Choose a model
        st.subheader("Choose a model")
        model_radio = st.radio("Chat models", chat_models, index=0, format_func=lambda x: x, label_visibility="collapsed")
        
        # If model radio has changed
        if model_radio and st.session_state.chat_model != model_radio:
            st.session_state.chat_model = model_radio
            pass
            # st.session_state.conversation = get_embedless_conversation_chain()
            # st.rerun()
        
        
        
        
        
        
if __name__ == "__main__":
    main()
"""
Title: Knowledge Page
Author: 
Description:

"""

import streamlit as st
import os
from persist_store import load_database
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA

from langchain.chat_models import ChatOpenAI
from langchain.llms import OpenAI
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationBufferMemory

from utils import get_pdf_text, get_text_chunks, get_vectorstore, get_conversation_chain, get_pdfs

def handle_userinput(user_question):
    response = st.session_state.conversation({'input': user_question})
    #response = st.session_state.conversation({'question': user_question})
    print(response)
    #st.session_state.chat_history = response['chat_history']
    return response["response"]
    #return response["answer"]

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

def main():
    st.set_page_config(page_title="Knowledge Page", page_icon=":books:")

    st.header("Knowledge Page")
    st.write("This is the knowledge page")

    if st.button("Embed"):
        #pdfs = get_pdfs()
        with st.spinner("Processing..."):
            pass
            # Get pdf text
            #raw_text = get_pdf_text(pdfs)
                
            # Get the text chunks
            #text_chunks = get_text_chunks(raw_text)

            # Create vector embeddings
            #vectorstore = get_vectorstore(text_chunks)

            # Create conversation chain
            #st.session_state.conversation = get_conversation_chain(vectorstore)
    
    #load vectorstore retriever
    retriever = load_database()
    
    # Make a chain to answer the questions
    qa_chain = RetrievalQA.from_chain_type(
        llm=OpenAI(),
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True) 
    
    # Session state to store the conversation
    if 'knowledge_conv' not in st.session_state:
        st.session_state.knowledge_conv = [{"role": "assistant", "content": "Ask me about health?"}]

    # Display chat messages
    for message in st.session_state.knowledge_conv:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Create conversation chain
    #if "conversation" not in st.session_state:
    #    st.session_state.conversation = get_embedless_conversation_chain()
            
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
                response = qa_chain(st.session_state.knowledge_conv[-1]["content"]) #TODO append propmt engineering
                process_llm_response(response)
                placeholder = st.empty()
                placeholder.markdown(response['result'])      
        st.session_state.knowledge_conv.append({'role': 'assistant', 'content': response['result']})
        
if __name__ == "__main__":
    main()
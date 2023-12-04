import streamlit as st
from langchain.llms.openai import OpenAI
from langchain.chat_models import ChatOpenAI
# from langchain.vectorstores import vectorstore
from langchain.chains import ConversationChain, ConversationalRetrievalChain
from langchain.chains.conversation.memory import ConversationBufferMemory


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


def main():
    st.set_page_config(page_title="Nutrition Page", page_icon="💉", layout="wide")
    
    st.header("💉 Nutrition Page")
    st.write("Keep track of your nutrition here")
    
    # Session state to store the conversation
    if 'nutrition_conv' not in st.session_state:
        st.session_state.nutrition_conv = [{"role": "assistant", "content": "Ask me about nutrition?"}]
    
    # Create conversation chain
    if "chatopenai_convo" not in st.session_state:
        st.session_state.chatopenai_convo = get_conversation_chain()
        
    # Display chat messages
    for message in st.session_state.nutrition_conv:
        with st.chat_message(message["role"]):
            st.write(message["content"])
            
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
                placeholder = st.empty()
                placeholder.markdown(response)
                
        st.session_state.nutrition_conv.append({'role': 'assistant', 'content': response})
    
    
if __name__ == "__main__":
    main()
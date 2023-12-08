"""
Example to persist embeddings to disk
"""
import os
from langchain.embeddings import HuggingFaceEmbeddings, OpenAIEmbeddings, HuggingFaceInstructEmbeddings
from langchain.text_splitter import CharacterTextSplitter, RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.llms import HuggingFaceHub, OpenAI
from langchain.chains import ConversationalRetrievalChain, RetrievalQA
from langchain.document_loaders import TextLoader, DirectoryLoader, PyPDFLoader, PyPDFDirectoryLoader
from dotenv import load_dotenv

load_dotenv()
os.environ["HUGGINGFACEHUB_API_TOKEN"] = os.getenv("HUGGINGFACEHUB_API_TOKEN")
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

"""
Example: https://www.youtube.com/watch?v=3yPBVii7Ct0&themeRefresh=1
Description: Use chromadb to store embeddings that can be retrieved later
"""
def persist_embeddings():
    # Load and process multiple documents (PDFs)
    print("Loading PDFs")
    pdf_path = os.path.expanduser("/home/ftpuser/")
    loader = DirectoryLoader(pdf_path, glob="*.pdf", loader_cls=PyPDFLoader)
    documents = loader.load()

    # Split text into chunks
    print("Splitting text")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )
    texts = text_splitter.split_documents(documents)
    print(len(texts))
    print(texts[0])
    
    # Create the database
    print("Creating database")
    persist_directory = "db"
    embeddings = OpenAIEmbeddings()

    # model_name = "hkunlp/instructor-large"
    # # model_kwargs = {'device': 'cpu'}
    # # encode_kwargs = {'normalize_embeddings': True}
    # # hf_embeddings = HuggingFaceInstructEmbeddings(
    # #     model_name=model_name,
    # #     model_kwargs=model_kwargs,
    # #     encode_kwargs=encode_kwargs
    # # )
    # embeddings = HuggingFaceEmbeddings(model_name=model_name)

    vectordb = Chroma.from_documents(
        documents=texts, 
        embedding=embeddings, 
        persist_directory=persist_directory
    )
    
    # Persist the database to disk
    print("Persisting database")
    vectordb.persist()
    vectordb = None

def load_database(): 
    # model_name = "hkunlp/instructor-large"
    # model_kwargs = {'device': 'cpu'}
    # encode_kwargs = {'normalize_embeddings': True}
    # hf_embeddings = HuggingFaceInstructEmbeddings(
    #     model_name=model_name,
    #     model_kwargs=model_kwargs,
    #     encode_kwargs=encode_kwargs
    # )
    
    persist_directory = "db"
    embeddings = OpenAIEmbeddings()
    
    # Load the database from disks
    # print("Loading database")
    vectordb = Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings)
    
    # Make a retriever
    # print("Making retriever")
    retriever = vectordb.as_retriever()
    # docs = retriever.get_relevant_documents("Exercise")
    # print("Documents", len(docs))
    
    # sets search limit to top k # of results
    retriever = vectordb.as_retriever(search_kwargs={"k": 2})
    # print(retriever.search_type)
    
    #can pass in queries to retreivalqa
    return retriever
    
    '''
    # Make a chain to answer the questions
    qa_chain = RetrievalQA.from_chain_type(
        llm=OpenAI(),
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True)
    
    def process_llm_response(llm_response):
        print(llm_response['result'])
        print("\n\nSources")
        for source in llm_response["source_documents"]:
            print(source.metadata["source"])
    
    query = "How much exercise is best?"
    llm_response = qa_chain(query)
    print(llm_response)
    '''
    
   
if __name__ == "__main__":
    #persist_embeddings()
    #load_database()
    pass
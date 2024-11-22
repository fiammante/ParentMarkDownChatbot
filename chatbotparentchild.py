from langchain_community.vectorstores import Chroma
from langchain.text_splitter import MarkdownTextSplitter
from langchain_core.prompts import  PromptTemplate
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage
from langchain_community.llms import Ollama
from dotenv import load_dotenv
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_history_aware_retriever
import os
from langchain_core.vectorstores import VectorStore
from langchain.storage._lc_store import create_kv_docstore
from langchain_community.embeddings import OllamaEmbeddings
from langchain.storage import LocalFileStore
from langchain.retrievers import ParentDocumentRetriever
import platform

load_dotenv()
# app config
st.set_page_config(page_title="Streamlit Chatbot", layout="wide",page_icon="🤖")
st.title("Chatbot")
col1, col2 = st.columns(2)

# Prompt
template = """Use the following pieces of context to answer the question at the end. Please follow the following rules:
1. If you don't know the answer, don't try to make up an answer.
2. If you find the answer, write the answer in a detailed way without references.

{context}
Question: {input}
Helpful Answer:"""

prompt= PromptTemplate(
 input_variables=["context", "input"],
 template=template,
)

ollama_ef = OllamaEmbeddings(
    model="all-minilm"
)

path_prefix = "/mnt/d/"
if platform.system() == "Darwin":
    path_prefix = "/tmp/"

# MD splits
parent_splitter = MarkdownTextSplitter(chunk_size=5000,chunk_overlap = 200)
child_splitter = MarkdownTextSplitter(chunk_size=500,chunk_overlap = 60)
vectorstore = Chroma(persist_directory=path_prefix + "data/HIE", embedding_function=ollama_ef)
# Instantiate the LocalFileStore with the root path
fs = LocalFileStore(path_prefix + "data/documentstore")
store = create_kv_docstore(fs)
llm = Ollama(model="wizardlm2", callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]),num_ctx=4096,verbose=True)

document_chain = create_stuff_documents_chain(llm, prompt)
retriever = ParentDocumentRetriever(
        vectorstore=vectorstore,
        docstore=store,
        child_splitter=child_splitter,
        parent_splitter=parent_splitter,
        search_type="similarity", search_kwargs={"k": 6})
retriever_chain = create_history_aware_retriever(llm, retriever, prompt)
chain = create_retrieval_chain(retriever_chain, document_chain)   
context="Context"

def get_response(query,chain ):   
    return chain.stream({"input": query})

def stream_data(response):
    for chunk in (response):
        if "context" in chunk:
            col2.header("Documentation")
            docs=chunk["context"]
            for doc in docs:
                col2.markdown("From **"+os.path.basename(doc.metadata["source"])+"**")
                if "html" in doc.metadata:
                    col2.markdown(doc.metadata["html"],unsafe_allow_html=True)
                else:
                    col2.markdown(doc.page_content)
        if "answer" in chunk:
            yield chunk["answer"]

with col1:
    # session state
    col1.header("Discussion")
    if "chat_history" not in st.session_state:
        print("initialize chat_history")
        st.session_state.chat_history = [
            AIMessage(content="Hello, I am a bot. How can I help you?"),
        ]
    # conversation
    for message in st.session_state.chat_history:
        if isinstance(message, AIMessage):
            with st.chat_message("AI"):
                st.write(message.content)
        elif isinstance(message, HumanMessage):
            with st.chat_message("Human"):
                st.write(message.content)
    
    # user input
    user_query = st.chat_input("Type your message here...")
    if user_query is not None and user_query != "":
        st.session_state.chat_history.append(HumanMessage(content=user_query))
        with st.chat_message("Human"):
            st.markdown(user_query)
        with st.chat_message("AI"):
            response = st.write_stream(stream_data(get_response(user_query, chain)))
        st.session_state.chat_history.append(AIMessage(content=response))
with col2:
    st.header("Documentation")

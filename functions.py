import streamlit as st
import torch
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
import yaml
from langchain_text_splitters import CharacterTextSplitter
from PyPDF2 import PdfReader
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from termcolor import colored
from htmlTemplates import css, user_template, bot_template
from langchain_openai import ChatOpenAI
device = "cuda" if torch.cuda.is_available() else "cpu"
print(colored(f"Device used is {device}","red"))
def get_pdf_raw_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf) 
        for page in pdf_reader.pages:
           text += page.extract_text()
    return text

def get_text_chunks(raw_text):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size= 1000,
        chunk_overlap = 200,
        length_function=len
    )
    chunks = text_splitter.split_text(raw_text)
    
    return chunks

def get_vectorstore(text_chunks):
    embedding = OpenAIEmbeddings()
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embedding)
    return vectorstore

def get_conversation_chain(vector_store):
    llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0.7,
    max_tokens=None,
    timeout=None,
    )
    print(colored(f"-------------------LLM crated successfully-------------------------------", "green"))
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vector_store.as_retriever(), #.as_retriever()
        memory = memory
    )
    
    return conversation_chain

def handle_userinput(user_question):
    response = st.session_state.conversation({"question": user_question})
    st.session_state.chat_history = response['chat_history']
    with st.session_state.chat_container:
        
        for i, message in enumerate(st.session_state.chat_history):
            if i % 2 == 0:
             st.write(user_template.replace("{{MSG}}", message.content), unsafe_allow_html=True)
            else:
             st.write(bot_template.replace("{{MSG}}", message.content), unsafe_allow_html=True)


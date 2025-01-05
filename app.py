import streamlit as st
from dotenv import load_dotenv
import yaml
from htmlTemplates import css, user_template, bot_template
import torch
from termcolor import colored
from functions import (
    handle_userinput,
    get_pdf_raw_text,
    get_conversation_chain,
    get_text_chunks,
    get_vectorstore,
)
def main(): 
    load_dotenv()
    st.set_page_config(page_title="Chat with multiple PDF", page_icon=":books:")
    st.write(css, unsafe_allow_html=True)
    st.session_state.chat_container = st.container()
    
    if  "conversation" not in st.session_state:
        st.session_state.conversation = None
        print(colored(f"--------------------- Conversation in session state and it's value is {st.session_state.conversation} -----------------", "blue"))
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = None
        print(colored(f"--------------------- chat_history in session state and it's value is {st.session_state.chat_history} -----------------", "blue"))
    st.header("Chat with multiple PDF :books:")
    user_question = st.text_input("Ask a question about yoour document: ")
    
    if user_question: 
        handle_userinput(user_question)
        
    with st.sidebar:
        st.subheader("Your documents")
        pdf_docs = st.file_uploader(
            "Upload your PDFs here and click on process",
            accept_multiple_files= True
            )
        if st.button("Process"):
            with st.spinner("Processing..."):
                #! 1. Get the pdf texts
                raw_text = get_pdf_raw_text(pdf_docs)
                print(colored(f"-------------------Raw text collected-------------------------------", "green"))
                #! 2. Get the text chunks
                text_chunks = get_text_chunks(raw_text)
                print(colored(f"-------------------Chunks sucessfully created-------------------------------","green"))
                #! 3. Create vector store
                vector_store = get_vectorstore(text_chunks)
                print(colored(f"-------------------Vector store sucessfully created-------------------------------","green"))
                #! 4. Create conversation chain
                #? In this case if the streamlit do not reinitilized the convesation object.
                st.session_state.conversation = get_conversation_chain(vector_store)

         
if __name__ == "__main__":
    main()
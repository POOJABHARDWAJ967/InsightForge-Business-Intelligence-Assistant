import streamlit as st
from PyPDF2 import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_community.chat_models import ChatOllama
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import google.generativeai as genai
from googleapiclient.discovery import build

import os
from dotenv import load_dotenv
load_dotenv()

# Now this will work automatically
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

# -------------------------------
# Ollama LLM setup
# -------------------------------
llm = ChatOllama(
    model="llama3",   # you can switch to "mistral" or "llama3:8b"
    temperature=0
)

# Function to list available models using Google API
def list_models():
    try:
        service = build('generativeai', 'v1beta', developerKey=os.getenv("GOOGLE_API_KEY"))
        models = service.models().list().execute()
        print("Available models:", models)
    except Exception as e:
        st.error(f"Error listing models: {e}")

# Update the get_vector_store function to handle generic exceptions
def get_vector_store(text_chunks):
    try:
        # Use a valid model name
        embeddings = GoogleGenerativeAIEmbeddings(model="valid-model-name")
        vector_store = FAISS.from_documents(text_chunks, embeddings)
        return vector_store
    except Exception as e:  # Replace GoogleGenerativeAIError with Exception
        st.error(f"Error embedding content: {e}")
        return None

# -------------------------------
# Prompt template for QA
# -------------------------------
prompt = PromptTemplate(
    input_variables=["context", "question"],
    template="""
    Use the following context to answer the question.
    If you don't know the answer, say you don't know.

    Context:
    {context}

    Question:
    {question}

    Answer:
    """
)

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# -------------------------------
# PDF processing functions
# -------------------------------
def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=200)
    return text_splitter.create_documents([text])

# Define embeddings globally or within the main function
embeddings = GoogleGenerativeAIEmbeddings(model="valid-model-name")  # Replace with actual model name

# -------------------------------
# Create and save the FAISS index
# -------------------------------
def create_faiss_index(text_chunks, embeddings):
    """Create and save the FAISS index."""
    vector_store = FAISS.from_documents(text_chunks, embeddings)
    vector_store.save_local("faiss_index")
    return vector_store

# -------------------------------
# Handle user input and load or create FAISS index
# -------------------------------
def user_input(user_question):
    """Handle user input and load or create FAISS index."""
    if not os.path.exists("faiss_index/index.faiss"):
        st.warning("FAISS index not found. Creating a new index...")
        # Assuming `text_chunks` and `embeddings` are available
        create_faiss_index(text_chunks, embeddings)

    try:
        new_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
        docs = new_db.similarity_search(user_question)

        qa_chain = (
            {
                "context": lambda x: format_docs(docs),
                "question": RunnablePassthrough(),
            }
            | prompt
            | llm
            | StrOutputParser()
        )

        response = qa_chain.invoke(user_question)
        st.write("Reply:", response)
    except Exception as e:
        st.error(f"Error loading FAISS index: {e}")

# -------------------------------
# Streamlit UI
# -------------------------------
def main():
    global embeddings
    # Initialize embeddings if not already defined
    embeddings = GoogleGenerativeAIEmbeddings(model="valid-model-name")  # Replace with actual model name

    st.set_page_config(page_title="PDF QA Chatbot", page_icon=":books:")
    st.title("📊 Insight Forge Sale Data Analysis")

    with st.sidebar:
        pdf_docs = st.file_uploader("Upload your PDF files here and click on 'Process'", accept_multiple_files=True)
        if st.button("Submit & Process"):
            with st.spinner("Processing..."):
                raw_text = get_pdf_text(pdf_docs)
                text_chunks = get_text_chunks(raw_text)
                get_vector_store(text_chunks)
                st.success("✅ Processing complete! You can now ask questions about your PDF data.")

    user_question = st.text_input("Ask a question about your PDF:")
    if user_question:
        user_input(user_question)

# THIS IS THE PART THAT WAS CAUSING THE ERROR
if __name__ == "__main__":
    load_dotenv()
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    genai.configure(api_key=GOOGLE_API_KEY)
main()  # Correctly indented!


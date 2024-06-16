import os
import shutil
import time
from app.lib.constants import WEEK_KEY
from app.lib.utils import extract_week_from_query
import openai 
import re
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

class DatabaseCreator:
    def __init__(self, data_path: str, chroma_instance: Chroma):
        self.data_path = data_path
        self.chroma_instance = chroma_instance
        load_dotenv()
        openai.api_key = os.environ['OPENAI_API_KEY']

    def generate_data_store(self):
        documents = self.load_documents()
        chunks = self.split_text(documents)
        self.save_to_chroma(chunks)
        
        
    def load_documents(self):
        filenames = os.listdir(self.data_path)
        pagesTot = []
        for filename in filenames:
            file_path = os.path.join(self.data_path, filename)
            print("Processing file:", file_path)
            loader = PyPDFLoader(file_path)
            pages = loader.load_and_split()
            week = extract_week_from_query(filename)
            print(f"week {week}")
            for page in pages:
                page.metadata[WEEK_KEY] = week
            pagesTot += pages

        return pagesTot

    def split_text(self, documents: list[Document]):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=300,
            chunk_overlap=100,
            length_function=len,
            add_start_index=True,
        )
        chunks = text_splitter.split_documents(documents)
        print(f"Split {len(documents)} documents into {len(chunks)} chunks.")

        document = chunks[1]
        print(document.page_content)
        print(document.metadata)

        return chunks

    def save_to_chroma(self, chunks: list[Document]):
        # if os.path.exists(self.chroma_path):
        #     shutil.rmtree(self.chroma_path)

        # db = Chroma.from_documents(
        #     chunks, OpenAIEmbeddings(), persist_directory=self.chroma_path
        # )
        
        self.chroma_instance.add_documents(chunks)
        self.chroma_instance.persist()

        print(f"Saved {len(chunks)} chunks")



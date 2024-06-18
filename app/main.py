
from app.api.VklassAPI import VklassAPI
from app.lib.constants import PATH_VECKOBREV
from app.services.DatabaseCreator import DatabaseCreator
from app.services.QueryProcessor import QueryProcessor

from multiprocessing import Process
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

CHROMA_PATH = "chroma"

app = FastAPI()
        # Add CORS middleware to the FastAPI app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

embedding_function = OpenAIEmbeddings()
chroma_instance = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

db_creator =  DatabaseCreator(data_path=PATH_VECKOBREV, chroma_instance=chroma_instance)
db_creator.generate_data_store()

queryProcessor = QueryProcessor(chroma_instance=chroma_instance)
vklassAPI = VklassAPI(queryProcessor=queryProcessor)
app.include_router(vklassAPI.router)

#start cmd uvicorn app.main:app --reload 
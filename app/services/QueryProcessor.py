import os
# import shutil
from app.lib.constants import WEEK_KEY
from app.lib.utils import extract_week_from_query
from app.models.responseModel import ResponseModel
import openai 
from dotenv import load_dotenv
# from langchain_community.vectorstores import Chroma
# from langchain_openai import OpenAIEmbeddings, ChatOpenAI
# from langchain.prompts import ChatPromptTemplate
import argparse
# from dataclasses import dataclass
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

CHROMA_PATH = "chroma"
PROMPT_TEMPLATE = """
Svara på frågan baserat endaspå följande sammanhang.:

{context}

---

Svara frågorna baserade på ovan context, svara utförligt på svenska. andra ord för "läxa" är "läsläxa" och "veckans ord": {question}
"""

load_dotenv()

class QueryProcessor:
    def __init__(self, chroma_instance: Chroma):
        print("init queryprocessor")
        self.embedding_function = OpenAIEmbeddings()
        self.db = chroma_instance
        self.model = ChatOpenAI()
        openai.api_key = os.environ['OPENAI_API_KEY']

    def process_query(self, query_text: str) -> str:
        print("start query-----")
        print(query_text)
        week = extract_week_from_query(query_text)

        if week:
            filter = {WEEK_KEY: week}
        else:
            filter = None

    
        results = self.db.similarity_search_with_relevance_scores(query_text, k=3, filter=filter)

        if len(results) == 0 or results[0][1] < 0.7:
            return ResponseModel(response="Kunde inte hitta några svar.", sources="")
        print("results")
        print(results)

        context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
        prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
        prompt = prompt_template.format(context=context_text, question=query_text)
       
        response_text = self.model.predict(prompt)
        sources = [doc.metadata.get("source", None) for doc, _score in results]
      
        formatted_response = f"Response: {response_text}\nSources: {sources}"
        print("context_text")
        print(context_text)

        responseModel = ResponseModel(response=response_text, sources=sources)
        return responseModel

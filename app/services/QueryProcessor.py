import os
from app.lib.constants import WEEK_KEY
from app.lib.utils import extract_week_from_query
from app.models.responseModel import ResponseModel
import openai
from dotenv import load_dotenv
import argparse
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

CHROMA_PATH = "chroma"
PROMPT_TEMPLATE = """
Svara på frågan baserat endast på följande sammanhang.:

{context}

---

Svara på frågan baserad på ovan context, svara utförligt på svenska. Tänk på attandra ord för "läxa" är "läsläxa" och "veckans ord".: {question}
"""




class QueryProcessor:
    def __init__(self, chroma_instance: Chroma):
        print("init queryprocessor")
        self.embedding_function = OpenAIEmbeddings()
        self.db = chroma_instance
        self.model = ChatOpenAI()
        load_dotenv()
        openai.api_key = os.environ['OPENAI_API_KEY']


    def process_query(self, query_text: str) -> str:
        # If a week is metioned, only use the document from this week
        week = extract_week_from_query(query_text)
        if week:
            filter = {WEEK_KEY: week}
        else:
            filter = None

        results = self.db.similarity_search_with_relevance_scores(
            query_text, k=3, filter=filter)

        if len(results) == 0 or results[0][1] < 0.7:
            return ResponseModel(response="Kunde inte hitta några svar.", sources="", send_pdf=False)

        context_text = "\n\n---\n\n".join(
            [doc.page_content for doc, _score in results])
        prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
        prompt = prompt_template.format(
            context=context_text, question=query_text)

        response_text = self.model.predict(prompt)

        sources = [doc.metadata.get("source", None) for doc, _score in results]

        if self.should_send_pdf(query_text):
            file_name = os.path.basename(sources[0])
            return ResponseModel(response=file_name, sources=sources, send_pdf=True)

        response_model = ResponseModel(
            response=response_text, sources=sources, send_pdf=False)
        return response_model


    def should_send_pdf(self, input: str) -> bool:
        input_lower = input.lower()
        return (("skicka" in input_lower) | ("hämta" in input_lower) | ("ge" in input_lower)) & (("veckobrev" in input_lower) | ("veckobrevet" in input_lower))

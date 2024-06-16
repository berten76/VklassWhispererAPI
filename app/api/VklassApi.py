
from fastapi import FastAPI, APIRouter

from app.services.QueryProcessor import QueryProcessor

from pydantic import BaseModel

class QueryRequest(BaseModel):
    query: str


class VklassApi2:
    def __init__(self,  queryProcessor: QueryProcessor):
        print("init queryprocessor")
        self.queryProcessor = queryProcessor
        self.router = APIRouter()
        self.router.add_api_route("/hello", self.hello, methods=["GET"])
        self.router.add_api_route("/", self.postQuery, methods=["POST"])

    async def hello(self):
        return {"Hello llll"}
    
    async def postQuery(self, request: QueryRequest):
        try:
            query = request.query
            response = self.queryProcessor.process_query(query)
            return {"response": response}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
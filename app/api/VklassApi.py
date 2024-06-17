
import os
from app.lib.constants import PATH_VECKOBREV
from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.responses import FileResponse

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
        self.router.add_api_route("/download/{file_name}", self.download_file, methods=["GET"])

    async def hello(self):
        return {"Hello llll33"}
    
    async def postQuery(self, request: QueryRequest):
        try:
            query = request.query
            print(f"queri*************** {query}")
            response = self.queryProcessor.process_query(query)
            print(f"queriRes*************** {query}")
            return response
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    

    async def download_file(self, file_name: str):
        file_path = PATH_VECKOBREV + file_name
 
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        return FileResponse(file_path, media_type='application/pdf', filename=file_name)
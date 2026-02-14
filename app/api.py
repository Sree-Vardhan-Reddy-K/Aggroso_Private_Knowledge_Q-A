import os
from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List

from .rag_service import (
    add_documents,
    list_documents,
    query_documents,
    health_check
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")

app = FastAPI(title="Private Knowledge Q&A", version="1.0")

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


class QueryRequest(BaseModel):
    question: str


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/status")
def status():
    return health_check()


@app.get("/documents")
def get_documents():
    return {"documents": list_documents()}


@app.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")

    saved_paths = []

    for file in files:
        if not file.filename.endswith(".txt"):
            raise HTTPException(status_code=400, detail="Only .txt files allowed")

        file_path = os.path.join(UPLOAD_DIR, file.filename)

        with open(file_path, "wb") as f:
            f.write(await file.read())

        saved_paths.append(file_path)

    count = add_documents(saved_paths)

    return {"status": "success", "files_indexed": count}


@app.post("/query")
def query(payload: QueryRequest):
    try:
        answer, sources = query_documents(payload.question)
        return {"answer": answer, "sources": sources}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

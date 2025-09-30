
import os
from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from temporalio.client import Client
from workflow.document_processing_workflow import DocumentProcessingWorkflow

app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def get_form(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/upload")
async def upload_document(organization: str, user: str, file: UploadFile = File(...)):
    client = await Client.connect(os.getenv("TEMPORAL_GRPC_ENDPOINT"))
    
    # Save file to a temporary location
    temp_file_path = f"/tmp/{file.filename}"
    with open(temp_file_path, "wb") as buffer:
        buffer.write(await file.read())

    await client.start_workflow(
        DocumentProcessingWorkflow.run,
        {"organization": organization, "user": user, "file_path": temp_file_path},
        id=f"doc-processing-{organization}-{user}-{file.filename}",
        task_queue="main-task-queue",
    )
    return {"message": "Document processing started."}


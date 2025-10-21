from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from worker.queue import queue
from worker.tasks.process_book import process_book

app = FastAPI(title="Palabra Worker API", version="1.0")

class EnqueueRequest(BaseModel):
    book_id: int
    filename: str


@app.post("/enqueue")
def enqueue_book_task(req: EnqueueRequest):
    """Accepts a book_id and filename, and enqueues processing job."""
    try:
        job = queue.enqueue(process_book, req.book_id, req.filename)
        return {"job_id": job.id, "status": "queued"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

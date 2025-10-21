from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from uuid import UUID
from worker.task_queue import queue
from worker.tasks.process_book import process_book

app = FastAPI(title="Palabra Worker API", version="1.0")

class EnqueueRequest(BaseModel):
    book_id: UUID
    filename: str


@app.post("/enqueue")
def enqueue_book_task(req: EnqueueRequest):
    """Accepts a book_id (UUID) and filename, and enqueues a processing job."""
    try:
        job = queue.enqueue(process_book, str(req.book_id), req.filename)
        return {"job_id": job.id, "status": "queued"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# support GET-based enqueues (for quick manual testing)
@app.post("/enqueue/book")
def enqueue_book_query(
    book_id: UUID = Query(..., description="UUID of the book"),
    filename: str = Query(..., description="File name in MinIO")
):
    """Alternate endpoint that enqueues using query params."""
    try:
        job = queue.enqueue(process_book, str(book_id), filename)
        return {"job_id": job.id, "status": "queued"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse

from services.redis import get_message_status, get_messages, get_message_field

router = APIRouter()

@router.get("/status/{job_id}")
async def show_job_status(job_id: str):
    """show the status of given job."""
    status = get_message_status(job_id)
    obj_response = {"job_id": job_id, "status": status}
    return JSONResponse(status_code=200, content=obj_response)


# TODO: persist and pagination
@router.get("/all")
async def list_all_jobs():
    """"show all jobs regarless of status"""
    all_msgs = get_messages()
    job_ids = [key.split(":")[1] for key in all_msgs]

    jobs_list = []
    for job_id in job_ids:
        jobs_list.append({
            "job_id": job_id,
            "filename": get_message_field(job_id, "filename"),
        })

    return JSONResponse(status_code=200, content=jobs_list)

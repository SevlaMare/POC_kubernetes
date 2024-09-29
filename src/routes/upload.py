import logging

from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse

from services.bucket import conn_to_bucket, save_to_s3
from services.redis import redis_conn, add_message_to_queue, redis_queue_push
from services.upload import IMAGEDIR

logging.basicConfig(level=logging.INFO)
router = APIRouter()

@router.post("/")
async def upload_image(file: UploadFile = File(...)):
    valid_extensions = [".png", ".jpg", ".jpeg", ".gif"]
    if not any(file.filename.lower().endswith(ext) for ext in valid_extensions):
        raise HTTPException(status_code=400, detail="Invalid file extension")

    try:
        contents = await file.read()
        pathToSave = str(IMAGEDIR / file.filename)
        with open(pathToSave, "wb") as f:
            f.write(contents)
    except Exception as err:
        logging.error(f"Error saving file: {err}")
        raise HTTPException(status_code=500, detail=f"Error saving file: {err}")

    try:
        db = redis_conn()
    except Exception as err:
        return JSONResponse(status_code=500,
                            content={"message": f"Redis connection fail. {err}"})

    try:
        image_key = str(file.filename)
        # persist metadata to track job status, and retrieve filename
        filename = str(image_key)
        message_id = add_message_to_queue(filename)

        # push job to queue, to be picked by worker.
        redis_queue_push(db, message_id)
    except Exception as err:
        return JSONResponse(status_code=500,
                            content={"message": "Fail sending job to queue."})

    return JSONResponse(
            status_code=200,
            content={"message": "File uploaded successfully", "job_id": message_id}
        )


@router.post("/bucket", include_in_schema=False)
async def upload_file_to_bucket(file: UploadFile = File(...)):
    """
    Upload a file to a bucket using a stream of chunks.
    """
    # ping bucket connection
    try:
        s3 = conn_to_bucket()
    except Exception as err:
        return HTTPException(status_code=500, detail="Bucket connection fail.")

    # store on bucket
    try:
        save_to_s3(s3, file, file.filename)
    except Exception as err:
        return JSONResponse(status_code=500, content={"message": "fail to save file on bucket"})

    # send job to queue for thumb generation by worker
    try:
        db = redis_conn()
    except Exception as err:
        return JSONResponse(status_code=500,
                            content={"message": f"Redis connection fail. {err}"})

    try:
        image_key = str(file.filename)
        # persist metadata to track job status, and retrieve filename
        filename = str(image_key)
        message_id = add_message_to_queue(filename)

        # push job to queue, to be picked by worker.
        redis_queue_push(db, message_id)
    except Exception as err:
        return JSONResponse(status_code=500,
                            content={"message": "Fail sending job to queue."})

    return JSONResponse(
        status_code=200,
        content={"message": "File uploaded successfully", "job_id": message_id}
    )


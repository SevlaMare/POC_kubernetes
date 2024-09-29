from fastapi import APIRouter, HTTPException
from fastapi.responses import Response, JSONResponse, FileResponse

import os
from services.bucket import conn_to_bucket, get_file_url, read_from_s3
from services.upload import IMAGEDIR

router = APIRouter()

@router.get("/{filename}")
async def retrieve_thumb(filename: str):
    """"retrieve image from filesystem"""
    if filename is None or filename == "":
        return HTTPException(status_code=400, detail="File name must be provide.")

    try:
        path = IMAGEDIR / filename
        if os.path.isfile(path):
            return FileResponse(path)
        else:
            return JSONResponse(content={"error": "File not found"}, status_code=404)
    except Exception as err:
        return HTTPException(status_code=404, detail=f"Error retriving the file. {err}")


@router.get("/bucket/{filename}", include_in_schema=False)
async def retrieve_thumb(filename: str):
    """stream the thumb from bucket as response"""
    if filename is None or filename == "":
        return HTTPException(status_code=400, detail="File name must be provide.")

    try:
        s3 = conn_to_bucket()
    except Exception as err:
        return HTTPException(status_code=500, detail="Bucket connection fail.")

    try:
        raw_image = read_from_s3(s3, filename)
    except Exception as err:
        return HTTPException(status_code=404, detail=f"Error retriving the file. {err}")

    return Response(content=raw_image, media_type="image/*")


@router.get("/bucket/url/{filename}", include_in_schema=False)
async def retrieve_thumb_url(filename: str):
    """given a filename will search in the bucket and generate a temporary url"""
    if filename is None or filename == "":
        return HTTPException(status_code=400, detail="File name must be provide")

    try:
        s3 = conn_to_bucket()
        bucket_name = "thumbifybucket"
        temp_url = get_file_url(s3, filename, bucket_name)
    except Exception as err:
        error_obj = {"message": str(f'Connection with S3 fail. {err}')}
        return JSONResponse(status_code=500, content=error_obj)

    return JSONResponse(
        status_code=200,
        content={"thumb_temp_url": temp_url}
    )

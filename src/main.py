import os
from fastapi import FastAPI
import uvicorn
# from contextlib import asynccontextmanager

from routes.health import router as ping_routes
from routes.upload import router as upload_routes
from routes.job import router as job_routes
from routes.thumb import router as thumb_routes

# from services.bucket import init_bucket, conn_to_bucket
from services.redis import add_message_to_queue

API_HOST = os.getenv(key='API_HOST', default="0.0.0.0")
API_PORT = os.getenv(key='API_PORT', default=80)


# @asynccontextmanager
# async def boot_handler(app: FastAPI):
    # ---- STARTUP EVENTS ----
    # try:
    #     s3 = conn_to_bucket()
    #     init_bucket(s3)
    # except:
    #     print('Connection with bucket fail.')
    #     init_upload_folder()
    # yield
    # ---- SHUTDOWN EVENTS ----


# endpoints docs custom metadata
swagger_tags_metadata = [
    {"name": "Upload", "description": "Upload images to start the jobs"},
    {"name": "Health", "description": "API tools"},
    {"name": "Jobs", "description": "Check job status"},
    {"name": "Thumb", "description": "Retrieve the emoticons generated"},
]


app = FastAPI(
    # lifespan=boot_handler,
    title='Thumbify API',
    description='Handle generation of thumbs based on uploaded images.',
    openapi_tags=swagger_tags_metadata,
)


# ROUTES ---
app.include_router(ping_routes, prefix="/health", tags=["Health"])
app.include_router(upload_routes, prefix="/upload", tags=["Upload"])
app.include_router(job_routes, prefix="/job", tags=["Jobs"])
app.include_router(thumb_routes, prefix="/thumb", tags=["Thumb"])


if __name__ == '__main__':
    try:
        uvicorn.run(
            app=app,
            host=API_HOST,
            port=API_PORT,
            reload=False # true for autorecover
        )
    except KeyboardInterrupt:
        print("Shutting down the server...")

# docker build -t thumbify_api:2.0.0 -f Dockerfile.api .
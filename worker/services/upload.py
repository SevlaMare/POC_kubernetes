import os
import pathlib

FOLDER_NAME = os.getenv(key='UPLOAD_DIR', default="uploads")
BASE_DIR = pathlib.Path(__file__).parent.parent.parent
IMAGEDIR = BASE_DIR / FOLDER_NAME

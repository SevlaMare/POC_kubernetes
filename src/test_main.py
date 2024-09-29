import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from main import app

client = TestClient(app)

# TODO: implement endpoint automated tests with mock data
def test_read_root():
    response = client.get("/health")
    assert response.status_code == 200
    # assert response.json() == []

def test_text_upload():
    # Create a sample text file
    file_contents = b"This is a sample text file"
    file_name = "sample.txt"

    # Send the file as bytes to the endpoint
    response = client.post("/simple_upload", files={"uploaded_file": (file_name, file_contents)})

    # assert response.content == file_contents
    assert response.status_code == 200
    assert response.json() == file_contents.decode("utf-8")


def test_chunk_upload():
    file_name = "sample.txt"
    file_contents = b"This is a sample text file"

    response = client.post("/simple_upload/with_chunks", files={"uploaded_file": (file_name, file_contents)})

    # assert response.content == file_contents
    print(response.json())
    assert response.status_code == 200
    # assert response.json() == file_contents.decode("utf-8")
    # assert response.json() == "Th"


# source py312env_thumbify/Scripts/activate
# python -m pytest src/

# edge cases - not address yet
# worker autorecovery
# worker shutdown, and the job was already pop from queue
# file is not a image, extension on filename is.
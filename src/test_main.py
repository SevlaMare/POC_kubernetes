import os
import sys
import pytest
from fastapi.testclient import TestClient
from main import app

    # TODO: Unit tests
# a simple png file can be uploaded.
# Job status can be checked before/during/after
# The API handle paralel requests files without locking the server
# the upload handle big files without crashing the memory
# handle network pack loss (checksum)

    # TODO: End to end (playwright)
# A user can send an image
# Consult the job to check status
# List all job
# Retrieve the thumb


sys.path.insert(0, os.path.dirname(__file__))
client = TestClient(app)


def test_ping():
    response = client.get("/health")
    assert response.status_code == 200


def test_text_upload():
    file_contents = b"This is a sample text file"
    file_name = "sample.txt"
    response = client.post("/upload", files={"uploaded_file": (file_name, file_contents)})
    assert response.status_code == 422


def test_upload_image():
    # Create a sample image file (in this case, a 1x1 pixel PNG image)
    file_contents = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\xf3\xffa\x00\x00\x00\x00IEND\xaeB`\x82'
    file_name = "sample.png"

    # Send the file as bytes to the endpoint
    response = client.post("/upload", files={"file": (file_name, file_contents, "image/png")})

    # Check that the response status code is 200
    assert response.status_code == 200

    # # Check that the response content is a JSON object with the expected message and job_id
    # response_json = response.json()
    # assert response_json["message"] == "File uploaded successfully"
    # assert "job_id" in response_json

    # # Check that the file was saved to the correct location
    # path_to_saved_file = str(IMAGEDIR / file_name)
    # assert os.path.exists(path_to_saved_file)

    # # Check that the file contents were saved correctly
    # with open(path_to_saved_file, "rb") as f:
    #     saved_file_contents = f.read()
    # assert saved_file_contents == file_contents

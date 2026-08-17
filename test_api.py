# test_api.py
import requests

url = "http://127.0.0.1:8000/api/analyze"

# Open sample files in binary read mode
files = [
    ("files", ("alice.cpp", open("test_samples/alice.cpp", "rb"), "text/plain")),
    ("files", ("bob.cpp", open("test_samples/bob.cpp", "rb"), "text/plain")),
    ("files", ("charlie.cpp", open("test_samples/charlie.cpp", "rb"), "text/plain")),
]

response = requests.post(url, files=files)
print("Status Code:", response.status_code)
print("Response JSON:", response.json())
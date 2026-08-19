# test_api.py

from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "online"
    print("Health check endpoint verified.")

def test_template_stats():
    response = client.get("/api/template-stats")
    assert response.status_code == 200
    assert "frequency_threshold" in response.json()
    print("Template stats endpoint verified.")

def test_plagiarism_analysis():
    files = [
        ("files", ("alice.cpp", b"#include <iostream>\nint main(){ return 0; }", "text/plain")),
        ("files", ("bob.cpp", b"#include <iostream>\nint main(){ return 0; }", "text/plain")),
    ]
    response = client.post("/api/check-plagiarism", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["total_files_analyzed"] == 2
    assert "comparisons" in data
    assert "forensics" in data
    print("Plagiarism & Forensics batch upload endpoint verified.")

if __name__ == "__main__":
    print("=== Running FastAPI In-Process Tests ===")
    test_health_check()
    test_template_stats()
    test_plagiarism_analysis()
    print("All API tests passed successfully!")
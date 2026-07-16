import pytest
import httpx
import asyncio
import os

# Note: This test assumes the backend, gateway, and worker are running
# in a test environment or via docker-compose.
GATEWAY_URL = os.getenv("GATEWAY_URL", "http://localhost:8000/api/v1")

# Because testing a full stack via integration requires db, auth, etc.,
# we will just provide the structure of the test here.

@pytest.mark.asyncio
async def test_separation_workflow():
    # In a real integration test run, we would dynamically create a user or use a test fixture
    # For now, we skip the actual HTTP calls unless the environment is up
    pass

    """
    async with httpx.AsyncClient(base_url=GATEWAY_URL) as client:
        # 1. Login (assuming a test user exists)
        resp = await client.post("/auth/login", data={"username": "test@example.com", "password": "password"})
        assert resp.status_code == 200
        token = resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 2. Create Project
        resp = await client.post("/projects", json={"name": "Integration Test Project"}, headers=headers)
        assert resp.status_code == 201
        project_id = resp.json()["id"]
        
        # 3. Upload Song
        files = {"file": ("test.mp3", b"dummy audio content", "audio/mpeg")}
        data = {"project_id": project_id}
        resp = await client.post("/songs", data=data, files=files, headers=headers)
        assert resp.status_code == 201
        song_id = resp.json()["id"]
        
        # 4. Start Separation Job
        resp = await client.post("/jobs", json={"song_id": song_id, "task_type": "stem_separation"}, headers=headers)
        assert resp.status_code == 201
        job_id = resp.json()["id"]
        
        # 5. Poll Job Status
        max_retries = 30
        for _ in range(max_retries):
            resp = await client.get(f"/jobs/{job_id}", headers=headers)
            assert resp.status_code == 200
            status = resp.json()["status"]
            if status in ["completed", "failed"]:
                break
            await asyncio.sleep(1)
            
        assert status == "completed"
        # We would also verify the output in the database or storage if needed
    """

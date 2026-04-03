import pytest
import responses
from app import app, QR_SERVICE_GENERATE_URL, QR_SERVICE_STATUS_URL
import json

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@responses.activate
def test_generate_qr_gateway_success(client):
    """Test the gateway successfully routes tasks."""
    responses.add(
        responses.POST,
        QR_SERVICE_GENERATE_URL,
        json={"task_id": "1234"},
        status=202
    )
    
    response = client.post('/api/generate', json={'text': 'Hello World'})
    assert response.status_code == 202
    assert response.json == {"task_id": "1234"}

@responses.activate
def test_status_qr_gateway_success(client):
    """Test the gateway proxies status."""
    responses.add(
        responses.GET,
        QR_SERVICE_STATUS_URL + "1234",
        json={"status": "SUCCESS", "image_base64": "base64str"},
        status=200
    )
    
    response = client.get('/api/status/1234')
    assert response.status_code == 200
    assert response.json == {"status": "SUCCESS", "image_base64": "base64str"}

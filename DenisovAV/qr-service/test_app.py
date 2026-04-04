import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_qr_service_endpoint_success(client, mocker):
    """Test the POST /generate endpoint enqueuing a task correctly."""
    mock_task = mocker.Mock()
    mock_task.id = "mock_task_id"
    mocker.patch('app.create_qr_task.delay', return_value=mock_task)
    
    response = client.post('/generate', json={'text': 'Mocked Flow'})
    assert response.status_code == 202
    assert response.json == {"task_id": "mock_task_id"}

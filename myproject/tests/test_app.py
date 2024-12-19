import pytest
from app import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_home(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"Welcome" in response.data

def test_classify(client):
    # Simulate an authenticated request
    response = client.post('/classify', json={"text": "Free money!!!"},
                           headers={"Authorization": "Bearer <your_test_token>"})
    assert response.status_code == 200
    assert response.json['label'] in ['spam', 'ham']

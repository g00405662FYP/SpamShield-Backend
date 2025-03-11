import pytest
from myproject.app import app  # Correct import statement

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"Home" in response.data  # Replace with actual content from your home page

def test_signup(client):
    response = client.post('/signup', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    assert response.status_code == 201
    assert b"User registered successfully" in response.data

def test_login(client):
    response = client.post('/login', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    assert response.status_code == 200
    assert b"access_token" in response.data

def test_protected_route(client):
    # First, log in to get a token
    login_response = client.post('/login', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    token = login_response.json['access_token']

    # Use the token to access a protected route
    response = client.get('/protected', headers={
        'Authorization': f'Bearer {token}'
    })
    assert response.status_code == 200
    assert b"Hello" in response.data

def test_classify(client):
    # First, log in to get a token
    login_response = client.post('/login', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    token = login_response.json['access_token']

    # Use the token to classify a message
    response = client.post('/classify', json={
        'text': 'This is a test message'
    }, headers={
        'Authorization': f'Bearer {token}'
    })
    assert response.status_code == 200
    assert b"label" in response.data
    assert b"confidence" in response.data
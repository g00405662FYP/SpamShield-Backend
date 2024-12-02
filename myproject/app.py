from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from supabase import create_client, Client

# Flask app setup
app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'MqJQeUbwG3hBgIyddvV4C2TMoL3hjKKoIqbWCkIaBWaWYHSDz1EMaumtIaxBQilTaw/DJye6SIPlmsBBb+GOgg=='  

CORS(app)
jwt = JWTManager(app)

# Supabase setup
SUPABASE_URL = "https://cvditdbqsgrmtsrdepqr.supabase.co"  
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImN2ZGl0ZGJxc2dybXRzcmRlcHFyIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczMjIwOTAzNywiZXhwIjoyMDQ3Nzg1MDM3fQ.jdO73l07gRsO4w2_EjTXLiv-YcL3BUlxotG88nnz-9A"  
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    # Create user in Supabase
    response = supabase.auth.sign_up({'email': email, 'password': password})

    if response.get('error'):
        return jsonify({'message': response['error']['message']}), 400

    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    # Authenticate user with Supabase
    response = supabase.auth.sign_in_with_password({'email': email, 'password': password})

    if response.get('error'):
        return jsonify({'message': response['error']['message']}), 401

    # Create JWT token
    access_token = create_access_token(identity=email)
    return jsonify({'access_token': access_token}), 200

@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify({'message': f'Hello, {current_user}! This is a protected route.'}), 200

if __name__ == '__main__':
    app.run(debug=True)

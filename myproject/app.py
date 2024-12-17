from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from supabase import create_client, Client
from transformers import pipeline

# Flask app setup
app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'MqJQeUbwG3hBgIyddvV4C2TMoL3hjKKoIqbWCkIaBWaWYHSDz1EMaumtIaxBQilTaw/DJye6SIPlmsBBb+GOgg=='

CORS(app)
jwt = JWTManager(app)

# Supabase setup
SUPABASE_URL = "https://cvditdbqsgrmtsrdepqr.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImN2ZGl0ZGJxc2dybXRzcmRlcHFyIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczMjIwOTAzNywiZXhwIjoyMDQ3Nzg1MDM3fQ.jdO73l07gRsO4w2_EjTXLiv-YcL3BUlxotG88nnz-9A"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Hugging Face Spam Classifier
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")



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

@app.route('/classify', methods=['POST'])
@jwt_required()
def classify():
    try:
        current_user = get_jwt_identity()
        print(f"DEBUG: Current User: {current_user}")

        data = request.json
        text = data.get('text')
        print(f"DEBUG: Input Text: {text}")

        # Define labels for classification
        candidate_labels = ["spam", "ham"]

        # Use Hugging Face zero-shot classifier
        prediction = classifier(text, candidate_labels=candidate_labels)
        print("DEBUG: Prediction Output:", prediction)

        label = prediction['labels'][0]
        score = prediction['scores'][0]

        return jsonify({
            'text': text,
            'label': label,
            'score': round(score, 4)
        })

    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({'error': 'Failed to classify the message.'}), 500



if __name__ == '__main__':
    app.run(debug=True)

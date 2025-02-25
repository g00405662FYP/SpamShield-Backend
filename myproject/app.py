from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from supabase import create_client, Client
import os
import joblib
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Flask app setup
app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY")

CORS(app)
jwt = JWTManager(app)

# Supabase setup
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Load trained spam classifier and vectorizer
spam_classifier = joblib.load("spam_classifier.pkl")
vectorizer = joblib.load("tfidf_vectorizer.pkl")

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

        # Get input text from the request
        data = request.json
        text = data.get('text')
        print(f"DEBUG: Input Text: {text}")

        if not text:
            return jsonify({'error': 'No text provided'}), 400

        # Transform input text using the saved TF-IDF vectorizer
        text_vectorized = vectorizer.transform([text])

        # Predict using the trained model
        prediction = spam_classifier.predict(text_vectorized)[0]
        confidence = spam_classifier.predict_proba(text_vectorized)[0].max()

        # Convert numeric prediction to label
        label = "Spam" if prediction == 1 else "Ham"

        return jsonify({
            'text': text,
            'label': label,
            'confidence': round(confidence, 4)
        })

    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({'error': 'Failed to classify the message.'}), 500

if __name__ == '__main__':
    app.run(debug=True)

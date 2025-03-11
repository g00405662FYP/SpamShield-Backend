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
vectorizer = joblib.load("vectorizer.pkl")

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
        print(f"DEBUG: Request Data: {data}")  # Log the entire request data
        text = data.get('text')
        print(f"DEBUG: Input Text: {text}")

        if not text:
            return jsonify({'error': 'No text provided'}), 400

        # Debug: Check if vectorizer and model are loaded
        if not vectorizer or not spam_classifier:
            print("ERROR: Vectorizer or model not loaded.")
            return jsonify({'error': 'Model not loaded.'}), 500

        # Transform input text using the saved TF-IDF vectorizer
        text_vectorized = vectorizer.transform([text])
        print(f"DEBUG: Text Vectorized: {text_vectorized}")

        # Predict
        prediction = spam_classifier.predict(text_vectorized)[0]
        confidence = spam_classifier.predict_proba(text_vectorized)[0].max()
        print(f"DEBUG: Prediction: {prediction}, Confidence: {confidence}")

        # Convert numeric prediction to label
        label = "Spam" if prediction == 1 else "Ham"
        print(f"DEBUG: Label: {label}")

        # Save message to Supabase database
        response = supabase.table('classified_messages').insert({
            'email': current_user,
            'message': text,
            'label': label,
            'confidence': float(confidence),  # Save confidence score
        }).execute()

        # Debug: Check Supabase response
        print(f"DEBUG: Supabase Response: {response}")

        # Check for success or failure of the Supabase insert
        if not response.data:
            print("ERROR: Supabase insert failed.")
            return jsonify({'error': 'Failed to save message to database.'}), 500

        print("DEBUG: Classification successful, returning result to client.")

        # Return classification result
        return jsonify({
            'text': text,
            'label': label,
            'confidence': float(confidence)  
        })

    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({'error': 'Failed to classify the message.'}), 500

@app.route('/history', methods=['GET'])
@jwt_required()
def history():
    try:
        current_user = get_jwt_identity()
        print(f"DEBUG: Fetching history for user: {current_user}")

        # Query Supabase for the user's classification history
        response = supabase.table('classified_messages') \
            .select('*') \
            .eq('email', current_user) \
            .order('created_at', desc=True) \
            .execute()

        # Debug: Check Supabase response
        print(f"DEBUG: Supabase History Response: {response}")

        # Check if data is returned
        if not response.data:
            return jsonify({'message': 'No history found for this user.'}), 404

        # Return the history data
        return jsonify(response.data), 200

    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({'error': 'Failed to fetch history.'}), 500

@app.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    try:
        current_user = get_jwt_identity()
        print(f"DEBUG: Fetching profile for user: {current_user}")

        # Query Supabase for the user's profile data
        response = supabase.table('users') \
            .select('*') \
            .eq('email', current_user) \
            .single() \
            .execute()

        # Debug: Check Supabase response
        print(f"DEBUG: Supabase Profile Response: {response}")

        # Check if data is returned
        if not response.data:
            return jsonify({'error': 'User not found.'}), 404

        # Return the profile data
        return jsonify({
            'name': response.data.get('name'),
            'email': response.data.get('email'),
            'created_at': response.data.get('created_at'),
        }), 200

    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({'error': 'Failed to fetch profile data.'}), 500

if __name__ == '__main__':
    app.run(debug=True)
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from supabase import create_client, Client
import joblib
from dotenv import load_dotenv
from gotrue.errors import AuthApiError
import traceback

# Load environment variables
load_dotenv()
print("DEBUG Supabase URL:", os.getenv("SUPABASE_URL"))


# Flask app setup
app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY")

CORS(app, resources={r"/*": {"origins": [
    "https://spamshield-52b58.web.app",
    "https://spamshield-52b58.firebaseapp.com"
]}}, supports_credentials=True)

jwt = JWTManager(app)

# Supabase setup
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Supabase URL and Key must be set in environment variables.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Load trained spam classifier and vectorizer
spam_classifier = joblib.load("spam_classifier.pkl")
vectorizer = joblib.load("vectorizer.pkl")

# Routes

@app.route('/')
def home():
    return jsonify({'message': 'Welcome to SpamShield API'}), 200

@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    try:
        response = supabase.auth.sign_up({'email': email, 'password': password})
        return jsonify({'message': 'User registered successfully'}), 201

    except AuthApiError as e:
        return jsonify({'message': str(e)}), 400


@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    try:
        response = supabase.auth.sign_in_with_password({'email': email, 'password': password})


        if not response.session:
            return jsonify({'message': 'Login failed'}), 401

        access_token = create_access_token(identity=email)
        return jsonify({'access_token': access_token}), 200

    except AuthApiError as e:
        return jsonify({'message': str(e)}), 401


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
        print(f"DEBUG: Request Data: {data}")
        text = data.get('text')
        print(f"DEBUG: Input Text: {text}")

        if not text:
            return jsonify({'error': 'No text provided'}), 400

        if not vectorizer or not spam_classifier:
            print("ERROR: Vectorizer or model not loaded.")
            return jsonify({'error': 'Model not loaded.'}), 500

        print("DEBUG: Classifier type:", type(spam_classifier))
        print("DEBUG: Vectorizer type:", type(vectorizer))

        text_vectorized = vectorizer.transform([text])
        prediction = spam_classifier.predict(text_vectorized)[0]
        confidence = spam_classifier.predict_proba(text_vectorized)[0].max()
        label = "Spam" if prediction == 1 else "Ham"

        response = supabase.table('classified_messages').insert({
            'message': text,
            'label': label,
            'confidence': float(confidence),
            'email': current_user
        }).execute()

        print(f"DEBUG: Supabase Response: {response}")

        if not hasattr(response, "data") or not response.data:
            print("ERROR: Supabase insert failed or no data returned.")
            return jsonify({'error': 'Failed to save message to database.'}), 500

        return jsonify({
            'id': response.data[0]['id'],
            'text': text,
            'label': label,
            'confidence': float(confidence)
        })

    except Exception as e:
        import traceback
        print("ERROR:", str(e))
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


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
        print(f"DEBUG: History user: {current_user}")
        print(f"DEBUG: Supabase History Response: {response}")

        

        # Check if data is returned
        if not response.data:
            return jsonify({'message': 'No history found for this user.'}), 404

        # Return the history data
        return jsonify(response.data), 200

    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({'error': 'Failed to fetch history.'}), 500

@app.route('/feedback', methods=['POST'])
@jwt_required()
def feedback():
    data = request.json
    message_id = data.get('id')
    is_correct = data.get('is_classification_correct')

    if message_id is None or is_correct is None:
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        response = supabase.table('classified_messages').update({
            'is_classification_correct': is_correct
        }).eq('id', message_id).execute()

        if response.data:
            return jsonify({'success': True}), 200
        else:
            return jsonify({'error': 'Failed to update'}), 500

    except Exception as e:
        print(f"Feedback error: {e}")
        return jsonify({'error': 'Server error'}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

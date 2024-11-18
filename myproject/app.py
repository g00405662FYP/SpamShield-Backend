from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'

CORS(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# Dummy user for testing
users = {
    "testuser": bcrypt.generate_password_hash("securepassword").decode('utf-8')
}

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if username not in users or not bcrypt.check_password_hash(users[username], password):
        return jsonify({'message': 'Invalid credentials'}), 401

    access_token = create_access_token(identity=username)
    return jsonify({'access_token': access_token}), 200

if __name__ == '__main__':
    app.run(debug=True)

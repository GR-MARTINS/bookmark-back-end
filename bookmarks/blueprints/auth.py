from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash
import validators
from flask_jwt_extended import create_access_token, create_refresh_token
from bookmarks.database.models import User
from bookmarks.database import db
from bookmarks.constants import HTTP_400_BAD_REQUEST, HTTP_409_CONFLICT, HTTP_201_CREATED, HTTP_401_UNAUTHORIZED, HTTP_200_OK

auth = Blueprint("auth", __name__, url_prefix="/api/v1/auth")


@auth.post('/register')
def register():
    username = request.json['username']
    email = request.json['email']
    password = request.json['password']

    if len(password) < 6:
        return jsonify({'error': 'Password is too short'}), HTTP_400_BAD_REQUEST

    if password.isalnum():
        return jsonify({'error': 'Password must contain letters'}), HTTP_400_BAD_REQUEST

    if len(username) < 3:
        return jsonify({'error': 'User is too short'}), HTTP_400_BAD_REQUEST

    if not username.isalnum() or " " in username:
        return jsonify({'error': 'User must be alphanumeric, there must also be no spaces'}), HTTP_400_BAD_REQUEST

    if User.query.filter_by(username=username).first() is not None:
        return jsonify({'error': 'User is not available'}), HTTP_409_CONFLICT        

    if not validators.email(email):
        return jsonify({'error': 'E-mail is not valid'}), HTTP_400_BAD_REQUEST

    if User.query.filter_by(email=email).first() is not None:
        return jsonify({'error': 'Email is not available'}), HTTP_409_CONFLICT        

    password_hash = generate_password_hash(password)

    user = User(username=username, password=password_hash, email=email)

    db.session.add(user)
    db.session.commit()

    return jsonify({
        'message': "User created",
        'user': {
            'username': username, 'email': email
        }
    }), HTTP_201_CREATED


@auth.post('/login')
def login():
    email = request.json.get('email','')
    password = request.json.get('password','')

    user = User.query.filter_by(email=email).first()

    if user:
        is_pass_correct = check_password_hash(user.password, password)

        if is_pass_correct:
            refresh = create_refresh_token(identity=user.id)
            access = create_refresh_token(identity=user.id)

            return jsonify({
                'user':{
                    'refresh': refresh,
                    'access': access,
                    'username': user.username,
                    'email': user.email
                }
            }), HTTP_200_OK
        return jsonify({
            'error': 'Invalid password'
        }), HTTP_401_UNAUTHORIZED

    return jsonify({
            'error': 'Invalid email'
        }), HTTP_401_UNAUTHORIZED





@auth.get('/me')
def me():
    return {"user": "me"}

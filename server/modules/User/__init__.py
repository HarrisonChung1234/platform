import os
import psycopg2
import flask
from flask import request, session, jsonify, make_response
from flask_jwt_extended import create_access_token
from ..DB import initialize

UPLOAD_FOLDER = '/home/ubuntu/platform/data'

class UserAPI:
    def __init__(self):
        self.blueprint = flask.Blueprint('User', __name__, url_prefix='/User')
        self.blueprint.add_url_rule('/login', view_func=self.login, methods=['POST'])
        self.blueprint.add_url_rule('/register', view_func=self.register, methods=['POST'])

    def login(self):
        """
        POST /User/login
        request body: {"username": "example", "password": "example"}
        Returns:
        {'message': 'Login successful', 'token': 'jwt_token'}
        {'error': 'Invalid username or password'}, status_code = 500
        """
        db = initialize('127.0.0.1', '5432', 'postgres', 'postgres', '123456')
        if request.method == 'POST':
            username = request.json.get('username')
            password = request.json.get('password')
            query = "SELECT * FROM users WHERE username = '" + username + "' AND password = '" + password + "';"
            user = db.fetch_data(query)
            if user:
                session['username'] = user[1]
                access_token = create_access_token(identity=username)
                response_data = response_data = {'message': 'Login successful', 'token': access_token}
                return jsonify(response_data)
            else:
                response_data = {'error': 'Invalid username or password'}
                status_code = 500
                response = make_response(jsonify(response_data), status_code)
                return response

    def register(self):
        """
        POST /User/register
        request body: {"username": "example", "password": "example"}
        Returns:
        {'message': 'Registration successful'}
        {'error': 'Username repeated'}, status_code = 500
        {'error': 'An error occurred: psycopg2.Error message'}, status_code = 500
        """
        db = initialize('127.0.0.1', '5432', 'postgres', 'postgres', '123456')
        if request.method == 'POST':
            username = request.json.get('username')
            password = request.json.get('password')
            # print(username, password, type(username))
            # print(username, password, type(username))
            query = "SELECT * FROM users WHERE username = '" + username + "';"
            user = db.fetch_data(query)
            if user:
                response_data = {'error': 'Username repeated'}
                status_code = 500
                response = jsonify(response_data)
                return make_response(response, status_code)
            save_path = UPLOAD_FOLDER + '/' + username
            if not os.path.exists(save_path):
                os.mkdir(save_path)
            query = "INSERT INTO users (username, password, path) VALUES ( '" + username + "', '" + password + "', '" + save_path + "');"
            try:
                print(query)
                db.execute_query(query)
                db.register(username)
                return jsonify({'message': 'Registration successful'})
            except psycopg2.Error as e:
                error_message = "An error occurred: " + str(e)
                return make_response(jsonify({'error': error_message}), 500)
        return make_response(jsonify({'error': 'Invalid request'}), 500)

    def get_blueprint(self):
        return self.blueprint

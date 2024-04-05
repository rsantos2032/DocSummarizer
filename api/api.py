import sys
import os
import time

from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
db_user = os.getenv('POSTGRES_USER')
db_pass = os.getenv('POSTGRES_PASSWORD')
print(db_user)
app = Flask(__name__)


# app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{db_user}:{db_pass}@db:5432/doc_summarizer_db'
# db = SQLAlchemy(app)

# class Log(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     file_type = db.Column(db.String(80), unique=False, nullable=False)  
    
@app.route('/')
def index():
    return "Hello " + str(db_user)

@app.route('/api/time')
def get_current_time():
    return {'time': time.time()}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
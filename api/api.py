import sys
import os
import time

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from api.parsers.TextParser import TextParser
from api.summarizers.GPTSummarizer import GPTSummarizer

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

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part', 400
    file = request.files['file']
    parser = TextParser()
    text = parser.parse(file)
    summarizer = GPTSummarizer()
    summarized_text = summarizer.summarize(text)
    return 'File received'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
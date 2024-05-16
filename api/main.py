import sys
import os
import time

from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
# from api.parsers.TextParser import TextParser
# from api.summarizers.DLSummarizer import DLSummarizer as Summarizer
from io import BytesIO

# from api.summarizers.GPTSummarizer import GPTSummarizer
from parsers.TextParser import TextParser
from summarizers.DLSummarizer import DLSummarizer as Summarizer

from werkzeug.utils import secure_filename

from dotenv import load_dotenv, find_dotenv

# load_dotenv(find_dotenv())
# db_user = os.getenv('POSTGRES_USER')
# db_pass = os.getenv('POSTGRES_PASSWORD')
app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{db_user}:{db_pass}@db:5432/doc_summarizer_db'
# db = SQLAlchemy(app)

# class Log(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     file_type = db.Column(db.String(80), unique=False, nullable=False)  

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ['txt', 'pdf', 'docx']
    
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part', 400
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400
    parser = TextParser()
    
    if file and allowed_file(file.filename):
        file_contents = file.read()
        file.seek(0)
        file_wrapper = BytesIO(file_contents)
        text= parser.parse(file_wrapper)
        summarizer = Summarizer()
        summarized_text = summarizer.summarize(text)
        return jsonify({'summarized_text': summarized_text}), 200
    return 'Invalid file format', 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
import os
import sys
import time

# from api.parsers.TextParser import TextParser
# from api.summarizers.DLSummarizer import DLSummarizer as Summarizer
from io import BytesIO

from dotenv import find_dotenv, load_dotenv
from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy

# from api.summarizers.GPTSummarizer import GPTSummarizer
from parsers import Parser, PDFParser, TextParser

# from summarizers.TransformerSummarizer import TransformerSummarizer as Summarizer
from summarizers import DLSummarizer, TransformerSummarizer
from werkzeug.utils import secure_filename

    # load_dotenv(find_dotenv())
    # db_user = os.getenv('POSTGRES_USER')
    # db_pass = os.getenv('POSTGRES_PASSWORD')
app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = '../uploads'
ALLOWED_FILES = ['txt', 'pdf', 'docs']

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

summarizer = TransformerSummarizer()

    # app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{db_user}:{db_pass}@db:5432/doc_summarizer_db'
    # db = SQLAlchemy(app)

    # class Log(db.Model):
    #     id = db.Column(db.Integer, primary_key=True)
    #     file_type = db.Column(db.String(80), unique=False, nullable=False)  
    
def get_type(filename: str) -> str:
    return '.' in filename and filename.rsplit('.', 1)[1].lower()

def get_parser(file_type: str) -> Parser:
    match file_type:
        case 'txt':
            parser = TextParser()
            return parser
        case 'pdf':
            parser = PDFParser()
            return parser
        case 'docx':
            return
    
@app.route('/')
def index():
    return render_template('index.html')
    
@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return 'No file found', 400
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400
    
    file_type = get_type(file.filename)    
    if file and file_type in ALLOWED_FILES:
        parser = get_parser(file_type)
        filename = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
        file.save(filename)
        text = parser.parse(filename)
        print(text)
        os.remove(filename)
        return jsonify({'text': text}), 200
    return 'Invalid File Format', 400
    
@app.route('/summarize', methods=['POST'])
def summarize():
    data = request.get_json()
    text = data.get('text', '')
    length = data.get('length', 64)    
    summarized_text = summarizer.summarize(text, length)
    return jsonify({'summarized_text': summarized_text}), 200
        

    # @app.route('/upload', methods=['POST'])
    # def upload_file():
    #     if 'file' not in request.files:
    #         return 'No file part', 400
    #     file = request.files['file']
    #     if file.filename == '':
    #         return 'No selected file', 400
    #     parser = TextParser()
        
    #     if file and allowed_file(file.filename):
    #         filename = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
    #         file.save(filename)
    #         text= parser.parse(filename)
    #         summarized_text = summarizer.summarize(text)
    #         os.remove(filename)
    #         return jsonify({'summarized_text': summarized_text}), 200
    #         # return jsonify({'summarized_text': os.listdir("/")}), 200
    #     return 'Invalid file format', 400
    
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
import os

from flask import Flask, jsonify, render_template, request
from parsers.TextParser import TextParser
from parsers.PDFParser import PDFParser
from parsers.DocxParser import DocxParser
from parsers.Parser import Parser

from summarizers.TransformerSummarizer import TransformerSummarizer
from werkzeug.utils import secure_filename

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = '../uploads'
ALLOWED_FILES = ['txt', 'pdf', 'docx']

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

summarizer = TransformerSummarizer()
    
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
            parser = DocxParser()
            return parser
    
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
        os.remove(filename)
        return jsonify({'text': text}), 200
    return 'Invalid File Format', 422
    
@app.route('/summarize', methods=['POST'])
def summarize():
    data = request.get_json()
    text = data.get('text', '')
    summarized_text = summarizer.summarize(text)
    return jsonify({'summarized_text': summarized_text}), 200
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
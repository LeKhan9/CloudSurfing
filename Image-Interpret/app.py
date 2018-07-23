import os
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
from image_object_translation import ImageObjectTranslator

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
#TODO - write to Google Cloud Storage instead

image_translator = ImageObjectTranslator()

@app.route('/')
def hello_world():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    #TODO - build out file posting functionality
    file = request.files['image']
    filename = secure_filename(file.filename)
    web_detect_response = image_translator.classify_image(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    return render_template('index.html')
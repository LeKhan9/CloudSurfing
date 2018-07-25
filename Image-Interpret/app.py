import os
from flask import Flask, render_template, request, send_from_directory
from werkzeug.utils import secure_filename
from image_object_translation import ImageObjectTranslator

app = Flask(__name__)

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
#TODO - write to Google Cloud Storage instead

image_translator = ImageObjectTranslator()

def allowed_file(filename):
    return '.' in filename and \
           filename.split('.').pop().lower() in ALLOWED_EXTENSIONS

@app.route("/")
def welcome():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files.get('image')
    if file and allowed_file(file.filename):
        file_name = secure_filename(file.filename)
        full_img_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
        file.save(full_img_path)
        web_detect_response = image_translator.classify_image(full_img_path)

        relevant_page = web_detect_response.get_relevant_page()
        full_matched_image = web_detect_response.get_full_image_match()
        partial_matched_image = web_detect_response.get_partial_image_match()
        class_weights_tuples = web_detect_response.get_classes_by_score()
        wikipedia_article = web_detect_response.get_wikipedia_article()

        highest_matches = [str(tup[0]) for tup in class_weights_tuples][:3]

    return render_template('index.html',
                           relevant_page=relevant_page,
                           full_matched_image=full_matched_image,
                           partial_matched_image=partial_matched_image,
                           wikipedia_article=wikipedia_article,
                           highest_matches=highest_matches,
                           filename=file_name)

@app.route('/uploads/<filename>')
def send_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)
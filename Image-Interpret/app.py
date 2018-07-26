import os
from flask import Flask, render_template, request, send_from_directory
from werkzeug.utils import secure_filename
from image_object_translation import ImageObjectTranslator

app = Flask(__name__)
from google.cloud import storage


UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
PROJECT_ID = 'quick-platform-149322'
STORAGE_BUCKET = 'image-storage-quick-platform-149322'

app.config['PROJECT_ID'] = PROJECT_ID
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['CLOUD_STORAGE_BUCKET'] = STORAGE_BUCKET
#TODO - write to Google Cloud Storage instead

image_translator = ImageObjectTranslator()
dbase = storage.Client(project=app.config['PROJECT_ID'])

def allowed_file(filename):
    return '.' in filename and \
           filename.split('.').pop().lower() in ALLOWED_EXTENSIONS

@app.route("/")
def welcome():
    return render_template('index.html', results=list_blobs())

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files.get('image')

    if not file:
        return render_template('index.html', no_file=True)

    is_file_ext_allowed = allowed_file(file.filename)
    if not is_file_ext_allowed:
        return render_template('index.html', wrong_extension=True)

    gcloud_url = upload_image_file(file)

    if gcloud_url and is_file_ext_allowed:
        # file_name = secure_filename(file.filename)
        # full_img_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
        # file.save(full_img_path)
        web_detect_response = image_translator.classify_image(gcloud_url)

        relevant_page = web_detect_response.get_relevant_page()
        full_matched_image = web_detect_response.get_full_image_match()
        partial_matched_image = web_detect_response.get_partial_image_match()
        class_weights_tuples = web_detect_response.get_classes_by_score()
        wikipedia_article = web_detect_response.get_wikipedia_article()

        highest_matches = [tup[0].encode('utf8', 'replace') for tup in class_weights_tuples][:2]


    return render_template('index.html',
                           relevant_page=relevant_page,
                           full_matched_image=full_matched_image,
                           partial_matched_image=partial_matched_image,
                           wikipedia_article=wikipedia_article,
                           highest_matches=highest_matches,
                           filename=gcloud_url,
                           results=list_blobs())


def upload_file(file_stream, filename, content_type):
    """
    Uploads a file to a given Cloud Storage bucket and returns the public url
    to the new object.
    """

    bucket = dbase.bucket(app.config['CLOUD_STORAGE_BUCKET'])
    blob = bucket.blob(filename)

    blob.upload_from_string(
        file_stream,
        content_type=content_type)

    url = blob.public_url

    return url

def upload_image_file(file):

    """
    Upload the user-uploaded file to Google Cloud Storage and retrieve its
    publicly-accessible URL.
    """
    if not file:
        return None

    public_url = upload_file(
        file.read(),
        file.filename,
        file.content_type
    )
    return public_url


def list_blobs():
    """Lists all the blobs in the bucket."""
    bucket = dbase.get_bucket(app.config['CLOUD_STORAGE_BUCKET'])

    blobs = bucket.list_blobs()
    img_urls = [blob.public_url for blob in blobs]
    return img_urls


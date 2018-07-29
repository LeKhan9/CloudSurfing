from flask import Flask, render_template, request

from scripts.cloud_store import CloudStorage
from scripts.image_interpretation import ImageInterpreter
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# -------- SETUP ----------
HTML_BASE_PAGE = app.config.get('HTML_BASE_PAGE')
LANGUAGES_LS = app.config.get('TRANSLATE_TO_LANG')
ISO_LANG_MAP = app.config.get('LANGUAGE_MAP')
ALLOWED_EXTENSIONS = app.config.get('ALLOWED_EXTENSIONS')

interpreter = ImageInterpreter()
database = CloudStorage(project_id=app.config.get('PROJECT_ID'),
                        storage_bucket=app.config.get('CLOUD_STORAGE_BUCKET'))
# -------------------------

def allowed_file(filename):
    return '.' in filename and filename.split('.').pop().lower() in ALLOWED_EXTENSIONS

@app.route("/")
def welcome():
    return render_template(HTML_BASE_PAGE, stored_images=database.get_images()) # display images already interpreted

@app.route('/interpret', methods=['POST'])
def upload_file():
    """
        Filter out requests without images and/or improper file extensions, otherwise render response
        using helper function below

    :return:
    """

    file = request.files.get('image')
    file_name = file.filename

    if not file: # no file given
        return render_template(HTML_BASE_PAGE, no_file=True)

    if not allowed_file(file_name): # improper file extension
        return render_template(HTML_BASE_PAGE, wrong_extension=True)

    gcloud_url = database.upload_image_file(file) # save img to Google Cloud Storage

    if not gcloud_url: # upload error, no URL found
        return render_template(HTML_BASE_PAGE, upload_error=True)

    response_blob = interpreter.interpret_image(gcloud_url)
    return render_vision_api_response(response_blob, file_name, gcloud_url)

def render_vision_api_response(response_blob, file_name, gcloud_url):
    """
        Filters out unsafe images and displays Vision API image aspects, some helpful links, and language translations

    :param response_blob: custom wrapper class to encapsulate all Vision API response data
    :param file_name: full file name
    :param gcloud_url: URL of file on google cloud - entry point for running Vision API requests
    :return: HTML Flask render object
    """

    unsafe_tags = response_blob.get_unsafe_tags()
    if unsafe_tags: # image tagged as unsafe
        database.delete_blob(file_name)
        return render_template(HTML_BASE_PAGE, unsafe_tags=unsafe_tags)

    # extract dict of relevant API response metadata to display in HTML to user
    interpreter_params = interpreter.build_html_params(LANGUAGES_LS, ISO_LANG_MAP, response_blob)

    return render_template(HTML_BASE_PAGE, filename=gcloud_url, stored_images=database.get_images(), **interpreter_params)

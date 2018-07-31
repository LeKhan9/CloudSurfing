import json
import os


class Config(object):
    HTML_BASE_PAGE = 'index.html'
    ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
    TRANSLATE_TO_LANG = ['fr', 'es', 'ar'] # choose any languages to translate to - based on ISO 639-1 codes

    # Explicitly set the constants here or export and read from your env
    PROJECT_ID = os.environ['PROJECT_ID']
    CLOUD_STORAGE_BUCKET = os.environ['CLOUD_STORAGE_BUCKET']

    with open('config/iso_639_1_codes.json') as f:
        LANGUAGE_MAP = json.load(f)

    WIKIPEDIA_ENDPOINT = 'https://en.wikipedia.org/wiki/{}'
    UNSAFE_IMG_TAGS = ['adult', 'violence', 'racy']
    UNSAFE_IMG_PROBABILITY_THRESHOLD = 4

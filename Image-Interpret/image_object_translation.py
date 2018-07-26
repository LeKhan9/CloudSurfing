import io
import argparse

from google.cloud import vision
from google.cloud.vision import types
from google.cloud import translate

from flask import current_app

from web_detect_data import WebDetectResponse


class ImageObjectTranslator:
    def __init__(self):
        # initialize clients
        self.image_client = vision.ImageAnnotatorClient()
        self.translate_client = translate.Client()

    def classify_image(self, img_path):
        """
            Given an image path - predictions and annotations are provided from the vision API through a wrapper class

        :param img_path: full web, google storage, or local path to img
        :return: wrapper class to encapsulate various responses from annotation API
        """
        image = ImageObjectTranslator.get_raw_img(img_path)
        detected_aspects = self.image_client.web_detection(image=image).web_detection
        web_detect_response = WebDetectResponse(detected_aspects)

        return web_detect_response

    def translate_prediction(self, target_language):
        #TODO - translate the top X predictions for the image using the translation API
        pass

    @classmethod
    def get_raw_img(cls, img_path):
        """
            Compressed image object from a web, google storage, or local path

        :param img_path: full web, google storage, or local path to img
        :return: compressed image object
        """
        if img_path.startswith('http') or img_path.startswith('gs:'):
            image = types.Image()
            image.source.image_uri = img_path
        else:
            with io.open(img_path, 'rb') as image_file:
                content = image_file.read()

            image = types.Image(content=content)

        return image

    @classmethod
    def print_url_with_msg_for_token(self, token, msg):
        """
            If the token is exists, print the url and a corresponding string description

        :param token: various annotation API response objects - such as page, partial image, or full image match
        :param msg: string message provided as description to client
        :return: N/A
        """

        if token:
            print '\n{}'.format(msg)
            print token

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--img", help="full file path to img")
    parser.add_argument("--verbose",
                        help="verbose mode will print extra details",
                        action='store_true')

    args = parser.parse_args()

    image_translator = ImageObjectTranslator()
    web_detect_response = image_translator.classify_image(args.img)

    relevant_page = web_detect_response.get_relevant_page()
    full_matched_image = web_detect_response.get_full_image_match()
    partial_matched_image = web_detect_response.get_partial_image_match()
    class_weights_tuples = web_detect_response.get_classes_by_score()
    wikipedia_article = web_detect_response.get_wikipedia_article()

    if args.verbose:
        image_translator.print_url_with_msg_for_token(relevant_page, 'Relevant Page:')
        image_translator.print_url_with_msg_for_token(wikipedia_article, 'Relevant Wikipedia Article:')
        image_translator.print_url_with_msg_for_token(full_matched_image, 'Found full matched image:')
        image_translator.print_url_with_msg_for_token(partial_matched_image, 'Found partial matched image:')

    print '\nTop Classifications'
    if class_weights_tuples:
        for pred, weight in class_weights_tuples[:3]:
            print 'Prediction: {}, Confidence: {:.2f}'.format(pred, weight)


if __name__ == '__main__':
    main()


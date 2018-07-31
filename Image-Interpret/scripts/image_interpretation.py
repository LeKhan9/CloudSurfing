import io
import argparse

from google.cloud import vision
from google.cloud import translate
from google.cloud.vision import types

from vision_api_response import ResponseBlob


class ImageInterpreter:

    def __init__(self):
        self.image_client = vision.ImageAnnotatorClient()
        self.translate_client = translate.Client()

    def interpret_image(self, img_path):
        """
            Given an image path - predictions and annotations are provided from the vision API through a wrapper class

        :param img_path: full web, google storage, or local path to img
        :return: wrapper class to encapsulate various responses from annotation API
        """

        image = ImageInterpreter.get_raw_img(img_path)
        detected_aspects = self.image_client.web_detection(image=image).web_detection
        censor_aspects = self.image_client.safe_search_detection(image=image).safe_search_annotation
        vision_response = ResponseBlob(detected_aspects, safety_metadata=censor_aspects)

        return vision_response

    def translate_prediction(self, text, target_language):
        """
            Translates an input string to a desired language

        :param text: input string to translate
        :param target_language: ISO 639-1 code for language to translate to; ex: 'es' for Spanish
        :return: string translation of input text in desired image
        """

        translation_response = self.translate_client.translate(text, target_language=target_language)
        if translation_response:
            translation = translation_response.get('translatedText')
            return translation if translation != text else 'Same as English or N/A'

        return ''

    def build_html_params(self, languages_ls, iso_lang_map, response_blob):
        """
            Builds a dict of params to pass to the main HTML page for the app;
            Parameter data is parsed from the custom ResponseBlob object and from live translations
                through the Google translation API

        :param languages_ls: A list of languages to translate to - labeled as ISO codes
        :param iso_lang_map: A map of ISO 639-1 codes to language
        :param response_blob: custom wrapper class for Vision API output
        :return: dict of parameters to pass to the html page
        """

        relevant_page = response_blob.get_relevant_page()
        full_matched_image = response_blob.get_full_image_match()
        partial_matched_image = response_blob.get_partial_image_match()
        wikipedia_article = response_blob.get_wikipedia_article()
        class_weights_tuples = response_blob.get_classes_by_score()

        # encoding in case unexpected unicode characters are encountered
        highest_matches = [tup[0] for tup in class_weights_tuples][:2]
        top_pred = highest_matches[0]

        translations = {}
        for lang in languages_ls:
            translations[iso_lang_map.get(lang)] = self.translate_prediction(top_pred, lang)

        html_params = {'relevant_page': relevant_page,
                       'full_matched_image': full_matched_image,
                       'partial_matched_image': partial_matched_image,
                       'wikipedia_article': wikipedia_article,
                       'highest_matches': highest_matches,
                       'translations': translations}
        return html_params

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
    """ Try running this file directly with command line args --img and --verbose to interpret an image! """

    parser = argparse.ArgumentParser()
    parser.add_argument("--img", help="full file path to img")
    parser.add_argument("--verbose",
                        help="shows extra links and details",
                        action='store_true')

    args = parser.parse_args()

    interpreter = ImageInterpreter()
    vision_response = interpreter.interpret_image(args.img)

    relevant_page = vision_response.get_relevant_page()
    full_matched_image = vision_response.get_full_image_match()
    partial_matched_image = vision_response.get_partial_image_match()
    pred_weights_tuples = vision_response.get_classes_by_score()
    wikipedia_article = vision_response.get_wikipedia_article()

    print '\nTop Classifications'
    if pred_weights_tuples:
        for pred, weight in pred_weights_tuples[:3]:
            print 'Prediction: {}, Confidence: {:.2f}'.format(pred, weight)

    print 'Translation of top prediction in Arabic:'
    print interpreter.translate_prediction(pred_weights_tuples[0][0], 'ar')

    if args.verbose:
        interpreter.print_url_with_msg_for_token(relevant_page, 'Relevant Page:')
        interpreter.print_url_with_msg_for_token(wikipedia_article, 'Relevant Wikipedia Article:')
        interpreter.print_url_with_msg_for_token(full_matched_image, 'Found full matched image:')
        interpreter.print_url_with_msg_for_token(partial_matched_image, 'Found partial matched image:')


if __name__ == '__main__':
    main()

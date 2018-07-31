import requests

from ..config import Config

class ResponseBlob:
    """
        Wrapper for data responses out of cloud Image Annotation API with getters to simplify interface with Flask app
    """

    def __init__(self, cloud_web_response, safety_metadata):
        """
            Extract various aspects of the image annotation API response

        :param cloud_web_response: Google Cloud API response for annotation call
        :param safety_metadata: metadata detailing probability of this image being spoofy, adult, violent, medical, or racy
        """

        self.cloud_web_response = cloud_web_response

        self.relevant_pages = self.cloud_web_response.pages_with_matching_images
        self.full_image_matches = self.cloud_web_response.full_matching_images
        self.partial_image_matches = self.cloud_web_response.partial_matching_images
        self.classifications = self.cloud_web_response.web_entities

        self.safety_metadata = safety_metadata

    def get_relevant_page(self):
        """
            Supposing we have page matches, return the top one

        :return: page json object from annotation API response
        """

        return self.relevant_pages[0].url if self.relevant_pages else None

    def get_full_image_match(self):
        """
            Supposing we have full image matches, return the top one

        :return: full image json object from annotation API response
        """

        return self.full_image_matches[0].url if self.full_image_matches else None

    def get_partial_image_match(self):
        """
            Supposing we have partial image matches, return the top one

        :return: partial image json object from annotation API response
        """

        return self.partial_image_matches[0].url if self.partial_image_matches else None

    def get_classes_by_score(self):
        """
            Build and return tuples of prediction and weight for each classification

        :return: list of tuples (pred, weight)
        """

        class_weight_tuples = []
        if not self.classifications:
            return class_weight_tuples

        for classified in self.classifications:
            class_weight_tuples.append((classified.description, classified.score))

        return class_weight_tuples

    def get_unsafe_tags(self):
        """
            Given metadata about an image being unsafe, return corresponding tags if necessary

        :return: list of censorship tags:  'adult', 'racy', and/or 'violence'
        """

        tags = []
        for tag in Config.UNSAFE_IMG_TAGS:
            probability = getattr(self.safety_metadata, tag)
            if probability < Config.UNSAFE_IMG_PROBABILITY_THRESHOLD:
                continue
            tags.append(tag)
        return tags

    def get_wikipedia_article(self):
        """
            Ping wiki page for existence and health to obtain a valid wiki page link

        :return: requests response object
        """

        if not self.classifications:
            return None

        main_predicted_class = self.classifications[0].description.replace(' ', '_')
        full_wiki_url = Config.WIKIPEDIA_ENDPOINT.format(main_predicted_class)
        wiki_response = requests.get(full_wiki_url)

        return wiki_response.url if wiki_response.status_code == 200 else None

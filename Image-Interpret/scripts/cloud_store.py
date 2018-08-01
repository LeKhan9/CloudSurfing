from google.cloud import storage

class CloudStorage:
    def __init__(self, project_id, storage_bucket):
        self.data_base = storage.Client(project=project_id)
        self.bucket = storage_bucket

    def upload_image_file(self, image_file):
        """
            Takes a Flask request file object and uploads it to Google Cloud Storage

        :param image_file: Flask request file object
        :return: Google Cloud Storage URL for image
        """

        if not image_file:
            return ''

        image_url = self.upload_as_blob(image_file.read(), image_file.filename, image_file.content_type)

        return image_url

    def upload_as_blob(self, file_data, filename, content_type):
        """
            Helper function that takes a Flask request file object and uploads it to Google Cloud Storage

        :param file_data: data stream from Flask file object
        :param filename: string name of the file
        :param content_type: data format of the file
        :return: Google Cloud Storage URL for image
        """

        bucket = self.data_base.bucket(self.bucket)
        blob = bucket.blob(filename)

        blob.upload_from_string(file_data, content_type=content_type)
        url = blob.public_url

        return url

    def delete_blob(self, blob_name):
        bucket = self.data_base.bucket(self.bucket)
        blob = bucket.delete_blob(blob_name)

        return blob

    def get_images(self):
        """
            Returns a list of image URLs for all images in the Google Cloud Storage bucket

        :return: list of image Google Cloud Storage URLs
        """

        bucket = self.data_base.get_bucket(self.bucket)

        blobs = bucket.list_blobs()
        img_urls = [blob.public_url for blob in blobs]
        return img_urls

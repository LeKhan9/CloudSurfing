# CloudSurfing

Experimentation with various Google Cloud Machine Learning APIs

# Image Interpret

### Summary
The Google Vision, Translate, and Storage APIs are leveraged to orchestrate displaying relevant web links, classifications, and language translations for an image. 

As images are uploaded, they are tossed into Google Cloud Storage. These storage links are then fed into the Vision Annotation API to extract useful aspects. The classifications are translated in any language the user provides in the config file so that you can also beef up your language skills ;) 

These relevant web links and translations are displayed to the user. A recently viewed / analyzed gallery of images is also displayed to the user.

### Workflow
**Upload an image**:
<img src="https://storage.googleapis.com/quick-platform-149322.appspot.com/img_upload.png" alt="drawing"/>

**Wait patiently on the loading screen :)**

**Image interpretations and links are presented to the user in a card:**
<img src="https://storage.googleapis.com/quick-platform-149322.appspot.com/relevant_links.png" alt="drawing" width="400" height="400"/>

You can click on any of these links to take you to relevant pages. Examples for the image above:

[Predicted relevant online article](https://en.wiktionary.org/wiki/cat)

[Relevant predicted Wikipedia article](https://en.wikipedia.org/wiki/Kitten)


**Image classification translations are presented to the user in a card:**

<img src="https://storage.googleapis.com/quick-platform-149322.appspot.com/translations.png" alt="drawing" width="450" height="200"/>

**A gallery of recently uploaded images is presented to the user at all times:**

<img src="https://storage.googleapis.com/quick-platform-149322.appspot.com/image_gallery.png" alt="drawing"/>


### Prerequisites

```
Flask==0.12.2
Werkzeug<0.13.0,>=0.12.0
google-cloud-vision
google-cloud-translate
google-cloud-storage
```

You will also need to:
* [create a project](https://cloud.google.com/resource-manager/docs/creating-managing-projects)
* [create a cloud storage bucket](https://cloud.google.com/storage/docs/creating-buckets)
* [enable the Vision, Translation, and Storage APIs](https://cloud.google.com/endpoints/docs/openapi/enable-api)

### Installing

Installing the Python dependencies locally:

```
pip install -r requirements.txt
```

**OR**

Installing python dependencies for App Engine:

```
pip install -t lib/ -r requirements.txt
```

this will make copied installs in the lib folder which app engine can point to in order to identify 3rd party libs


## Project Configuration
Set up Project ID and Cloud Storage Bucket link. You can do this two ways:

Export the values in the environment:
```
export PROJECT_ID=YOUR_PROJECT_ID
export CLOUD_STORAGE_BUCKET=YOUR_CLOUD_STORAGE_BUCKET
```

**OR**

Explicitly edit the config file (Image-Interpret/config/__init__.py):
```
PROJECT_ID = YOUR_PROJECT_ID
CLOUD_STORAGE_BUCKET = YOUR_CLOUD_STORAGE_BUCKET
```

Set up languages you want to translate to in the config file:
```
TRANSLATE_TO_LANG = ['fr', 'es', 'ar'] # choose any languages to translate to - based on ISO 639-1 codes
```

## Running - locally
Export the flask env:
```
cd Image-Interpret/
export FLASK_APP=app.py
```

Run the app:
```
flask run
```

## Running - Google App Engine [Not completely tested]
Given the app.yaml and appengine_config.py files we should be able to integrate with App Engine.

NOTE: There may be dependency issues with finding the right imports from the lib folder based on project path specs and any virtual environments set up. This way of running is not recommended at the moment.

**For reference**

Deploy to App Engine directly through:
```
gcloud app deploy
```

You can also test locally:
```
dev_appserver.py app.yaml
```


## Built With

* [Google Vision API](https://cloud.google.com/vision/docs/apis) - to handle extraction of various image features and obtain annotations
* [Google Translation API](https://cloud.google.com/storage/docs/apis) - to handle language translation of classifications
* [Google Storage API](https://cloud.google.com/translate/docs/apis) - to handle upload and retrieval of images

* [Flask](http://flask.pocoo.org/) - web microframework 
* [Jinja](http://jinja.pocoo.org/docs/2.10/) - templating framework
* [Bootstrap](https://getbootstrap.com/docs/3.3/getting-started/) - front end framework for clean card templating
* [JQuery](https://jquery.com/) - JS lib to handle loading screen while image interpretation churns away

### Acknowledgements
Image links:

* [Cat](http://iphonewallpapershd.com/wp-content/uploads/2018/05/cute-little-kitten-wallpaper-iphone-x-best-of-free-wallpapers-cats-and-kittens-impremedia-of-cute-little-kitten-wallpaper-iphone-x.jpg)
* [LeBron GOAT](https://clutchpoints.com/wp-content/uploads/2018/07/LeBron-James-9.jpg)
* [House Plant](http://www.italianlightdesign.com/img/indoor-fig-tree/_fullsize/perky-ficus-benjamina-danielle-weeping-fig-tree-house-plant-benjamina-danielle-weeping-fig-tree-house-plant_indoor-fig-tree.jpg)


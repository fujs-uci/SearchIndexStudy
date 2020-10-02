# SearchIndexStudy

## Goal

1. Create a TF-IDF Search Index

2. Develop a better understanding of Pandas

3. Develop a better understanding of processing large data efficiently

# Tools
Django, Bootstrap, Pandas

## Resources

movie dataset: https://www.kaggle.com/rounakbanik/the-movies-dataset

# How to deploy

## Prerequisites

1. Python 3 (https://www.python.org/downloads/)

2. Django (https://www.djangoproject.com/download/)

3. Pandas (https://pandas.pydata.org/)

## Steps

1. Clone repository

2. Start Django project:
```
django-admin startproject [project_name]
```

3. Place Results clone inside project directory.

4. In project_name.settings.py add the following:
```
INSTALLED_APPS = [

  'results.apps.ResultsConfig',  # Add this line
  ...
]
```

5. In project_name.urls.py add the following:
```
urlpatterns = [
    path('', include('results.urls')),  # Add this line
    ...
]
```

6. Download the datasets from Kaggle -> https://www.kaggle.com/rounakbanik/the-movies-dataset.
  - credits.csv
  - keywords.csv
  - movies_metadata.csv
  
7. Create test csv files with a subset of the records:
  - credits_test.csv
  - keywords_test.csv
  - movies_metadata_test.csv
  
8. Run the following command to load the files into the default database:
```
python manage.py load_file --movies [meta_data.csv] --keywords [keywords.csv] --credits [credits.csv]
```

9. Run the following command to generate the TF-IDF index:
```
ptyhon manage.py calibrate
```

10. Launch Django and start searching Movies by keyword query

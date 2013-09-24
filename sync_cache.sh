#! /bin/bash

export PYTHONPATH=$PYTHONPATH:/home/sebmartin/django
export DJANGO_SETTINGS_MODULE=albums.settings
python ./sync_cache.py

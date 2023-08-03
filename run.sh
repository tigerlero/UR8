#!/bin/bash

# Apply migrations
python manage.py makemigrations
python manage.py migrate

# Start the Django development server
python manage.py runserver

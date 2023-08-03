#!/bin/bash

# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

# Apply migrations
python manage.py makemigrations
python manage.py migrate

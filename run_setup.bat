@echo off
python manage.py migrate
python manage.py setup_sample_data
python manage.py runserver

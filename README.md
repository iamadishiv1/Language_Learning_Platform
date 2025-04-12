# Language_Learning_Platform
Creating Project from Beginning
//SetUP
python3 -m venv myenv
source myenv/bin/activate
pip install django
pip install --upgrade pip
python -m django --version

//Start Making Project start with creation
django-admin startproject language_platform
cd language_platform
python manage.py startapp learning
python manage.py migrate
python manage.py createsuperuser  # Create the admin user
python manage.py runserver

http://127.0.0.1:8000/

Run: python manage.py runserver 8080
to start the server

Access the webpage at: http://localhost:8080/login

The login.html webpage is under 'ssad911/system/templates/registration'
(has to be there by Django conventions)

command to run shell: python manage.py shell




commands to create user (operator/supervisor):
python manage.py shell
from django.contrib.auth.models import User
user = User.objects.create_user('operator1', 'operator1@911.com','operator1') //username, email, pw
user.role.job = 'operator'
user.save()
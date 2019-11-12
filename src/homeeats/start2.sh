python manage.py flush --no-input 
python manage.py migrate 
python manage.py loaddata real_data.json
python manage.py runserver localhost:8000
python3 manage.py flush --no-input 
python3 manage.py migrate 
python3 manage.py loaddata real_data.json
python3 manage.py runserver localhost:8000
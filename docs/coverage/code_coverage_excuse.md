# Code Coverage Excuses

#### homeeats/wsgi.py
This file contains django-generated code that exposes the WSGI callable as a module-level variable. We did not add any code to this file and therefore are not testing it.

#### homeeats_app/apps.py
This file contains django-generated code that allows the user to add any necessary application configuration information. We did not add any additional configuration information to this file, and therefore are not testing it.

#### manage.py
This file is django's executable file. We did not change this file so we are not testing it.

#### homeeats_app/tests.py
This is our tests file. We are not testing it because testing our tests is worthless.

#### migrations/*
Although all of the migrations have 100% coverage, we aren't testing them because they just define the database schema and are django-generated. 
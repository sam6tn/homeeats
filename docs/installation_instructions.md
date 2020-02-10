##AWS Database Setup

1. Create AWS account if necessary and launch AWS console
2. Go to RDS (Relational Database Service) 
3. Click on “Create Database” and you will be taken to a database creation module
4. Choose “Standard Create” for method and “PostgreSQL” for the engine type
5. Use the free tier template if this is meant for development or a production template if meant for production
6. Give your database a name, username and password in the Settings section, make sure to write them down because you will need them later
7. Under connectivity, hit the “Additional connectivity configuration” dropdown, and select Yes for publicly accessible.  
8. Keep everything else the same as default and select “Create Database”
9. In the console, click on your new database so you are on a page that looks similar to this:



10. Scroll down to security group rules and add rules necessary so that your security group rules look like this: 




##Installing Python3 on Linux
1. Open the Terminal, type “python3 --version” to see if you have Python3 installed. If python3 has been installed, then there is no need to reinstall python3.
2. If you are using Ubuntu 16.10 or newer, then you can easily install Python 3.6 with the following commands:
sudo apt-get update
sudo apt-get install python3.6
3. If you’re using another version of Ubuntu
sudo apt-get install software-properties-common
$ sudo add-apt-repository ppa:deadsnakes/ppa
$ sudo apt-get update
$ sudo apt-get install python3.6
4. Check if pip3 has been installed by entering “command -v pip3” into the command line

##Clone the HomeEats repository
1. Open the Command Prompt application on Windows or the Terminal application on Mac.
2. Move to the directory where you would like the HomeEats repository to be installed.
3. Enter into the command line: $ git clone https://github.com/uva-cp-1920/HomeEats.git

##Database Configuration in HomeEats Repo

1. Go to the AWS console and to the RDS service
2. Click on the RDS instance you created to open a page looking like this: 

3. Go to the settings.py file in your HomeEats Repo and copy/paste the below to replace what is currently in the DATABASES variable.
`
DATABASES = {
   'default': {
       'ENGINE': 'django.db.backends.postgresql_psycopg2',
       'NAME': 'homeeats',
       'USER': 'postgres',
       'PASSWORD': 'homeeats123',
       'HOST': 'dev-homeeats1.cetolplhgphy.us-east-1.rds.amazonaws.com',
       'PORT': '5432',
   }
}
`
4. Replace the NAME, USER and PASSWORD with the credentials you wrote down from the first part of these installation instructions when you provisioned your RDS instance
5. Replace HOST and PORT with the Endpoint & Port shown in the screenshot from step 2

##Install HomeEats dependencies
1. On the command line, from the HomeEats root folder, “cd src/homeeats”
2. Type “ls” to ensure that you are in the right location. You should see requirements.txt listed as a file in that directory.
3. Then enter into the command line, pip3 install --upgrade -r requirements.txt.

##Deploying to AWS:
1. In a terminal install awsebcli
`pip3 install awsebcli`
2. CD into the HomeEats root folder
3. Initialize EB Cli repository
`$ eb init -p python-3.6 <APPLICATION NAME>`
4. Create an environment and deploy the application to it
`$ eb create <ENVIRONMENT NAME>`
5. Find the domain name of the new environment
`$ eb status`

6. Edit the settings.py file located at <HOMEEATS ROOT>/src/homeeats/homeeats/settings.py
Add your applications CNAME to the ALLOWED_HOSTS array
For example: ALLOWED_HOSTS = ['128.143.67.97', 'localhost', '127.0.0.1', 'django-env.tgmufqa8jm.us-west-2.elasticbeanstalk.com']
7. Save the file then deploy the application
`$ eb deploy`
8. When the deployment process completes you can view your application with
`$ eb open`


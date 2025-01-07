# NLC Script Database: Web
The NLC Script Database is accessed by authenticated users through a custom Django web site.

## Development
To run the site locally, make the `web` directory a [Python3 virtual environment](https://docs.python.org/3/tutorial/venv.html):\
`python3 -m venv .`

Then install the required Python packages:\
`pip3 install -r requirements.txt`

On first load of the project, run the [Django database migrations](https://docs.djangoproject.com/en/2.2/topics/migrations/):\
`python3 manage.py migrate`

Before starting the site, update the web/script_search/script_search/settings.py file with the postgres connection information and a valid SECRET_KEY. Secret keys can be generated with [Djecrety](https://djecrety.ir/).\
To start the Django server locally:\
`python3 manage.py runserver`

## Database
Django has out-of-the-box integration with PostgreSQL. Models are defined in /web/script_search/search/models.py and the migration files are in the /web/script_search/search/migrations directory. The `Script` table holds the TV and movie script instances and metadata, whereas the `ScriptMigration` table is used during the upload process.\
Full-text search is implemented on this database through the use of indices, a trigger, and a function, which can be viewed in the migration files.

## Deployment
The Django and PostgreSQL solution is deployed to AWS Elastic Beanstalk with EB CLI. Files in the `.ebextensions` and `.elasticbeanstalk` directories provide previous configurations used to deploy the code.\
Much of the information necessary for deployment can be found in this [Real Python](https://realpython.com/deploying-a-django-app-and-postgresql-to-aws-elastic-beanstalk/) walkthrough.

## Management
Django has built-in [management](https://docs.djangoproject.com/en/2.2/ref/contrib/admin/) functionality. The live site has an administrative user that can access the /admin site to provision new users and make updates to the Script table.

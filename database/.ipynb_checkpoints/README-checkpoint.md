# NLC Script Database: Database
The PostgreSQL database model is defined in the Django project. Files in this portion of the project upload the TV and movie script data into the script database.

## script_importer.py
Once the scripts are downloaded and packaged into text files for import to postgres, the `script_importer.py` is used to upload the information into the database.\
The corresponding `run_script_importer.py` file is used to run the upload process and requires the following parameters to be set in the file:
- `import_files_dir`: Local directory holding the postgres import files
- `db_info.db_name`: Name of the postgres database to upload data to
- `db_info.db_user`: User to perform the upload with
- `db_info.db_host`: URL of the postgres instance
- `db_info.db_password`: Password of the postgres user
- `db_info.table_name`: Name of the database table to upload to (normally 'ScriptMigration')

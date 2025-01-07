from script_importer import ScriptImporter


def run_script_importer(import_files_dir, db_info):
  try:
    script_importer = ScriptImporter(import_files_dir, db_info)
    print('Starting script import process')
    script_importer.run_import_process()
    print('Finished script import process')
  except Exception as e:
    print('An error occurred during import process: {error}'.format(error=str(e)))


if __name__ == '__main__':
  # Parameters for importing scripts into the postgres database
  import_files_dir = ''
  db_info = { 'db_name': '', 'db_user': '', 'db_host': '', 'db_password': '', 'table_name': '' }

  # Engage!
  run_script_importer(import_files_dir, db_info)

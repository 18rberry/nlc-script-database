import psycopg2
from os import path, listdir
from os.path import isfile, join
import logging
from time import time, strftime


class ScriptImporter:
  def __init__(self, import_files_dir, db_info):
    self.import_files_dir = import_files_dir
    self.db_info = db_info
    self.table_name = self.db_info['table_name']
    self.conn_str = "dbname='{db_name}' user='{db_user}' host='{db_host}' password='{db_password}'".format(
                    db_name=self.db_info['db_name'],
                    db_user=self.db_info['db_user'],
                    db_host=self.db_info['db_host'],
                    db_password=self.db_info['db_password']
                  ) 
    print(self.db_info)
    self.conn = None
    self.log_file = 'scriptimporter_{time}.log'.format(time=strftime('%Y-%m-%d %H-%M'))

    logging.basicConfig(filename=self.log_file, format='%(levelname)s: %(message)s', level=logging.DEBUG)
    
  
  def run_import_process(self):
    """Connect to the database and kick off the script import process.
    """
    start_time = time()

    try:
      logging.info('Starting import process')
      self.connect_to_db()
    except:
      raise ValueError('Failed to connect to database with given information.')

    self.import_scripts()
    self.conn.close()

    total_time = time() - start_time
    logging.info('Import process completed in {time} sec.'.format(time=total_time))
  
  def import_scripts(self):
    """Iterate through the files in the given directory and attempt to import them into postgres.
    """
    import_file_names = listdir(self.import_files_dir)
    for import_file_name in import_file_names:
      logging.info('Processing {import_file_name}'.format(import_file_name=import_file_name))
      try:
#         with open(join(self.import_files_dir, import_file_name), 'r', encoding='ISO-8859-1') as import_file:
#           self.cur.copy_from(import_file, self.table_name, sep='\t', columns=('script_type', 'title', 'season_text', 'year_text', 'episode_text', 'episode_title', 'script_content'))
    # try new optimizaiton for batch processing files 
        with open(join(self.import_files_dir, import_file_name), 'r', encoding='ISO-8859-1') as import_file:
                while True:
                    lines = list(import_file.readlines(1000))  # Adjust batch size as needed
                    if not lines:
                        break
                    self.cur.copy_from(
                        '\n'.join(lines),
                        self.table_name,
                        sep='\t',
                        columns=(
                            'script_type', 'title', 'season_text',
                            'year_text', 'episode_text', 'episode_title', 'script_content'
                        )
                    )
      except Exception as e:
        logging.error('Error occurred importing file ' + import_file_name + ': ' + str(e))
        self.connect_to_db()  # Reconnect to the database
  
  def connect_to_db(self):
    """Connect to the postgres instance.
    """
    logging.info('Connecting to postgres')
    self.conn = psycopg2.connect(self.conn_str)
    self.conn.autocommit = True
    self.cur = self.conn.cursor()

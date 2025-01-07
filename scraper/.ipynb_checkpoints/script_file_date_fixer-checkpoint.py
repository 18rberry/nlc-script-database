import os
import logging
from time import strftime, time
import scraper_constants


class ScriptFileDateFixer():
  def __init__(self, script_dir, date_fix_file):
    self.script_dir = script_dir
    self.date_fix_file = date_fix_file
    self.log_file = 'scriptfiledatefixer_{time}.log'.format(time=strftime('%Y-%m-%d %H-%M'))

    logging.basicConfig(filename=self.log_file, format='%(levelname)s: %(message)s', level=logging.DEBUG)

  def fix_dates(self):
    logging.info('Starting script file date fix process:\n\tScript directory:{script_dir}\n\tFix file:{fix_file}'
                  .format(
                    script_dir=self.script_dir,
                    fix_file=self.date_fix_file
                  )
                )
    start_time = time()

    try:
      if os.path.exists(self.script_dir) and os.path.isfile(self.date_fix_file):
        with open(self.date_fix_file, 'r') as fix_file:
          for line in fix_file:
            if not line:
              continue
            
            script_attributes = line.split('\t')
            script_title = script_attributes[0]
            script_date = script_attributes[1]
            self.update_script_dir(script_title, script_date)
      else:
        raise ValueError('Script directory path or date file does not exist')
    except Exception as e:
      logging.error('An error occurred: ' + str(e))
    
    total_time = time() - start_time
    logging.info('Total time: ' + str(total_time))

  def update_script_dir(self, script_title, script_date):
    clean_title = scraper_constants.clean_script_title(script_title)
    script_letter = script_title[0]
    if script_letter.isalpha():
      search_dir = '/'.join([self.script_dir, script_letter])
    else:
      search_dir = '/'.join([self.script_dir, '0'])
    
    if os.path.exists(search_dir):
      sub_dirs = os.listdir(search_dir)
      script_matches = [sub_dir for sub_dir in sub_dirs if clean_title == sub_dir[:sub_dir.rfind('_')]]
      if script_matches:
        for script_match in script_matches:
          dir_to_update = '/'.join([search_dir, script_match])
          os.rename(dir_to_update, dir_to_update.replace(scraper_constants.DATE_TOKEN, script_date))
      else:
        logging.error('No match found for ' + clean_title)
    else:
      raise ValueError('Search directory path not found: ' + search_dir)

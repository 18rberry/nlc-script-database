import os
import logging
from time import strftime, time
import scraper_constants


class PostgressImportCreator():
  def __init__(self, tv_dir, movie_dir, movies_per_file=500, tv_shows_per_file=2000):
    self.tv_dir = tv_dir
    self.movie_dir = movie_dir
    self.movies_per_file = movies_per_file
    self.tv_shows_per_file = tv_shows_per_file
    self.current_movie_file = None
    self.current_tv_file = None
    start_time = strftime('%Y-%m-%d %H-%M')
    self.log_file = 'postgressimportcreator_{time}.log'.format(time=start_time)
    self.start_time = start_time

    logging.basicConfig(filename=self.log_file, format='%(levelname)s: %(message)s', level=logging.DEBUG)

  def create_import_files(self):
    """Kicks off process to create postgres import files
    """
    start_time = time()

    if os.path.exists(self.movie_dir) and os.path.exists(self.tv_dir):
      self.create_movie_import_files()
      self.create_tv_import_files()
    else:
      raise ValueError('The provided movie and/or tv directory does not exist.')

    total_time = time() - start_time
    logging.info('Total time: ' + str(total_time))
  
  def create_movie_import_files(self):
    """Creates a series of movie data import files for postgres
    """
    logging.info('Starting movie file creation')
    movie_file_count = 0
    movies_per_file_counter = 0

    self.increment_movie_import_file(movie_file_count)

    movie_letters = os.listdir(self.movie_dir)
    for letter in movie_letters:
      try:
        movie_files = os.listdir('/'.join([self.movie_dir, letter]))
        for movie_file in movie_files:
          try:
            movie_title, movie_year = self.extract_movie_title_and_year_from_file_name(movie_file)
            # Replace tokens with special characters
            movie_title = scraper_constants.remake_script_title(movie_title)
            with open('/'.join([self.movie_dir, letter, movie_file]), 'r', encoding='ISO-8859-1') as movie_file_contents:
              movie_script = movie_file_contents.read()
            
            # Attributes in the following order: type, title, season, year, episode_number, episode_title, script
            movie_data = '\t'.join(['M', movie_title, '-1', movie_year, '-1', '', movie_script]) + '\n'
            self.current_movie_file.write(movie_data)
            movies_per_file_counter += 1

            if movies_per_file_counter >= self.movies_per_file:
              movie_file_count += 1
              self.increment_movie_import_file(movie_file_count)
              movies_per_file_counter = 0
          except Exception as e:
            logging.error('Error occurred while processing movie ' + movie_file + ': ' + str(e))
      except Exception as e:
        logging.error('Error occurred while processing movie letter' + letter + ': ' + str(e))
    
    logging.info('Finished movie file processing')
  
  def create_tv_import_files(self):
    """Creates a series of TV data import files for postgres
    """
    logging.info('Starting TV file creation')
    tv_file_count = 0
    tv_per_file_counter = 0

    self.increment_tv_import_file(tv_file_count)

    tv_letters = os.listdir(self.tv_dir)
    for letter in tv_letters:
      try:
        if os.path.isfile('/'.join([self.tv_dir, letter])):
          continue

        show_dirs = os.listdir('/'.join([self.tv_dir, letter]))
        for show_dir in show_dirs:
          try:
            if os.path.isfile('/'.join([self.tv_dir, letter, show_dir])):
              continue

            show_title, show_year = self.extract_tv_title_and_year_from_dir(show_dir)
            show_season_dirs = os.listdir('/'.join([self.tv_dir, letter, show_dir]))

            for show_season_dir in sorted(show_season_dirs):
              try:
                if os.path.isfile('/'.join([self.tv_dir, letter, show_dir, show_season_dir])):
                  continue
      
                show_season = show_season_dir.split(' ')[1]

                # Calculate current season's year. E.g., if show_year is 1995,
                # then season 4's year is 1995 + 4 - 1 = 1998
                current_show_year = str(int(show_year) + int(show_season) - 1)
                show_season_eps = os.listdir('/'.join([self.tv_dir, letter, show_dir, show_season_dir]))
                for show_season_ep in show_season_eps:
                  try:
                    ep_number, ep_title = self.extract_tv_episode_number_and_title_from_file(show_season_ep)
                    # Replace tokens with special characters
                    ep_title = scraper_constants.remake_script_title(ep_title)
                    with open('/'.join([self.tv_dir, letter, show_dir, show_season_dir, show_season_ep]), 'r', encoding='ISO-8859-1') as ep_contents:
                      show_script = ep_contents.read()
                    
                    # Attributes in the following order: type, title, season, year, episode_number, episode_title, script
                    show_data = '\t'.join(['T', show_title, show_season, current_show_year, ep_number, ep_title, show_script]) + '\n'
                    self.current_tv_file.write(show_data)
                    tv_per_file_counter += 1

                    if tv_per_file_counter >= self.tv_shows_per_file:
                      tv_file_count += 1
                      self.increment_tv_import_file(tv_file_count)
                      tv_per_file_counter = 0
                  except Exception as e:
                    logging.error('create_tv_import_files() - episode loop: Error occurred while processing TV show ' + show_title + ', season ' + show_season + ', episode ' + show_season_ep + ': ' + str(e))
              except Exception as e:
                logging.error('create_tv_import_files() - season loop: Error occurred while processing TV show ' + show_title + ', season ' + show_season_dir + ': ' + str(e))
          except Exception as e:
            logging.error('create_tv_import_files() - show loop: Error occurred while processing TV show ' + show_dir + ': ' + str(e))
      except Exception as e:
        logging.error('create_tv_import_files() - letter loop: Error occurred while processing TV letter ' + letter + ': ' + str(e))

    logging.info('Finished TV file processing')
  
  def extract_movie_title_and_year_from_file_name(self, file_name):
    """Returns the title and year from a movie file name, e.g. 'Movie Title_1994.txt' -> 'Movie Title', '1994'
    """
    title = file_name[:]
    if title.lower().endswith('.txt'):
      title = title[:-4]
      last_underscore = title.rfind('_')
      if last_underscore > -1:
        return title[:last_underscore], title[last_underscore+1:]
      else:
        raise ValueError('File name has incorrect date format: ' + file_name)

      return title
    else:
      raise ValueError('File name in unsupported format: ' + file_name)
  
  def extract_tv_title_and_year_from_dir(self, show_dir):
    """Returns the title and year from a TV show directory name, e.g. 'TV Show Title_1994' -> 'TV Show Title', '1994'
    """
    title = show_dir[:]
    if title.find('_') > -1:
      last_underscore = title.rfind('_')
      return title[:last_underscore], title[last_underscore+1:]
    else:
      raise ValueError('TV show directory missing year information')
  
  def extract_tv_episode_number_and_title_from_file(self, file_name):
    """Returns the TV show episode number and title from a TV show file name, e.g. '1. Episode Title.txt' -> '1', 'Episode Title'
    """
    title = file_name[:]
    if title.lower().endswith('.txt'):
      title = title[:-4]
      separator = '. '
      ep_separator = title.find(separator)
      if ep_separator > -1:
        return title[:ep_separator], title[ep_separator+len(separator):]
    else:
      raise ValueError('File name in unsupported format: ' + file_name)
  
  def increment_movie_import_file(self, counter):
    if self.current_movie_file:
      self.current_movie_file.close()
    self.current_movie_file = open('pg_import_movie_' + self.start_time + '_' + str(counter) + '.txt', 'w')
  
  def increment_tv_import_file(self, counter):
    if self.current_tv_file:
      self.current_tv_file.close()
    self.current_tv_file = open('pg_import_tv_' + self.start_time + '_' + str(counter) + '.txt', 'w')

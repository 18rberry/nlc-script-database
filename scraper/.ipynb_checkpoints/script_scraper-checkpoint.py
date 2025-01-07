from bs4 import BeautifulSoup
import os
from urllib.request import urlopen
from concurrent.futures import ThreadPoolExecutor, as_completed
from time import strftime, time
import re
import logging
import scraper_constants


class ScriptScraper:
  def __init__(self, tv_scripts, letters, site_url, thread_count, download_directory, error_threshold=5):
    self.tv_scripts = tv_scripts
    self.letters = letters
    self.site_url = site_url
    self.scripts_url = ''
    self.thread_count = thread_count
    self.download_directory = download_directory
    self.log_file = 'scriptscraper_{time}.log'.format(time=strftime('%Y-%m-%d %H-%M'))
    self.ERROR_THRESHOLD = error_threshold

    logging.basicConfig(filename=self.log_file, format='%(levelname)s: %(message)s', level=logging.DEBUG)
  
  def scrape_site(self):
    logging.info('Starting scraping process:\n\tTV:{tv}\n\tLetters:{letters}'
                  .format(
                    tv=str(self.tv_scripts),
                    letters=str(self.letters)
                  )
                )
    start_time = time()

    if self.tv_scripts:
      self.scripts_url = self.site_url + '/tv_show_episode_scripts.php'
    else:
      self.scripts_url = self.site_url + '/movie_scripts.php'

    self.ensure_script_file_path(self.download_directory.split('/'))
    
    with ThreadPoolExecutor(self.thread_count) as executor:
      letter_results = {executor.submit(self.iterate_title_letter, letter): letter for letter in self.letters}
    for letter_result in as_completed(letter_results):
      try:
        letter = letter_results[letter_result]
        script_count, show_count, missing_dates = letter_result.result()
        if self.tv_scripts:
          logging.info('Shows for {letter} - {count}'.format(letter=letter, count=show_count))
        logging.info('Scripts for {letter} - {count}'.format(letter=letter, count=script_count))
        logging.info('Missing for {letter} - {missing}'.format(letter=letter, missing=missing_dates))
      except Exception as e:
        logging.error('scrape_site(): Error occurred for ' + letter + ': ' + str(e))
    
    total_time = time() - start_time
    logging.info('Total time: ' + str(total_time))
  
  def iterate_title_letter(self, letter):
    # Soupify the script page for each letter
    letter_page = urlopen(self.scripts_url + '?order=' + letter)
    letter_page_soup = BeautifulSoup(letter_page, 'lxml')

    # Find the number of pages for each letter
    letter_page_links = letter_page_soup.select('div.pagination a')
    if len(letter_page_links) > 0:
      letter_pages = int(letter_page_links[-1].get_text())
    else:
      letter_pages = 1

    script_count, show_count, missing_dates = self.iterate_letter_pages(letter, letter_pages, letter_page_soup)  
    return script_count, show_count, missing_dates
  
  def iterate_letter_pages(self, letter, num_pages, letter_page_soup):
    missing_dates = []
    current_page = 1
    show_count = 0
    script_count = 0
    error_count = 0

    while current_page <= num_pages:
      try:
        if current_page > 1:
          letter_page = urlopen(self.scripts_url + '?order=' + letter + '&page=' + str(current_page))
          letter_page_soup = BeautifulSoup(letter_page, 'lxml')
        
        title_links = letter_page_soup.select('a.script-list-item')
        for title_link in title_links:
          title_page = title_link['href']
          title = title_link.get_text()
          title_date = scraper_constants.DATE_TOKEN
          dates = re.findall(r'[(][\d]{4,4}[)]', title)
          if len(dates) > 0:
            # If a date in the format (####) exists then take the last one and remove from the title
            title_date = dates[-1][1:-1]
            title = title[:-7]
          else:
            # Make note of the title without a date on "Springfield, Springfield"
            missing_dates.append(title)
          
          if self.tv_scripts:
            added_scripts = self.scrape_tv_scripts(letter, title, title_date, title_page)
            script_count += added_scripts
          else:
            self.scrape_movie_scripts(letter, title, title_date, title_page)
            script_count += 1
          
          show_count += 1
          
        current_page += 1
      except Exception as e:
        logging.error('iterate_letter_pages(): Error occurred for ' + letter + ' on page ' + str(current_page) + ': ' + str(e))
        error_count += 1
        if error_count > self.ERROR_THRESHOLD:
          raise e
    
    return script_count, show_count, missing_dates
  
  def scrape_tv_scripts(self, letter, tv_show_title, tv_show_date, tv_episodes_page_url):
    script_count = 0
    season_error_count = 0
    ep_error_count = 0

    tv_episodes_page = urlopen(self.site_url + tv_episodes_page_url)
    tv_episodes_page_soup = BeautifulSoup(tv_episodes_page, 'lxml')

    season_divs = tv_episodes_page_soup.select('div.season-episodes')
    try:
      for season_div in season_divs:
        try:
          episode_links = season_div.select('a.season-episode-title')
          for episode_link in episode_links:
            episode_script_page_url = episode_link['href']
            episode_script_page = urlopen(self.site_url + '/' + episode_script_page_url)
            episode_script_page_soup = BeautifulSoup(episode_script_page, 'lxml')

            raw_script = episode_script_page_soup.find('div', class_='scrolling-script-container').get_text()
            clean_script = self.clean_script(raw_script)

            clean_title = self.clean_title(tv_show_title)
            season = season_div.find('h3').get_text()
            path_elements = self.download_directory.split('/') + \
                            [letter, clean_title + '_' + tv_show_date, season]
            self.ensure_script_file_path(path_elements)
            ep_path = '/'.join(path_elements)
            ep_filename = self.clean_title(episode_link.get_text()) + '.txt'

            self.save_script_file('/'.join([ep_path, ep_filename]), clean_script)
            script_count += 1
        except Exception as e:
          logging.error('scrape_tv_scripts() eps loop: Error occurred for TV show ' + tv_show_title + ': ' + str(e))
          ep_error_count += 1
          if ep_error_count > self.ERROR_THRESHOLD:
            logging.error('scrape_tv_scripts() eps loop: Too many errors for ' + tv_show_title + ': not downloaded')
            raise e
    except Exception as e:
      logging.error('scrape_tv_scripts() season loop: Error occurred for TV show ' + tv_show_title + ': ' + str(e))
      season_error_count += 1
      if season_error_count > self.ERROR_THRESHOLD:
        logging.error('scrape_tv_scripts() season loop: Too many errors for ' + tv_show_title + ': skipping')

    
    return script_count
  
  def scrape_movie_scripts(self, letter, movie_title, movie_date, movie_script_page_url):
    error_count = 0

    try:
      movie_script_page = urlopen(self.site_url + movie_script_page_url)
      movie_script_soup = BeautifulSoup(movie_script_page, 'lxml')

      raw_script = movie_script_soup.find('div', class_='scrolling-script-container').get_text()
      clean_script = self.clean_script(raw_script)

      path_elements = self.download_directory.split('/') + [letter]
      self.ensure_script_file_path(path_elements)
      movie_path = '/'.join(path_elements)
      movie_filename = self.clean_title(movie_title) + '_' + str(movie_date) + '.txt'

      self.save_script_file('/'.join([movie_path, movie_filename]), clean_script)
    except Exception as e:
      logging.error('scrape_movie_scripts(): Error occurred for movie ' + movie_title + ': ' + str(e))
      error_count += 1
      if error_count > self.ERROR_THRESHOLD:
        logging.error('scrape_move_scripts(): Too many errors for movie ' + movie_title + ': not downloaded')
        raise e
  
  def clean_title(self, raw_title):
    clean_title = (raw_title + '.')[:-1]
    clean_title = clean_title.strip()
    clean_title = clean_title.replace('\\', scraper_constants.BACKSLASH)
    clean_title = clean_title.replace('/', scraper_constants.SLASH)
    clean_title = clean_title.replace(':', scraper_constants.COLON)
    clean_title = clean_title.replace('*', scraper_constants.STAR)
    clean_title = clean_title.replace('<', scraper_constants.LESS_THAN)
    clean_title = clean_title.replace('>', scraper_constants.GREATER_THAN)
    clean_title = clean_title.replace('?', scraper_constants.QUESTION_MARK)
    clean_title = clean_title.replace('|', scraper_constants.PIPE)
    return clean_title
  
  def clean_script(self, raw_script):
    clean_script = re.sub(r'\s+', ' ', raw_script).strip()
    clean_script = clean_script.replace('\\', '')
    return clean_script
  
  def ensure_script_file_path(self, path_elements):
    if path_elements is not None and len(path_elements) > 0:
      current_path = ''
      for path_element in path_elements:
        if current_path == '':
          current_path = path_element
        else:
          current_path = '/'.join([current_path, path_element])
        if not os.path.exists(current_path):
          os.mkdir(current_path)
  
  def save_script_file(self, file_name, script):
    if not os.path.isfile(file_name):
      with open(file_name, 'w+', encoding='utf-8') as handle:
        handle.write(script)
        handle.close()
    else:
      logging.info('save_script_file(): File exists so skipping save: ' + file_name)

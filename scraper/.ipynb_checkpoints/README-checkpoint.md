# NLC Script Database: Scraper
There are three main processes in the scraping process:
- script_scraper.py
- script_file_date_fixer.py
- pg_import_creator.py

## script_scraper.py
This file scrapes TV and movie scripts from [Springfield, Springfield](https://www.springfieldspringfield.co.uk/) by going through its A-Z table of contents and systematically retrieving the text.\
The corresponding `run_script_scraper.py` file is used to run the scraping process and requires the following parameters to be set in the file:
- `tv_scripts`: `True` for TV shows, `False` for movies (the table of contents on the Springfield, Springfield site is in a different format for each type)
- `script_letters`: Array of which starting letters to run the process on. Should only contain `0` or `A` - `Z`.
- `site_url`: String URL of the Springfield, Springfield site - `'https://www.springfieldspringfield.co.uk'`
- `download_directory`: The local directory to download the script text files.

Movie files are downloaded in the following format:
- Starting Letter 1
  - Movie 1_year
  - Movie 2_year
  - Movie 3_year
- Starting Letter 2
  - Movie a_year
  - Movie b_year
  - Movie c_year

TV files are downloaded in the following format:
- Starting Letter 1
  - TV Show 1_year
    - Season 1
      - Episode 1
      - Episode 2
    - Season 2
      - Episode 1
      - Episode 2
  - TV Show 2_year
    - Season 1
      - Episode 1
- Starting Letter 2
  - TV Show a_year
    - Season 1
      - Episode 1

## script_file_date_fixer.py
Some of the TV shows and movies on the Springfield, Springfield site are missing the year information. For these items, a special token to indicate the missing information is appended to the title rather than the year. These dates must be collected from sources such as IMDB.com and recorded in a separate data file to then be used in the date fixing process.\
The corresponding `run_script_file_date_fixer.py` file is used to run the date fixing process and requires the following parameters to be set in the file:
- `script_dir`: The directory holding the TV and movie scripts on the local machine
- `date_fix_file`: File holding the missing year information for TV shows and movies. Each line in the file should contain a title, \t (tab), and year.

## pg_import_creator.py
Once the scripts are downloaded and dates fixed on a development machine, they are converted into text files that can be directly imported into PostgreSQL efficiently.\
The corresponding `run_pg_import_creator.py` file is used to run the import file creation process and requires the following parameters to be set in the file:
- `tv_dir`: The local directory holding the TV script directory structure and files
- `movie_dir`: The local directory holding the movie script directory structure and files

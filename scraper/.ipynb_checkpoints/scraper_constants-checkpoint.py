import re


BACKSLASH = '==BSLASH=='
SLASH = '==SLASH=='
COLON = '==COLON=='
STAR = '==STAR=='
LESS_THAN = '==LT=='
GREATER_THAN = '==GT=='
QUESTION_MARK = '==Q=='
PIPE = '==PIPE=='
DATE_TOKEN = '==DATE=='


def clean_script_title(script_title):
  """Cleans up a TV/movie title to save it as a file name.
  """
  clean_title = re.sub(r'\s+', ' ', script_title).strip()
  clean_title = clean_title.replace('\\', BACKSLASH)
  clean_title = clean_title.replace('/', SLASH)
  clean_title = clean_title.replace(':', COLON)
  clean_title = clean_title.replace('*', STAR)
  clean_title = clean_title.replace('<', LESS_THAN)
  clean_title = clean_title.replace('>', GREATER_THAN)
  clean_title = clean_title.replace('?', QUESTION_MARK)
  clean_title = clean_title.replace('|', PIPE)

  return clean_title

def remake_script_title(clean_title):
  """Replaces special characters in a TV/movie file name back to the friendly title.
  """
  script_title = clean_title[:]
  script_title = script_title.replace(BACKSLASH, '\\')
  script_title = script_title.replace(SLASH, '/')
  script_title = script_title.replace(COLON, ':')
  script_title = script_title.replace(STAR, '*')
  script_title = script_title.replace(LESS_THAN, '<')
  script_title = script_title.replace(GREATER_THAN, '>')
  script_title = script_title.replace(QUESTION_MARK, '?')
  script_title = script_title.replace(PIPE, '|')

  return script_title

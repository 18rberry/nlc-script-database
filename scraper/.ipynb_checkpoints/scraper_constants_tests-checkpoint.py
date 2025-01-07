import unittest
import scraper_constants


class ScraperConstantsTests(unittest.TestCase):
  def test_clean_script_title_replacements(self):
    # Arrange
    script_title = '\\/:*<>?|.txt'
    expected = ''.join([
                        scraper_constants.BACKSLASH,
                        scraper_constants.SLASH,
                        scraper_constants.COLON,
                        scraper_constants.STAR,
                        scraper_constants.LESS_THAN,
                        scraper_constants.GREATER_THAN,
                        scraper_constants.QUESTION_MARK,
                        scraper_constants.PIPE,
                        '.txt'
    ])

    # Act
    clean_title = scraper_constants.clean_script_title(script_title)

    # Assert
    self.assertEqual(clean_title, expected)
  
  def test_clean_script_title_whitespaces(self):
    # Arrange
    script_title = '1.\tWhy so many \ttabs .txt'
    expected = '1. Why so many tabs .txt'

    # Act
    clean_title = scraper_constants.clean_script_title(script_title)

    # Assert
    self.assertEqual(clean_title, expected)
  
  def test_remake_script_title(self):
    # Arrange
    file_name = ''.join([
                        scraper_constants.BACKSLASH,
                        scraper_constants.SLASH,
                        scraper_constants.COLON,
                        scraper_constants.STAR,
                        scraper_constants.LESS_THAN,
                        scraper_constants.GREATER_THAN,
                        scraper_constants.QUESTION_MARK,
                        scraper_constants.PIPE,
                        '.txt'
    ])
    expected = '\\/:*<>?|.txt'

    # Act
    script_title = scraper_constants.remake_script_title(file_name)

    # Assert
    self.assertEqual(script_title, expected)


if __name__ == '__main__':
  unittest.main()
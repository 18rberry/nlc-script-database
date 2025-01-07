import script_file_date_fixer


def main():
  script_dir = ''
  date_fix_file = ''

  print('Starting date fix process')
  date_fixer = script_file_date_fixer.ScriptFileDateFixer(script_dir, date_fix_file)
  date_fixer.fix_dates()
  print('Dates fixed. See log for details.')


if __name__ == '__main__':
  main()

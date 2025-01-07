from django.db import models
from django.contrib.postgres.search import SearchVectorField
from django.contrib.postgres.indexes import GinIndex, BTreeIndex


class ScriptMigration(models.Model):
  title = models.TextField()
  script_type = models.CharField(max_length=1)
  year_text = models.TextField()
  season_text = models.TextField(null=True)
  episode_text = models.TextField(null=True)
  episode_title = models.TextField(null=True)
  script_content = models.TextField()

  def __str__(self):
    return self.title


class Script(models.Model):
  title = models.TextField()
  script_type = models.CharField(max_length=1)
  year = models.IntegerField()
  season = models.IntegerField(null=True)
  episode = models.TextField(null=True)
  episode_title = models.TextField(null=True)
  script_content = models.TextField()
  search_content = SearchVectorField(null=True)

  def __str__(self):
    return format_script_title(self)

  class Meta:
      indexes = [BTreeIndex(fields=["year"]), BTreeIndex(fields=["script_type"]), GinIndex(fields=["search_content"])]
      ordering = ['title']


def format_script_title(script_obj):
  title = None
  if script_obj:
    if script_obj.script_type == 'T':
      title = '{show} (Season {season}, Episode \"{episode}\", {year})'.format(show=script_obj.title, season=str(script_obj.season), episode=script_obj.episode_title, year=str(script_obj.year))
    elif script_obj.script_type == 'M':
      title = '{show} ({year})'.format(show=script_obj.title, year=str(script_obj.year))
  else:
    title = ''

  return title

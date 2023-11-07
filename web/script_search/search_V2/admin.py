from django.contrib import admin
from .models import Script, ScriptMigration


# Create ModelAdmin classes to customize interacting with models
class ScriptAdmin(admin.ModelAdmin):
    list_display = ('title', 'script_type', 'year', 'season',
                    'episode', 'episode_title', 'genre_text')
    search_fields = ['title', 'year', 'episode_title']
    list_filter = ('script_type', 'year', 'genre_text')


# Register custom models to be able to view on admin site
admin.site.register(Script, ScriptAdmin)
admin.site.register(ScriptMigration)

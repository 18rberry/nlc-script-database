from django.contrib import messages
from django.contrib.auth import logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import Error
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.shortcuts import render
from django.views import generic
from .models import Script
from .forms import SearchForm
from time import time
import csv
import json
from re import compile, sub


def index(request):
    """Home page of the USC Norman Lear Center. No login required.
    """
    return render(request, 'search/v2index.html')


@login_required
def search(request):
    """Script search page. Login and search.can_search permission required.
    """
    search_context = {}
    if request.method == 'POST':
        try:
            start_time = time()
            form = SearchForm(request.POST)
            # print("query",form.data, form.is_valid())
            # print(form.errors)
            if form.is_valid():

                if 'search' in form.data:
                    # print("query",form.data)

                    # User performed a search
                    search_params = {}
                    search_params['search_terms'] = create_search_terms_query(
                        form.cleaned_data['search_terms'].strip())
                    search_params['year_filter_low'] = form.cleaned_data['year_filter_low'] or '1900-01-01'
                    search_params['year_filter_high'] = form.cleaned_data['year_filter_high'] or '2100-01-01'
                    search_params['script_type'] = form.cleaned_data['script_type']
                    search_params['genres_type'] = form.cleaned_data['genre_filter']
                    search_params['us_only'] = form.cleaned_data['us_only_filter']
                    query = create_search_query(search_params)
                    results = Script.objects.raw(query, search_params)

                    search_results = create_search_context_from_results(
                        results)
                    search_context['results'] = search_results

                    elapsed = time() - start_time
                    search_context['elapsed'] = '%.4f' % elapsed

                    # Cache the last results for export
                    if 'search_results' in search_results:
                        request.session['last_results'] = search_results['search_results']
                    else:
                        request.session['last_results'] = None
                elif 'export' in form.data:
                    checked_ids = request.POST.getlist('chk_result')
                    response = HttpResponse(content_type='text/csv')
                    response['Content-Disposition'] = 'attachment; filename=scripts.csv'
                    selected_rows = [row for row in request.session['last_results'] if str(
                        row['id']) in checked_ids]
                    writer = csv.writer(response)
                    writer.writerow(['Script Type', 'Title', 'Year', 'Season',
                                    'Episode', 'Country', 'Release Date', 'Genre', 'Network', 'URL', 'Mentions', 'Mentions_flat'])
                    for selected_row in selected_rows:
                        writer.writerow(['TV' if selected_row['script_type'] == 'T' else 'Movie',
                                        selected_row['title'],
                                        selected_row['year'],
                                        selected_row['season'] if selected_row['script_type'] == 'T' else '',
                                        selected_row['episode'] if selected_row['script_type'] == 'T' else '',
                                        selected_row['country'],
                                        selected_row['release_date'],
                                        ', '.join(selected_row['genre_text']),
                                         ', '.join(selected_row['network']),
                                         request.build_absolute_uri(
                                            'v2/search/{id}'.format(id=selected_row['id'])),
                                         clean_cr_mentions_for_export(
                                            selected_row['headline']),
                                         clean_mentions_for_export(
                                            selected_row['headline'])
                                         ])

                    return response
        except Error:
            search_context['errors'] = 'There was an error with the search. Please check your search query and try again.'
        except Exception:
            search_context['errors'] = 'An error occurred. Please try again later.'
    else:
        form = SearchForm(initial={'script_type': 'All'})

    search_context['form'] = form
    return render(request, 'search/v2searchscripts.html', context=search_context)


class ScriptDetailView(LoginRequiredMixin, generic.DetailView):
    model = Script
    template_name = 'search/v2viewscript.html'


@login_required
def logout_search(request):
    logout(request)
    return render(request, 'registration/logout.html')


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Keeps the user logged in
            messages.success(
                request, 'Your password was successfully updated!')
            return redirect('search:changepassword')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'registration/changepassword.html', {
        'form': form
    })


@login_required
def search_query_help(request):
    return render(request, 'search/v2queryhelp.html')


def create_search_terms_query(search_terms):
    whitespace_pattern = compile('\s+')
    clean_search_terms = whitespace_pattern.sub(' ', search_terms)
    single_terms = clean_search_terms.split(' ')
    print(single_terms)
    if '&' not in single_terms and \
        '|' not in single_terms and \
        '<' not in single_terms and \
            len(single_terms) > 1:
        return ' | '.join(single_terms)
    else:
        return search_terms


def create_search_query(search_params):
    query_template = """SELECT
                        id,
                        title,
                        year,
                        script_type,
                        season,
                        episode,
                        genre_text,
                        country,
                        category,
                        network,
                        release_date,
                        ts_rank("search_content", to_tsquery('english', %(search_terms)s)) as "rank",
                        ts_headline('english', script_content,
                                to_tsquery('english', %(search_terms)s),
                                'StartSel=<u><strong>,StopSel=</u></strong>,MaxFragments=10,' ||
                                'FragmentDelimiter=;#,MaxWords=10,MinWords=5') as "headline"
                      FROM
                        "search_V2_script"
                      WHERE
                        search_content @@ to_tsquery('english', %(search_terms)s)
                        AND release_date >= %(year_filter_low)s
                        AND release_date <= %(year_filter_high)s
                        {script_type_filter}
                        {genres_filter}
                        {us_only_filter}
                      ORDER BY rank DESC
                      LIMIT 20000
  """

    if search_params['script_type'] == 'T' or search_params['script_type'] == 'M':
        script_type_filter = 'AND script_type=\'{script_type}\''.format(
            script_type=search_params['script_type'])
    else:
        script_type_filter = ''

    if search_params['genres_type'] != '':
        genres_filter = 'AND genre_text::jsonb @>\'[{genres_type}]\'::jsonb'.format(
            genres_type=','.join(['\"'+genre+'\"' for genre in search_params['genres_type']]))
    else:
        genres_filter = ''

    if search_params['us_only'] != 'False':
        us_only_filter = 'AND (country=\'United States of America\' OR country=\'US\')'
    else:
        us_only_filter = ''

    return query_template.format(script_type_filter=script_type_filter, genres_filter=genres_filter, us_only_filter=us_only_filter)


def create_search_context_from_results(results):
    """Converts SQL query results to dictionary for HTML template.
    """
    search_results = {}
    if results:
        search_results['search_results'] = []
        search_results['script_hits'] = len(results)
        search_results['snippet_hits'] = 0

        for result in results:
            search_result = {}
            search_result['id'] = result.id
            search_result['title'] = result.title
            search_result['script_type'] = result.script_type
            search_result['genre_text'] = result.genre_text
            search_result['network'] = result.network
            search_result['season'] = result.season
            search_result['episode'] = result.episode
            search_result['year'] = result.year
            search_result['release_date'] = str(result.release_date)
            search_result['rank'] = result.rank
            search_result['country'] = result.country
            search_result['category'] = result.category
            snippets = result.headline.split(';#')
            search_result['headline'] = snippets
            search_results['snippet_hits'] += len(snippets)
            search_results['search_results'].append(search_result)
    return search_results


def clean_mentions_for_export(mentions):
    cleaned_mentions = ';#'.join(mentions)
    cleaned_mentions = cleaned_mentions.replace('<b>', '').replace('</b>', '')

    return cleaned_mentions


def clean_cr_mentions_for_export(mentions):
    """Formats mentions with carriage returns for Google Sheets.
    """
    quoted_mentions = []
    for mention in mentions:
        quoted_mentions.append('{q}{m}{q}'.format(q='"',
                                                  m=mention.replace('"', '\'').replace(
                                                      '<b>', '').replace('</b>', '')
                                                  )
                               )
    cleaned_cr_mentions = ', CHAR(10), CHAR(10), '.join(quoted_mentions)
    cleaned_cr_mentions = cleaned_cr_mentions
    cleaned_cr_mentions = '=CONCATENATE(' + cleaned_cr_mentions + ')'

    return cleaned_cr_mentions

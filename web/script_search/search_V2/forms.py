from django import forms


class SearchForm(forms.Form):
    class DateInput(forms.DateInput):
        input_type = 'date'
        is_required = False

    year_choices = [('', '')]
    year_choices += [(x, x) for x in reversed(range(1920, 2021))]
    genre_choices = [('Action & Adventure', 'Action & Adventure'),
                     ('Action', 'Action'),
                     ('Adventure', 'Adventure'),
                     ('Animation', 'Animation'),
                     ('Comedy', 'Comedy'),
                     ('Crime', 'Crime'),
                     ('Documentary', 'Documentary'),
                     ('Drama', 'Drama'),
                     ('Family', 'Family'),
                     ('Fantasy', 'Fantasy'),
                     ('History', 'History'),
                     ('Horror', 'Horror'),
                     ('Kids', 'Kids'),
                     ('Music', 'Music'),
                     ('Musical', 'Musical'),
                     ('Mystery', 'Mystery'),
                     ('News', 'News'),
                     ('Reality', 'Reality'),
                     ('Romance', 'Romance'),
                     ('Sci-Fi & Fantasy', 'Sci-Fi & Fantasy'),
                     ('Science Fiction', 'Science Fiction'),
                     ('Soap', 'Soap'),
                     ('TV Movie', 'TV Movie'),
                     ('Talk', 'Talk'),
                     ('Thriller', 'Thriller'),
                     ('War & Politics', 'War & Politics'),
                     ('War', 'War'),
                     ('Western', 'Western')]
    script_type_choices = [('All', 'All'), ('T', 'TV'), ('M', 'Movie')]
    country_filter_choices = [(False, 'False'), (True, 'True')]
    search_terms = forms.CharField(min_length=1, max_length=400, strip=True, required=True,
                                   widget=forms.TextInput(attrs={'class': 'form-control border-0 bg-light', 'placeholder': 'What are you searching for ?'}))
    year_filter_low = forms.DateField(widget=DateInput(), required=False)
    year_filter_high = forms.DateField(widget=DateInput(), required=False)
    genre_filter = forms.MultipleChoiceField(
        choices=genre_choices, required=False, widget=forms.CheckboxSelectMultiple(attrs={'aria-labelledby': 'dropdownMenuButton1'}))
    script_type = forms.ChoiceField(choices=script_type_choices, widget=forms.RadioSelect(
        attrs={'class': 'form-check-input p-0'}), required=True)
    us_only_filter = forms.ChoiceField(
        choices=country_filter_choices, required=False, widget=forms.CheckboxInput())

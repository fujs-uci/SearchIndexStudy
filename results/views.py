from django.shortcuts import render
from .forms import SearchQuery
from results.search_index import SearchIndexWrapper
from .models import Movies


def index(request):
    """
    Have a search bar
        search key words
        return ranked results

    addition features
        display results while typing search
        pagination
    """
    search_index = SearchIndexWrapper()
    search_results = None
    if request.method == "POST":
        search_query = SearchQuery(request.POST)
        search_results = search_index.lookup(search_query['query'].value(), limit=10)
        search_results = Movies.objects.filter(id__in=search_results)
    else:
        search_query = SearchQuery()
    template = "results/index.html"
    context = {'search_query': search_query,
               'search_results': search_results,}
    return render(request, template, context)

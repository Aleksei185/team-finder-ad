from django.core.paginator import Paginator

from .constants import ITEMS_PER_PAGE


def paginate_queryset(request, queryset, items_per_page=ITEMS_PER_PAGE):
    paginator = Paginator(queryset, items_per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    query_params = request.GET.copy()
    if 'page' in query_params:
        del query_params['page']
    query_prefix = query_params.urlencode()
    if query_prefix:
        query_prefix += '&'

    return page_obj, query_prefix

from django.core.paginator import Page, Paginator

from .constants import PAGE_SIZE


def paginate(request, queryset, per_page: int = PAGE_SIZE) -> Page:
    return Paginator(queryset, per_page).get_page(request.GET.get('page'))

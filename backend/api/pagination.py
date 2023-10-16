from rest_framework.pagination import PageNumberPagination


class LimitPagination(PageNumberPagination):
    page_size = 6
    max_page_size = 6
    page_size_query_param = 'limit'
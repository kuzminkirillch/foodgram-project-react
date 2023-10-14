from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination


class LimitPagination(PageNumberPagination):
    page_size = 6
    max_page_size = 6
    page_size_query_param = 'limit'

# class LimitPagination(LimitOffsetPagination):
#     page_size = 6
#     page_size_query_param = 'limit'

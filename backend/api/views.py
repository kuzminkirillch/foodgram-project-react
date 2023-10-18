from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from reciepts.models import (Favorite, Ingredient, Reciept, Routing,
                             ShoppingList, Tags)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response
from user.models import Subscribe

from .filters import IngredientFilter, RecieptFilter
from .mixins import ListRetrieve
from .pagination import LimitPagination
from .permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from .serializers import (IngredientSerializer, RecieptCreateSerializer,
                          RecieptReadSerializer, RecieptShortSerializer,
                          SubscribeSerializer, TagSerializer, UsersSerializer)

User = get_user_model()


class IngredientViewSet(ListRetrieve):
    """Функция для модели ингредиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    search_fields = ['^name', ]
    pagination_class = None


class TagViewSet(ListRetrieve):
    """Функция для модели тегов."""
    queryset = Tags.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = None


class RecieptViewSet(viewsets.ModelViewSet):
    """Функция для модели рецепта."""
    queryset = Reciept.objects.all()
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecieptFilter
    pagination_class = LimitPagination

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecieptReadSerializer
        return RecieptCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def add_obj(self, model, user, pk):
        if model.objects.filter(author=user, reciept__id=pk).exists():
            return Response({'errors': 'Такой рецепт уже есть'},
                            status=status.HTTP_400_BAD_REQUEST)
        reciept = get_object_or_404(Reciept, id=pk)
        model.objects.create(author=user, reciept=reciept)
        serializer = RecieptShortSerializer(reciept)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_obj(self, model, user, pk):
        obj = model.objects.filter(author=user, reciept__pk=pk)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'errors': 'Рецепт удалён'},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        if request.method == 'POST':
            return self.add_obj(Favorite, request.user, pk)
        return self.delete_obj(Favorite, request.user, pk)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            return self.add_obj(ShoppingList, request.user, pk)
        return self.delete_obj(ShoppingList, request.user, pk)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        string = f'Список покупок {request.user.username}\n'
        ingredients = Routing.objects.filter(
            reciept__shopping__author=request.user
        ).values(
            'ingredient__name', 'ingredient__value_unit'
        ).annotate(amount=Sum('amount'))
        for num, i in enumerate(ingredients):
            string += (
                f'\n* {i["ingredient__name"]} — {i["amount"]} '
                f'{i["ingredient__value_unit"]}'
            )
            if num < ingredients.count() - 1:
                string += '; '
        filename = f'{request.user.username}_string.txt'
        response = HttpResponse(
            f'{string} \n\nСпасибо за покупку!',
            content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename="{filename}'
        return response


class CustomUserViewSet(UserViewSet):
    """Функция для модели пользователя."""
    queryset = User.objects.all()
    serializer_class = UsersSerializer

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated],
    )
    def subscribe(self, request, **kwargs):
        user = request.user
        author_id = self.kwargs['id']
        author = get_object_or_404(User, id=author_id)

        if request.method == 'POST':
            if user == author:
                return Response({
                    'errors': 'Нельзя подписаться на самого себя'
                }, status=status.HTTP_400_BAD_REQUEST)
            if user.subscriber.filter(author=author).exists():
                return Response({
                    'errors': 'Вы уже подписаны на этого пользователя'
                }, status=status.HTTP_400_BAD_REQUEST)
            serializer = SubscribeSerializer(
                author, data=request.data, context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            Subscribe.objects.create(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            if user == author:
                return Response({
                    'errors': 'Вы не можете отписаться от самого себя'
                }, status=status.HTTP_400_BAD_REQUEST)
            sub = Subscribe.objects.filter(user=user, author=author)
            if sub.exists():
                sub.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({
                'error': 'Вы уже отписались'
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(following__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscribeSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

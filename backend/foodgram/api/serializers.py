from django.db import transaction
from djoser.serializers import (
    UserCreateSerializer as DjoserUserCreateSerializer
)
from djoser.serializers import UserSerializer as DjoserUserSerializer
from drf_extra_fields.fields import Base64ImageField
from reciepts.models import Ingredient, Routing, Reciept, Tags
from rest_framework import serializers
from rest_framework.fields import IntegerField, SerializerMethodField
from rest_framework.relations import PrimaryKeyRelatedField
from user.models import Subscribe, User


class UserCreateSerializer(DjoserUserCreateSerializer):

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'password',)


class UsersSerializer(DjoserUserSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name', 'is_subscribed',)

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        return not user.is_anonymous and Subscribe.objects.filter(
            user=user, author=obj).exists()


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tags
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'value_unit',)


class RoutingReadSerializer(serializers.ModelSerializer):
    id = IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.value_unit')

    class Meta:
        model = Routing
        fields = ('id', 'name', 'measurement_unit', 'amount',)


class RecieptReadSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    ingredients = RoutingReadSerializer(
        many=True, source='ingredient_list')
    author = UsersSerializer()
    image = Base64ImageField()
    is_favorited = SerializerMethodField(read_only=True)
    is_in_shopping_cart = SerializerMethodField(read_only=True)

    class Meta:
        model = Reciept
        fields = ('id', 'tags', 'author',
                  'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'image',
                  'name', 'text', 'cooking_time',)

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        return not user.is_anonymous and user.favorite.filter(
            reciept=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        return (not user.is_anonymous
                and user.shopping.filter(reciept=obj).exists())


class RoutingCreateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = Routing
        fields = ('id', 'amount')


class RecieptCreateSerializer(serializers.ModelSerializer):
    ingredients = RoutingCreateSerializer(many=True)
    tags = PrimaryKeyRelatedField(queryset=Tags.objects.all(), many=True)
    author = UsersSerializer(read_only=True)
    image = Base64ImageField()

    class Meta:
        model = Reciept
        fields = ('id', 'tags', 'author', 'ingredients',
                  'image', 'name', 'text', 'cooking_time',)

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        tags = self.initial_data.get('tags')
        list = []
        if not ingredients:
            raise serializers.ValidationError(
                {'ingredients': 'Выберите ингридиент'})
        for ingredient in ingredients:
            amount = ingredient['amount']
            if ingredient['id'] in list:
                raise serializers.ValidationError({
                    'ingredient': 'Ингредиент уже выбран'
                })
            list.append(ingredient['id'])
            if int(amount) < 1:
                raise serializers.ValidationError({
                    'amount': 'Выберите ингридиент'
                })
        if not tags:
            raise serializers.ValidationError(
                {'tags': 'Не выбран тэг'})
        return data

    def create_ingredients(self, ingredients, reciept):
        for ingredient in ingredients:
            print(ingredient)
            Routing.objects.bulk_create(
                [Routing(
                    ingredient=Ingredient.objects.get(id=ingredient['id']),
                    reciept=reciept,
                    amount=ingredient['amount']
                )
                ]
            )

    @transaction.atomic
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        reciept = Reciept.objects.create(**validated_data)
        reciept.tags.set(tags)
        self.create_ingredients(ingredients, reciept)
        return reciept

    @transaction.atomic
    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance = super().update(instance, validated_data)
        instance.tags.clear()
        instance.tags.set(tags)
        instance.ingredients.clear()
        self.create_ingredients(ingredients=ingredients, reciept=instance)
        instance.save()
        return instance

    def to_representation(self, instance):
        return RecieptReadSerializer(instance, context={
            'request': self.context.get('request')
        }).data


class RecieptShortSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Reciept
        fields = ('id', 'name', 'image', 'cooking_time',)


class SubscribeSerializer(UsersSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(UsersSerializer.Meta):
        fields = UsersSerializer.Meta.fields + ('recipes', 'recipes_count')
        read_only_fields = UsersSerializer.Meta.fields

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('reciepts_limit')
        queryset = obj.reciept.all()
        if limit:
            queryset = queryset[:int(limit)]
        return RecieptShortSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return obj.reciept.count()

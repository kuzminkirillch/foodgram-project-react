from django.contrib import admin

from .models import Favorite, Ingredient, Reciept, Routing, ShoppingList, Tags


class RoutingInline(admin.TabularInline):
    """
    Админ-зона технологической карты - здесь добавляются ингридиенты
    и описывается рецепт.
    """
    model = Routing
    extra = 1


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """
    Админ-зона ингридентов для рецептов.
    """
    list_display = ('name', 'value_unit')
    list_filter = ('name',)


@admin.register(Tags)
class TagsAdmin(admin.ModelAdmin):
    """
    Админ-зона тегов.
    """
    list_display = ('name', 'color')


@admin.register(Reciept)
class RecieptAdmin(admin.ModelAdmin):
    """
    Админ-зона рецептов.
    """
    list_display = ('name', )
    list_filter = ('author', 'name', 'tags',)
    inlines = (RoutingInline, )


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """
    Админ-зона избранных рецептов.
    """
    list_display = ('author', 'reciept')


@admin.register(ShoppingList)
class ShoppingListeAdmin(admin.ModelAdmin):
    """
    Админ-зона покупок.
    """
    list_display = ('author', 'reciept')

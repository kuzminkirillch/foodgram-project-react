from django.contrib import admin

from .models import Favorite, Ingredient, Reciept, Routing, ShoppingList, Tags


class RoutingInline(admin.TabularInline):
    model = Routing
    extra = 1


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'value_unit')
    list_filter = ('name',)


@admin.register(Tags)
class TagsAdmin(admin.ModelAdmin):
    list_display = ('name', 'color')


@admin.register(Reciept)
class RecieptAdmin(admin.ModelAdmin):
    list_display = ('name', )
    list_filter = ('author', 'name', 'tags',)
    inlines = (RoutingInline, )


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('author', 'reciept')


@admin.register(ShoppingList)
class ShoppingListeAdmin(admin.ModelAdmin):
    list_display = ('author', 'reciept')

from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAuthorOrReadOnly(BasePermission):
    """
    Неавторизованным пользователям доступен только просмотр контента.
    Если пользователь является администратором
    или автором рецепта, то ему доступны остальные методы.
    """
    def has_permission(self, request, view):
        return (request.method in SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        # return obj.author == request.user
        return (request.method in SAFE_METHODS
                or obj.author == request.user)


class IsAdminOrReadOnly(BasePermission):
    """
    Неавторизованным пользователям доступен только просмотр контента.
    Если пользователь является администратором
    или автором рецепта, то ему доступны остальные методы.
    """
    def has_permission(self, request, view):
        return (request.method in SAFE_METHODS
                or request.user.is_staff)

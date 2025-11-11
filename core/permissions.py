# permissions.py (new file in the app directory)
from rest_framework.permissions import BasePermission, IsAuthenticated
from django.db.models import Q

class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.groups.filter(name='admin').exists())

class IsDataCollector(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.groups.filter(name='data_collector').exists())

class IsSuperAdminOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return IsSuperAdmin().has_permission(request, view) or IsAdmin().has_permission(request, view)

class IsSuperAdminOrDataCollector(BasePermission):
    def has_permission(self, request, view):
        return IsSuperAdmin().has_permission(request, view) or IsDataCollector().has_permission(request, view)

class IsSuperAdminOrAdminOrDataCollector(BasePermission):
    def has_permission(self, request, view):
        return (
            IsSuperAdmin().has_permission(request, view) or
            IsAdmin().has_permission(request, view) or
            IsDataCollector().has_permission(request, view)
        )
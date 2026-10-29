from django.contrib import admin

from outpost.django.base.admin import ReadOnlyAdminMixin

from . import models


@admin.register(models.User)
class UserAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = ("person__last_name", "person__first_name", "person__email", "person__username")
    list_display_links = ("person__first_name", "person__last_name")
    search_fields = ("person__first_name", "person__last_name", "person__email", "person__username")


@admin.register(models.Person)
class PersonAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = ("person__last_name", "person__first_name", "academic", "pure_user")
    list_display_links = ("person__first_name", "person__last_name")
    search_fields = ("person__first_name", "person__last_name")
    list_filter = ("academic", "pure_user")


@admin.register(models.PersonOrganization)
class PersonOrganizationAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = ("person__last_name", "person__first_name", "organization__name", "start_date", "employee")
    list_display_links = ("person__first_name", "person__last_name")
    search_fields = ("person__first_name", "person__last_name")
    list_filter = ("employee",)
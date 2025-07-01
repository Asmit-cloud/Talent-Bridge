"""
Responsible for registering the SkillSwap_Network application's models with the Django admin interface.

By registering a model here, you make it accessible and manageable through the Django admin site (accessible at "/admin/").
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, AppRequirements, Skill, ProficiencyLevel, UserOfferedSkill, UserNeededSkill

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    """

    list_display = ("username", "is_active", "is_staff", "is_superuser", "last_login", "date_joined")
    search_fields = ("username",)
    ordering = ("username",)

    fieldsets = (
        (None, {
            "fields": ("username", "password")
        }),
        ("Permissions", {
            "fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")
        }),
        #("Important dates", {
            #"fields": ("last_login", "date_joined")
        #}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "password", "password2"),
        }),
    )


@admin.register(AppRequirements)
class AppRequirementsAdmin(admin.ModelAdmin):
    """
    """

    list_display = ("user", "bio", "location")
    search_fields = ("user__username", "location")
    list_filter = ("location",)
    
    fieldsets = (
        (None, {
            "fields": ("user", "bio", "location")
        }),
    )


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    """
    """

    list_display = ("name",)
    search_fields = ("name",)


@admin.register(ProficiencyLevel)
class ProficiencyLevelAdmin(admin.ModelAdmin):
    """
    """

    list_display = ("name", "proficiency_level_order")
    ordering = ("proficiency_level_order",)


@admin.register(UserOfferedSkill)
class UserOfferedSkillAdmin(admin.ModelAdmin):
    """
    """

    list_display = ("user", "skill", "proficiency_level", "description")
    list_filter = ("proficiency_level", "skill")
    search_fields = ("user__username", "skill__name", "description")


@admin.register(UserNeededSkill)
class UserNeededSkillAdmin(admin.ModelAdmin):
    """
    """

    list_display = ("user", "skill", "proficiency_level", "description")
    list_filter = ("proficiency_level", "skill")
    search_fields = ("user__username", "skill__name", "description")

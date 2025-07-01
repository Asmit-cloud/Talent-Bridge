"""
URL configuration for the SkillSwap_Network application.

In a nutshell: When an user navigates to this specific URL prefix associated with this app, here's the Python code (the view) that should handle that request.

By examining the 'urlpatterns' list in this file, you can see all the avialable URL endpoints provided by the SkillSwap_Network application and the views that handle them.
"""

from django.contrib.auth.decorators import login_required
from django.urls import path, include # Import the "path" function from "django.urls"
from . import views # Import the "views" module from the current directory (".")

# "urlpatterns" - A list that defines the URL patterns of the SkillSwap_Network app
urlpatterns = [
    path("splash/", views.splash_view, name="splash"),
    # The following URL pattern maps the URL "login\" to the "login_view" function.
    # The name "login" is given, so that it can be used in templates (e.g., "{% url 'login' %}")
    path("login/", views.login_view, name="login"),
    path("signup/", views.signup_view, name="signup"),
    path("logout/", views.logout_view, name="logout"),
    path("profile_completion/", views.post_login_view, name="profile_completion"),
    path("add_skils/", views.add_skills_view, name="add_skills"),
    path("api/skills/", views.get_skills_api, name="skills_api"),
    path("api/proficiency_levels/", views.get_proficiency_levels_api, name="proficiency_levels_api"),   
    path("home/", views.homepage_view, name="home"),
    path("profile/", views.user_profile_view, name="user_profile"),
    path("browse_skills/", views.browse_skills_view, name="browse_skills"),
    path("skills/<int:skill_id>/<str:skill_type>/", views.skill_users_list_view, name="skill_users_list"),
    path("users/<int:user_id>/profile/", views.public_user_profile_view, name="public_user_profile"),
    path("chat/start/<int:target_user_id>/", views.start_chat_with_user, name="start_chat_with_user"),
]

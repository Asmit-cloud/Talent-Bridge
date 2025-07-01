from django.urls import path
from . import views

app_name = "SkillSwap_Chat"

urlpatterns = [
    path("<int:chat_room_id>/", views.chat_room_view, name="chat_room_view"),
]

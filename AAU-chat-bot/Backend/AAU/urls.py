from django.urls import path
from . import views

urlpatterns = [
    path("stream_answer", views.stream_answer),
    path("clear_chat", views.clear_chat)
]
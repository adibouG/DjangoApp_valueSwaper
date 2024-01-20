from django.urls import path
from . import views


urlpatterns = [
    path("", views.index, name="swaper"),
    path("details/", views.details, name="details"),
    path("details/update/", views.update, name="update"),
]
from django.urls import path

from . import views

app_name = "pure"

urlpatterns = [
    path("user/xml/", views.UserView.as_view(), name="user-xml"),
    path("person/xml/", views.PersonView.as_view(), name="person-xml"),
]

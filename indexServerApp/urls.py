from django.urls import re_path
from .views import index
# Catch all pattern
urlpatterns = [
    re_path('.*/', index, name='index'),
]
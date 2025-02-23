from django.urls import path
from . views import api_home
from .views import ProductoListView
from . views import ChatBotView

urlpatterns = [
    path('productos/', ProductoListView.as_view(), name='productos'),
    path('', api_home, name='api_home'),
    path('chatbot/', ChatBotView.as_view(), name='chatbot'),
]

from django.urls import path
from .views import telegram_code_view

urlpatterns = [
    path('account/<int:account_id>/authorize/', telegram_code_view, name='account_authorize'),
]
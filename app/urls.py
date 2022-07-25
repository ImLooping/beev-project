from django.urls import path, include
from . import views
from app.views import AllList, Client
from django.conf.urls import url

urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard/', views.index, name='index'),
    path('dashboard/<str:pk>/', views.index, name='index'),
    path('run_script/', views.run_script, name='run_script'),
    path('all/', AllList.as_view(), name='resume'),
    path('all/<int:page>/', AllList.as_view(), name='resume'),
    path('all/<str:start>/<str:end>/', AllList.as_view(), name='resume'),
    path('client/<str:pk>/', Client.as_view(), name='client'),
]

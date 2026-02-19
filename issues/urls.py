from django.urls import path
from . import views

urlpatterns = [
    path('', views.issue_list, name='issue_list'),
    path('issue/<int:pk>/', views.issue_compact, name='issue_detail'),
    path('issue/<int:pk>/full/', views.issue_detail_full, name='issue_detail_full'),

    path('issue/<int:pk>/add-event/', views.add_event, name='add_event'),
    path('add/', views.add_issue, name='add_issue'),
    path('issue/<int:pk>/print/', views.print_issue, name='print_issue'),
    path('search/', views.global_search, name='global_search'),


]

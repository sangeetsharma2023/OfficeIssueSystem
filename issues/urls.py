from django.urls import path
from . import views

urlpatterns = [
    path('', views.issue_list, name='issue_list'),
    path('issue/<int:pk>/', views.issue_compact, name='issue_detail'),
    path('issue/<int:pk>/full/', views.issue_detail_full, name='issue_detail_full'),
    path('issue/<int:pk>/edit/', views.edit_issue, name='edit_issue'),
    path('issue/<int:pk>/delete/', views.delete_issue, name='delete_issue'),

    path('issue/<int:pk>/add-event/', views.add_event, name='add_event'),
    path('add/', views.add_issue, name='add_issue'),
    path('issue/<int:pk>/print/', views.print_issue, name='print_issue'),
    path('search/', views.global_search, name='global_search'),

    path('files/', views.file_list, name='file_list'),
    path('files/add/', views.add_file, name='add_file'),
    path('files/<int:pk>/edit/', views.edit_file, name='edit_file'),
    path('files/<int:pk>/delete/', views.delete_file, name='delete_file'),

    path('event/<int:pk>/edit/', views.edit_event, name='edit_event'),
    path('event/<int:pk>/delete/', views.delete_event, name='delete_event'),

]

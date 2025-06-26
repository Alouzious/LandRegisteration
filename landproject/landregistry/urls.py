from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register_land/', views.register_land, name='register_land'),
    path('transfer_land/', views.transfer_land, name='transfer_land'),
    path('lease_land/', views.lease_land, name='lease_land'),
    path('view_details/', views.view_details, name='view_details'),
    path('split_land/', views.split_land, name='split_land'),  # frontend page
    path('search/', views.search_page, name='search_page'),

    # API endpoints
    path('api/land/<str:plot_id>/', views.get_land, name='get_land'),
    path('api/search-owner/<str:owner_name>/', views.search_by_owner_name, name='search_owner'),
    path('api/split_land/', views.split_and_transfer_view, name='split_and_transfer_land'),
]

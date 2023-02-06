
from django.urls import path
from ride import views


urlpatterns = [
    path('', views.index, name='index'),
    path('home/', views.user_home_view, name='home'),
    path("register/", views.register_request, name="register"),
    path("rides/", views.RideListView, name='rides'),
    path("ride/<uuid:pk>/detail", views.ride_detail_view, name='ride-detail'),
    path("ride/<uuid:pk>/update", views.RideUpdate.as_view(), name='ride-update'),
    path("ride/<uuid:pk>/delete", views.RideDelete.as_view(), name='ride-delete'),
    path("ride/request/", views.RequestRide.as_view(), name='request-ride'),
    path("driver/menu/", views.drive_menu_view, name='driver'),
    path("driver/create/", views.DriverCreate.as_view(), name='driver-create'),
    path("driver/<int:pk>/detail/",
         views.DriverDetailView, name='driver-detail'),
    path("driver/<int:pk>/update/",
         views.DriverUpdate.as_view(), name='driver-update'),
    path("driver/<int:pk>/search",
         views.DriverSearchView, name='driver-search'),
    path("driver/<uuid:id>/confirm/",
         views.DriverConfirmView, name='driver-confirm'),
    path("driver/<uuid:id>/complete/",
         views.DriverCompleteView, name='driver-complete'),
    path("driver/<int:pk>/list", views.DriveListView, name='driver-list'),
    path("sharer/search/", views.SharerfindView, name='sharer-search'),
    path("sharer/<int:num>/join/", views.SharerJoinView, name='sharer-join'),
    path("sharer/<uuid:id>/delete/",
         views.SharerDeleteView, name='sharer-delete'),
]

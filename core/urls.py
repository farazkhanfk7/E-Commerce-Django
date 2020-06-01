from django.contrib import admin
from django.urls import path, include
from .views import ItemDetailView, checkout, HomeView, add_to_cart, add_single_item, remove_from_cart, OrderSummaryView, remove_single_item

app_name = 'core'

urlpatterns = [
    path('', HomeView.as_view(), name="home"),
    path('checkout', checkout, name="checkout"),
    path('order-summary', OrderSummaryView.as_view(), name="order-summary"),
    path('product/<slug>/', ItemDetailView.as_view(), name="product"),
    path('add-to-cart/<slug>', add_to_cart, name="add_to_cart"),
    path('remove-from-cart/<slug>', remove_from_cart, name="remove_from_cart"),
    path('remove-single-item/<slug>', remove_single_item,
         name="remove-single-item"),
    path('add-single-item/<slug>', add_single_item, name="add-single-item")
]

from django.urls import path
from . import views

urlpatterns = [
    path('add/', views.add_to_cart),
    path('', views.view_cart),
    path('update/<int:id>/', views.update_cart_item),
    path('delete/<int:id>/', views.delete_cart_item),
    path('checkout/', views.checkout),
    path('pay/<int:order_id>/', views.initiate_payment),
    path('verify/<str:reference>/', views.verify_payment),
]
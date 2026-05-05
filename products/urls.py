from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_product),
    path('', views.get_products),
    path('<int:id>/', views.get_product),
    path('update/<int:id>/', views.update_product),
    path('delete/<int:id>/', views.delete_product),
    path('<int:product_id>/review/', views.add_review),
    path('<int:product_id>/review/', views.get_reviews)
]
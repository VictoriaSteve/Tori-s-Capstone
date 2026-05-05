from rest_framework import serializers
from .models import Product, Review


# REVIEW 
class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = Review
        fields = ["id", "user", "rating", "comment", "created_at"]


# PRODUCT 
class ProductSerializer(serializers.ModelSerializer):
    reviews = ReviewSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "image",
            "name",
            "price",
            "description",
            "category",
            "stock",
            "created_at",
            "reviews"
        ]
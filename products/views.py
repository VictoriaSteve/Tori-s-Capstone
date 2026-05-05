from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import Product, Review
from .serializers import ProductSerializer, ReviewSerializer

# Swagger / OpenAPI
from rest_framework import serializers as drf_serializers
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
    inline_serializer,
    OpenApiResponse,
)

# RESPONSE SCHEMAS FOR DOCS

_product_response = inline_serializer(
    name="ProductResponse",
    fields={
        "message": drf_serializers.CharField(),
        "data": ProductSerializer()
    }
)

_product_list_response = inline_serializer(
    name="ProductListResponse",
    fields={
        "message": drf_serializers.CharField(),
        "data": ProductSerializer(many=True)
    }
)

_review_response = inline_serializer(
    name="ReviewResponse",
    fields={
        "message": drf_serializers.CharField(),
        "data": ReviewSerializer()
    }
)

_error_response = inline_serializer(
    name="ErrorResponse",
    fields={
        "error": drf_serializers.CharField()
    }
)


# CREATE PRODUCT
@extend_schema(
    summary="Create Product",
    description="Create a new ToriesGlow product.",
    request=ProductSerializer,
    responses={
        201: _product_response,
        400: _error_response
    },
    tags=["Products"]
)
@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def create_product(request):
    serializer = ProductSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(created_by=request.user)
        return Response(
            {"message": "Product added to ToriesGlow", "data": serializer.data},
            status=201
        )
    return Response(serializer.errors, status=400)


# GET ALL PRODUCTS
@extend_schema(
    summary="Get All Products",
    description="Retrieve all products or filter by category.",
    parameters=[
        OpenApiParameter(
            name="category",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Filter products by category"
        )
    ],
    responses={200: ProductSerializer(many=True)},
    tags=["Products"]
)
@api_view(["GET"])
def get_products(request):
    category = request.query_params.get('category')

    if category:
        products = Product.objects.filter(category=category)
    else:
        products = Product.objects.all()

    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)


# GET ONE PRODUCT
@extend_schema(
    summary="Get One Product",
    description="Retrieve one product with reviews.",
    responses={
        200: ProductSerializer,
        404: _error_response
    },
    tags=["Products"]
)
@api_view(["GET"])
def get_product(request, id):
    try:
        product = Product.objects.get(id=id)
    except Product.DoesNotExist:
        return Response({"error": "Product not found"}, status=404)

    serializer = ProductSerializer(product)
    return Response(serializer.data)


# UPDATE PRODUCT
@extend_schema(
    summary="Update Product",
    description="Update product details or upload image.",
    request=ProductSerializer,
    responses={
        200: _product_response,
        400: _error_response,
        404: _error_response
    },
    tags=["Products"]
)
@api_view(["PUT", "PATCH"])
@permission_classes([permissions.IsAuthenticated])
def update_product(request, id):
    try:
        product = Product.objects.get(id=id)
    except Product.DoesNotExist:
        return Response({"error": "Product not found"}, status=404)

    serializer = ProductSerializer(product, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Product updated", "data": serializer.data})
    return Response(serializer.errors, status=400)


# DELETE PRODUCT
@extend_schema(
    summary="Delete Product",
    description="Delete a product from ToriesGlow.",
    responses={
        204: OpenApiResponse(description="Product deleted successfully"),
        404: _error_response
    },
    tags=["Products"]
)
@api_view(["DELETE"])
@permission_classes([permissions.IsAuthenticated])
def delete_product(request, id):
    try:
        product = Product.objects.get(id=id)
    except Product.DoesNotExist:
        return Response({"error": "Product not found"}, status=404)

    product.delete()
    return Response({"message": "Product deleted"}, status=204)


# ADD REVIEW
@extend_schema(
    summary="Add Review",
    description="Add a review to a product.",
    request=ReviewSerializer,
    responses={
        201: _review_response,
        400: _error_response,
        404: _error_response
    },
    tags=["Reviews"]
)
@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def add_review(request, product_id):
    product = Product.objects.filter(id=product_id).first()

    if not product:
        return Response({"error": "Product not found"}, status=404)

    serializer = ReviewSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save(user=request.user, product=product)
        return Response({
            "message": "Review added successfully",
            "data": serializer.data
        }, status=201)

    return Response(serializer.errors, status=400)


# GET REVIEWS
@extend_schema(
    summary="Get Product Reviews",
    description="Retrieve all reviews for a product.",
    responses={200: ReviewSerializer(many=True)},
    tags=["Reviews"]
)
@api_view(["GET"])
def get_reviews(request, product_id):
    reviews = Review.objects.filter(product_id=product_id)
    serializer = ReviewSerializer(reviews, many=True)
    return Response(serializer.data)
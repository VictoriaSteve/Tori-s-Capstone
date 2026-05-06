from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import permissions
from .models import Cart, CartItem, Order, OrderItem
from products.models import Product
from .serializers import CartItemSerializer
import requests
from django.conf import settings
from .utils import send_receipt_email

# Swagger / OpenAPI
from rest_framework import serializers as drf_serializers
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
    inline_serializer,
    OpenApiResponse,
)


# RESPONSE SCHEMAS
_message_response = inline_serializer(
    name="MessageResponse",
    fields={
        "message": drf_serializers.CharField()
    }
)

_error_response = inline_serializer(
    name="ErrorResponse",
    fields={
        "error": drf_serializers.CharField()
    }
)

_cart_response = inline_serializer(
    name="CartResponse",
    fields={
        "items": CartItemSerializer(many=True),
        "total_price": drf_serializers.DecimalField(max_digits=10, decimal_places=2)
    }
)

_checkout_response = inline_serializer(
    name="CheckoutResponse",
    fields={
        "message": drf_serializers.CharField(),
        "total_price": drf_serializers.DecimalField(max_digits=10, decimal_places=2),
        "order_id": drf_serializers.IntegerField()
    }
)

_payment_response = inline_serializer(
    name="PaymentResponse",
    fields={
        "message": drf_serializers.CharField(),
        "order_id": drf_serializers.IntegerField(),
        "total_paid": drf_serializers.DecimalField(max_digits=10, decimal_places=2)
    }
)

add_to_cart_request = inline_serializer(
    name="AddToCartRequest",
    fields={
        "product_id": drf_serializers.IntegerField(),
        "quantity": drf_serializers.IntegerField(default=1)
    }
)

update_cart_request = inline_serializer(
    name="UpdateCartRequest",
    fields={
        "quantity": drf_serializers.IntegerField()
    }
)


# ADD TO CART
@extend_schema(
    summary="Add to Cart",
    description="Add product to user's cart.",
    request=add_to_cart_request,
    tags=["Cart"],
    responses={200: _message_response, 404: _error_response}
)
@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def add_to_cart(request):
    user = request.user
    product_id = request.data.get("product_id")
    quantity = int(request.data.get("quantity", 1))

    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({"error": "Product not found"}, status=404)

    cart, created = Cart.objects.get_or_create(user=user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not created:
        cart_item.quantity += quantity
    else:
        cart_item.quantity = quantity

    cart_item.save()
    return Response({"message": "Added to cart"}, status=200)


# VIEW CART
@extend_schema(
    summary="View Cart",
    description="Retrieve all cart items and total price.",
    tags=["Cart"],
    responses={200: _cart_response}
)
@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def view_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    items = CartItem.objects.filter(cart=cart)
    serializer = CartItemSerializer(items, many=True)

    total_price = 0
    for item in items:
        total_price += item.product.price * item.quantity

    return Response({
        "items": serializer.data,
        "total_price": total_price
    })


# UPDATE CART ITEM
@extend_schema(
    summary="Update Cart Item",
    description="Update quantity of a cart item.",
    request=update_cart_request,
    tags=["Cart"],
    responses={200: _message_response, 404: _error_response}
)
@api_view(["PUT"])
@permission_classes([permissions.IsAuthenticated])
def update_cart_item(request, id):
    try:
        item = CartItem.objects.get(id=id, cart__user=request.user)
    except CartItem.DoesNotExist:
        return Response({"error": "Item not found"}, status=404)

    quantity = int(request.data.get("quantity", 1))
    item.quantity = quantity
    item.save()

    return Response({"message": "Cart updated"})


# DELETE CART ITEM
@extend_schema(
    summary="Delete Cart Item",
    description="Remove an item from cart.",
    tags=["Cart"],
    responses={
        200: _message_response,
        404: _error_response
    }
)
@api_view(["DELETE"])
@permission_classes([permissions.IsAuthenticated])
def delete_cart_item(request, id):
    try:
        item = CartItem.objects.get(id=id, cart__user=request.user)
        item.delete()
        return Response({"message": "Item removed"})
    except CartItem.DoesNotExist:
        return Response({"error": "Item not found"}, status=404)


# CHECKOUT
@extend_schema(
    summary="Checkout",
    description="Create order from cart.",
    tags=["Orders"],
    responses={200: _checkout_response, 400: _error_response}
)
@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def checkout(request):
    user = request.user
    cart, created = Cart.objects.get_or_create(user=user)
    items = CartItem.objects.filter(cart=cart)

    if not items:
        return Response({"error": "Cart is empty"}, status=400)

    total_price = 0
    for item in items:
        total_price += item.product.price * item.quantity

    order = Order.objects.create(user=user, total_price=total_price)

    for item in items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.product.price
        )

    items.delete()

    return Response({
        "message": "Checkout successful",
        "total_price": total_price,
        "order_id": order.id
    })


# INITIATE PAYMENT
@extend_schema(
    summary="Initiate Payment",
    description="Initialize Paystack payment.",
    tags=["Payments"]
)
@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def initiate_payment(request, order_id):
    order = Order.objects.filter(id=order_id, user=request.user).first()
    if not order:
        return Response({"error": "Order not found"}, status=404)

    url = "https://api.paystack.co/transaction/initialize"

    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "email": request.user.email,
        "amount": int(order.total_price * 100),
        "reference": str(order.id)
    }

    response = requests.post(url, json=data, headers=headers)
    res_data = response.json()

    return Response(res_data)


# VERIFY PAYMENT
@extend_schema(
    summary="Verify Payment",
    description="Verify payment and reduce stock automatically.",
    tags=["Payments"],
    responses={200: _payment_response, 404: _error_response}
)
@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def verify_payment(request, reference):
    order = Order.objects.filter(id=reference, user=request.user).first()

    if not order:
        return Response({"error": "Order not found"}, status=404)

    url = f"https://api.paystack.co/transaction/verify/{reference}"

    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"
    }

    response = requests.get(url, headers=headers)
    res_data = response.json()

    if res_data["data"]["status"] == "success":
        order.is_paid = True
        order.save()

        order_items = OrderItem.objects.filter(order=order)

        for item in order_items:
            product = item.product
            if product.stock >= item.quantity:
                product.stock -= item.quantity
                product.save()

        send_receipt_email(order)

        return Response({
            "message": "Payment successful",
            "order_id": order.id,
            "total_paid": order.total_price
        })

    return Response({"message": "Payment failed"})


# GET ORDER DETAILS
@extend_schema(
    summary="Get Order Details",
    description="View what a customer ordered.",
    tags=["Orders"]
)
@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def get_order_details(request, order_id):
    if request.user.is_staff:
        order = Order.objects.filter(id=order_id).first()
    else:
        order = Order.objects.filter(id=order_id, user=request.user).first()

    if not order:
        return Response({"error": "Order not found"}, status=404)

    items = OrderItem.objects.filter(order=order)

    data = []
    for item in items:
        data.append({
            "product": item.product.name,
            "quantity": item.quantity,
            "price": item.price
        })

    return Response({
        "order_id": order.id,
        "total_price": order.total_price,
        "items": data
    })    
# 💄 ToriesGlow API

A Django REST API for a beauty personal care.

# Features

* Products (CRUD + images)
* Reviews system
* Cart & checkout
* Paystack payments
* Auto stock update after payment
* Email receipts
* View order details (per user)
* Admin can view any order
* Swagger API docs

# Access Control

* Authentication required for protected endpoints
* Users can only access their own data (cart, orders)
* Admin users have extended privileges (e.g. view all orders)
 

# Tech Stack

* Django REST Framework
* Paystack
* drf-spectacular

# Endpoints

* `/products/`
* `/cart/`
* `/cart/checkout/`
* `/cart/pay/<order_id>/`
* `/cart/verify/<reference>/`
* `/cart/order/<order_id>/`

# Docs

* `/api/docs/`

# Tagline

Stay Glossy, Stay Gorgeous

from django.core.mail import send_mail

def send_receipt_email(order):
    subject = "ToriesGlow Order Receipt 💄✨"

    message = f"""
Hi {order.user.first_name},

Thank you for shopping with ToriesGlow Beauty ✨

Your order has been paid successfully.

Total Paid: ₦{order.total_price}

We are preparing your glow products for delivery ✨

Stay Glossy, Stay Gorgeous💄
"""

    send_mail(
        subject,
        message,
        "stevevicky16@mail.com",
        [order.user.email],
        fail_silently=False
    )
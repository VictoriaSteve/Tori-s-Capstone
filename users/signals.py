from .models import User
from django.db.models.signals import post_save
from django.dispatch import receiver #receiver helps listens to events and its a decorator
# from django.core.mail import send_mail
from utils.mail import send_smtp_mail




@receiver(post_save, sender=User)
def send_mail_with_template(sender, instance, created, **kwargs):
    print(instance)
    if created:

        send_smtp_mail(
            subject="🎉 Welcome to ToriesGlow Beauty",
            from_email="stevevicky16@mail.com",
            to=[instance.email],
            context={
                "header": f"{instance.first_name} {instance.last_name}",
                "description": "Welcome to ToriesGlow Beauty 💄✨We are so excited to have you with us. Get ready to experience luxury beauty, glowing skin, and confidence like never before.Your glow journey starts now ✨Stay Glossy, Stay Gorgeous! — ToriesGlow Beauty",
                "extra_info": "Let's get started.",
                "show_button": True,
                "button_text": "Get started",
                "button_link": "http://localhost:3000/onboarding"
            }
        )
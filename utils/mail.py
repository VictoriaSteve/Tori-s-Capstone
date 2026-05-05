from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives


def send_smtp_mail(subject, from_email, to, context, fall_back_default_text_content="Welcome to our app!"):
    """
    This function sends an email in both text and plain HTML content.

    Parameters:
    subject: The sender's email address
    to: List of recipient email addresses
    context: Dictionary of data to render in the HTML template
    """

    # Render HTML template with the given context
    html_content = render_to_string("messages.html", context)

    # Fallback plain text content for email clients that do not support HTML
    text_content = fall_back_default_text_content

    # Create an email object with subject, text content, sender and reciepients
    msg = EmailMultiAlternatives(subject, text_content, from_email, to)

    # Attach the HTML version of the messages
    msg.attach_alternative(html_content, "text/html")

    # Send the email
    msg.send()

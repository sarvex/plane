# Django imports
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

# Third party imports
from celery import shared_task
from sentry_sdk import capture_exception


@shared_task
def magic_link(email, key, token, current_site):
    try:
        realtivelink = f"/magic-sign-in/?password={token}&key={key}"
        abs_url = f"http://{current_site}{realtivelink}"

        from_email_string = "Team Plane <team@mailer.plane.so>"

        subject = "Login for Plane"

        context = {"magic_url": abs_url, "code": token}

        html_content = render_to_string("emails/auth/magic_signin.html", context)

        text_content = strip_tags(html_content)

        msg = EmailMultiAlternatives(subject, text_content, from_email_string, [email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        return
    except Exception as e:
        print(e)
        capture_exception(e)
        return

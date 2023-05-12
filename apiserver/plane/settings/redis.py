import os
import redis
from django.conf import settings
from urllib.parse import urlparse


def redis_instance():
    if settings.DOCKERIZED or os.environ.get(
        "DJANGO_SETTINGS_MODULE", "plane.settings.local"
    ):
        return redis.Redis.from_url(settings.REDIS_URL, db=0)
    url = urlparse(settings.REDIS_URL)
    return redis.Redis(
        host=url.hostname,
        port=url.port,
        password=url.password,
        ssl=True,
        ssl_cert_reqs=None,
    )

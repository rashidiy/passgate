from django.db import models


class Webhook(models.Model):
    name = models.CharField(max_length=255)
    url = models.URLField()

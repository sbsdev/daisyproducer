from django.db import models

class Document(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    publisher = models.CharField(max_length=255)
    content = models.FileField(upload_to='media')



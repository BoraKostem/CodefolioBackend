from django.db import models

class Chat(models.Model):
    uuid = models.CharField(max_length=255, unique=True)
    user_id = models.CharField(max_length=255)
    user_name = models.CharField(max_length=255, null=True)
    last_activity = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.uuid
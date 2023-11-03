from django.db import models
from django.conf import settings

class Chest(models.Model):
    user1 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user1_chests')
    user2 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user2_chests')
    confirmed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user1.first_name} & {self.user2.first_name}"


class Item(models.Model):
    chest = models.ForeignKey(Chest, on_delete=models.CASCADE, related_name='items')
    created = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    is_picture = models.BooleanField(default=False)


class Picture(models.Model):
    item = models.OneToOneField(Item, primary_key=True, on_delete=models.CASCADE)

    content = models.BinaryField(editable=True)
    content_type = models.CharField(max_length=256, help_text='The MIMEType of the file')

    def __str__(self):
        formatted_date = self.item.created.strftime('%b-%d-%y')
        return f"Picture {formatted_date} in Chest {self.item.chest.id}"


class Note(models.Model):
    item = models.OneToOneField(Item, primary_key=True, on_delete=models.CASCADE)

    text = models.TextField(editable=True)

    def __str__(self):
        formatted_date = self.item.created.strftime('%b-%d-%y')
        return f"Note {formatted_date} in Chest {self.item.chest.id}"


class Settings(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, primary_key=True, on_delete=models.CASCADE)
    light_dark_device = models.IntegerField(choices=[(1, "light"), (2, "dark"), (3, "device")], default=1)

    def __str__(self):
        return f"user {self.user.username} settings"

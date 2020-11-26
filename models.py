from django.db import models
from django.contrib.auth.models import User

class Folder(models.Model):
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    under = models.CharField(max_length=20)

class File(models.Model):
    name = models.CharField(max_length=255)
    name_in_dir = models.CharField(max_length=255)
    privacity = models.CharField(max_length=1)
    under = models.ForeignKey(Folder, on_delete=models.CASCADE)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    tags = models.CharField(max_length=1000, blank=True)

    def __str__(self):
        return self.file_name

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)

from django.db import models

class Resume(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    skills = models.TextField()
    file = models.FileField(upload_to='resumes/', null=True, blank=True)
    score = models.IntegerField(default=0)

    def __str__(self):
        return self.name
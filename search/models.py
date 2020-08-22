from django.db import models

# Create your models here.
class Sites(models.Model):
    url = models.TextField(unique=True)
    title = models.CharField(max_length=255)
    keywords = models.TextField()
    first_par = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sites'
from django.db import models

# Create your models here.
class Pais(models.Model):
    cdiatapais = models.CharField(max_length=4)
    cdsiscomexpais = models.CharField(max_length=4)
    nomepais = models.CharField(max_length=255)
    sigla = models.CharField(max_length=3)
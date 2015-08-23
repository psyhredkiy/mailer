# -*- coding: utf-8 -*-
from django.db import models
import os
from django.core.files.base import File
# Create your models here.
class Job(models.Model):
    name = models.CharField(max_length=30,verbose_name='Имя')
    recips = models.CharField(max_length=150,verbose_name='Кому')
    subj = models.CharField(max_length=140,verbose_name='Тема' )
    body = models.CharField(max_length=150,verbose_name='Тело')
    fromdir = models.CharField(max_length=50,verbose_name='Папка')


class Shed (models.Model):
    job = models.ForeignKey(Job)
    enabled=models.BooleanField()
    time = models.TimeField()


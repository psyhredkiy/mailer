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

    def getfc(self):
      job = Job.objects.get(id=self.id)
      o = os.popen('ls -1 %s | wc -l'%(job.fromdir))
      cnt = o.read()
      return cnt
    def ished(self):
      jb = Job.objects.get(id=self.id)
      shed = Shed.objects.get(job=jb).time
      return shed

class Shed (models.Model):
    job = models.ForeignKey(Job)
    enabled=models.BooleanField()
    time = models.TimeField()
    lastrun = models.CharField(max_length=10)



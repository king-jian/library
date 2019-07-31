import hashlib

from django.contrib.auth.hashers import make_password
from django.db import models


# Create your models here.
class Readers(models.Model):
    id = models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    name = models.CharField(max_length=12, null=False)
    student_card = models.IntegerField(unique=True)
    password = models.CharField(max_length=255)
    active = models.BooleanField(default=True)




class Book(models.Model):
    available = models.BooleanField(default=True)
    title = models.CharField(max_length=64)
    author = models.CharField(max_length=32)
    ISBN = models.CharField(max_length=32)
    publisher = models.CharField(max_length=32)
    pub_time = models.DateTimeField(auto_now_add=True)
    pages = models.IntegerField(null=True)
    describle = models.TextField(null=True)
    position = models.CharField(max_length=8)
    price = models.IntegerField()


class Record(models.Model):
    WAITFORCHECK = 'WAITFORCHECK'
    BORROWED = 'BORROWED'
    RETURNED = 'RETURNED'
    TURNDOWN = 'TURNDOWN'
    DEMAGE = 'DEMAGE'
    STATUS_CHOICES = (
        (WAITFORCHECK, 'WAITFORCHECK'),
        (BORROWED, 'BORROWED'),
        (RETURNED, 'RETURNED'),
        (TURNDOWN, 'TURNDOWN'),
        (DEMAGE, 'DEMAGE'),
    )
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    reader = models.ForeignKey(Readers)
    create_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)
    fine = models.IntegerField(default=20)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=WAITFORCHECK)


class FineStatistic(models.Model):
    begin_time = models.DateField(auto_now_add=True)
    end_time = models.DateField(auto_now_add=True)
    reader = models.ForeignKey("Readers", blank=True, null=True)
    total_fine = models.IntegerField(null=True)

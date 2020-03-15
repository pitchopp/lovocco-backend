import os
from django.contrib.auth.models import User
from django.db import models
from django.db.models import BooleanField, CharField, ForeignKey, DateField, TextField, IntegerField, OneToOneField, \
    ManyToManyField, ImageField


class Gender(models.Model):
    code = CharField(max_length=3)
    label = CharField(max_length=30)

    def __str__(self):
        return '%s (%s)' % (self.label, self.code)


class City(models.Model):
    name = CharField(max_length=50)

    def __str__(self):
        return self.name


def get_image_path(instance, filename):
    return os.path.join('photos', str(instance.id), filename)


class Lover(models.Model):
    configured = BooleanField(default=False)
    name = CharField(max_length=50, null=True)
    description = TextField(null=True)
    city = ForeignKey(City, on_delete=models.SET_NULL, related_name='+', null=True)
    gender = ForeignKey(Gender, on_delete=models.SET_NULL, related_name='+', null=True)
    birth_date = DateField(null=True)
    target_gender = ForeignKey(Gender, on_delete=models.SET_NULL, related_name='+', null=True)
    age_min = IntegerField(default=18, null=True)
    age_max = IntegerField(default=60, null=True)
    user = OneToOneField(User, on_delete=models.CASCADE)
    likes = ManyToManyField('self', related_name='likers')

    def __str__(self):
        return str(self.user)


class Photo(models.Model):
    file_path = ImageField(upload_to=get_image_path, blank=True, null=True)
    lover = ForeignKey(Lover, on_delete=models.CASCADE, related_name='photos')

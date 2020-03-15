from django.contrib.auth.models import User
from rest_framework import serializers
from backend.models import Lover, City, Gender, Photo


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = 'name',


class GenderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gender
        fields = 'code', 'label'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = 'id', 'username', 'email'


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = 'file_path'


class LoverSerializer(serializers.ModelSerializer):
    city = CitySerializer()
    gender = GenderSerializer()
    target_gender = GenderSerializer()
    user = UserSerializer()
    photos = PhotoSerializer(many=True)

    class Meta:
        model = Lover
        fields = '__all__'

from django.contrib.auth.models import User
from rest_framework import serializers
from backend.models import Lover, City, Gender, Photo


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = 'id', 'name'


class GenderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gender
        fields = 'id', 'code', 'label'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = 'id', 'username', 'email'


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = 'image',


class LoverSerializer(serializers.ModelSerializer):
    city = CitySerializer()
    gender = GenderSerializer()
    target_gender = GenderSerializer()
    # user = UserSerializer()
    photos = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()

    class Meta:
        model = Lover
        fields = 'id', 'name', 'description', 'birth_date', 'gender', 'city', 'target_gender', 'age_min', 'age_max', 'photos', 'age'

    def get_age(self, obj: Lover):
        return obj.get_age()

    def get_photo(self, obj: Lover):
        return [x.get('image') for x in PhotoSerializer(obj.photos, many=True).data]


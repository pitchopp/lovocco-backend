from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import User
from django.http import JsonResponse
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes, parser_classes
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

from backend.models import Lover, Gender, City
from backend.serializers import LoverSerializer, CitySerializer, GenderSerializer, PhotoSerializer


def get_body(request) -> dict:
    return request.data


def get_authenticated_user(request) -> User:
    headers = request.headers
    auth = headers.get('Authorization')
    if auth is not None:
        if auth.startswith('Token '):
            token = auth[6:]
            return Token.objects.get(key=token).user
        else:
            raise ValueError('Unknown authentication method')
    else:
        raise ValueError('no authentication found')


def get_or_create_lover(user: User) -> Lover:
    try:
        lover = user.lover
    except Lover.DoesNotExist:
        data = user.last_name.split(';')
        gender = Gender.objects.get(pk=int(data[0]))
        city = data[2]
        birth_date = datetime.strptime(data[1], '%Y-%m-%d').date()
        lover = Lover(
            user=user,
            name=user.first_name,
            gender=gender,
            city_id=int(city),
            birth_date=birth_date,
        )
        lover.target_gender = Gender.objects.exclude(id=gender.id).first()
        age = lover.get_age()
        lover.age_min = max(age - 3, 18)
        lover.age_max = age + 3
        lover.save()
    return lover


@api_view(['GET', 'PUT'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
def my_profile(request):
    user = get_authenticated_user(request)
    lover = get_or_create_lover(user)
    if request.method == 'GET':
        return JsonResponse(LoverSerializer(lover).data, safe=False)
    elif request.method == 'PUT':
        body = get_body(request)
        name = body.get('name')
        if name in [None, '']:
            return JsonResponse(
                {"name": "Veuillez saisir votre prénom"},
                status=status.HTTP_400_BAD_REQUEST
            )
        gender = body.get('gender')
        if gender in [None, '']:
            return JsonResponse(
                {"gender": "Veuillez indiquer votre sexe"},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            gender = Gender.objects.get(pk=gender)
        except Gender.DoesNotExist:
            return JsonResponse(
                {"gender": "Le sexe choisi est ambigu"},
                status=status.HTTP_400_BAD_REQUEST
            )
        birth_date = body.get("birth_date")
        if birth_date in [None, '']:
            return JsonResponse(
                {"birth_date": "Veuillez saisir une date de naissance"},
                status=status.HTTP_400_BAD_REQUEST
            )
        birth_date = datetime.strptime(birth_date, '%Y-%m-%d').date()
        city = body.get('city')
        if city in [None, '']:
            return JsonResponse(
                {"city": "Veuillez saisir une ville"},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            city = City.objects.get(pk=city)
        except City.DoesNotExist:
            return JsonResponse(
                {"city": "Ville invalide"},
                status=status.HTTP_400_BAD_REQUEST
            )
        target_gender = body.get('target_gender')
        if target_gender in [None, '']:
            return JsonResponse(
                {"gender": "Veuillez indiquer votre orientation sexuelle"},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            target_gender = Gender.objects.get(pk=target_gender)
        except Gender.DoesNotExist:
            return JsonResponse(
                {"target_gender": "Le sexe choisi est ambigu"},
                status=status.HTTP_400_BAD_REQUEST
            )
        description = body.get('description')
        age_min = body.get('age_min')
        age_max = body.get('age_max')

        # update lover
        lover.name = name
        lover.birth_date = birth_date
        lover.gender = gender
        lover.city = city
        lover.description = description
        lover.age_min = age_min
        lover.age_max = age_max
        lover.target_gender = target_gender

        lover.save()
        return JsonResponse(LoverSerializer(lover).data, safe=False)


@api_view(['POST'])
def register_user(request):
    body = get_body(request)
    username = body.get('username')
    if username in [None, '']:
        return JsonResponse(
            {"username": "Veuillez choisir un identifiant"},
            status=status.HTTP_400_BAD_REQUEST
        )
    username = username.lower().replace(' ', '')
    if User.objects.filter(username=username).exists():
        return JsonResponse(
            {"username": "Ce pseudo n'est pas disponible"},
            status=status.HTTP_400_BAD_REQUEST
        )
    name = body.get('name')
    if name in [None, '']:
        return JsonResponse(
            {"name": "Veuillez saisir votre prénom"},
            status=status.HTTP_400_BAD_REQUEST
        )
    gender = body.get('gender')
    if gender in [None, '']:
        return JsonResponse(
            {"gender": "Veuillez indiquer votre sexe"},
            status=status.HTTP_400_BAD_REQUEST
        )
    elif not Gender.objects.filter(id=gender).exists():
        return JsonResponse(
            {"gender": "Le sexe choisi est ambigu"},
            status=status.HTTP_400_BAD_REQUEST
        )
    email = body.get('email')
    if email in [None, '']:
        return JsonResponse(
            {"email": "Veuillez saisir une adresse email"},
            status=status.HTTP_400_BAD_REQUEST
        )
    elif User.objects.filter(email=email).exists():
        return JsonResponse(
            {"email": "Cet adresse email est déjà utilisée"},
            status=status.HTTP_400_BAD_REQUEST
        )
    password = body.get('password')
    if password in [None, '']:
        return JsonResponse(
            {"password": "Veuillez saisir un mot de passe"},
            status=status.HTTP_400_BAD_REQUEST
        )
    birthdate = body.get("birthdate")
    if birthdate in [None, '']:
        return JsonResponse(
            {"birthdate": "Veuillez saisir une date de naissance"},
            status=status.HTTP_400_BAD_REQUEST
        )
    city = body.get('city')
    if city in [None, '']:
        return JsonResponse(
            {"city": "Veuillez saisir une ville"},
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        City.objects.get(pk=city)
    except City.DoesNotExist:
        return JsonResponse(
            {"city": "Ville invalide"},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = User(
        username=username,
        email=email,
        first_name=name,
        last_name='%s;%s;%s' % (str(gender), birthdate, str(city)),
        is_active=True,
        is_staff=False,
        is_superuser=False
    )
    user.save()
    user.set_password(password)
    user.save()
    get_or_create_lover(user)
    token, created = Token.objects.get_or_create(user=user)
    return JsonResponse({'token': token.key}, safe=False)


@api_view(['POST'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
def like(request, lover_id):
    user = get_authenticated_user(request)
    lover = get_or_create_lover(user)
    lover.likes.add(lover_id)
    match = lover.likers.all().filter(id=lover_id).exists()
    return JsonResponse({"match": match})


@api_view(['POST'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
def dislike(request, lover_id):
    user = get_authenticated_user(request)
    lover = get_or_create_lover(user)
    lover.dislikes.add(lover_id)
    return JsonResponse({"status": "ok"})


@api_view(['GET'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
def candidates(request):
    user = get_authenticated_user(request)
    lover = get_or_create_lover(user)
    today = datetime.today()
    birthday_min = today - relativedelta(years=lover.age_max)
    birthday_max = today - relativedelta(years=lover.age_min)
    age = lover.get_age()
    possible_candidates = Lover.objects.filter(
        gender=lover.target_gender,
        target_gender=lover.gender,
        city=lover.city,
        user__is_active=True,
        birth_date__gte=birthday_min,
        birth_date__lte=birthday_max,
        age_min__lte=age,
        age_max__gte=age,
    ).exclude(id=lover.id).exclude(id__in=[o.id for o in lover.likes.all()])
    return JsonResponse(LoverSerializer(possible_candidates, many=True).data, safe=False)


@api_view(['GET'])
@authentication_classes((TokenAuthentication,))
# @permission_classes((IsAuthenticated,))
def cities(request):
    return JsonResponse(CitySerializer(City.objects.all(), many=True).data, safe=False)


@api_view(['GET'])
@authentication_classes((TokenAuthentication,))
# @permission_classes((IsAuthenticated,))
def genders(request):
    return JsonResponse(GenderSerializer(Gender.objects.all(), many=True).data, safe=False)


@api_view(['GET', 'POST'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
@parser_classes([MultiPartParser, FormParser])
def photos(request):
    user = get_authenticated_user(request)
    lover = get_or_create_lover(user)
    if request.method == 'GET':
        photos = lover.photos.all()
        return Response(PhotoSerializer(photos, many=True).data)
    elif request.method == 'POST':
        lover.photos.all().delete()
        data = request.data
        photo_serializer = PhotoSerializer(data=data)
        if photo_serializer.is_valid():
            photo_serializer.save(lover=lover)
            return Response(photo_serializer.data)
        else:
            return Response(photo_serializer.errors, status=status.HTTP_418_IM_A_TEAPOT)

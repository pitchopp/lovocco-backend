import json
from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import User
from django.http import JsonResponse
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from backend.models import Lover, Gender, City
from backend.serializers import LoverSerializer, UserSerializer, CitySerializer, GenderSerializer


def get_body(request) -> dict:
    body_unicode = request.body.decode('utf-8')
    if body_unicode:
        body = json.loads(body_unicode)
    else:
        body = {}
    return body


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
        gender = Gender.objects.get(code=data[0])
        city = data[2]
        birthdate = datetime.strptime(data[1], '%Y-%m-%d')
        lover = Lover(
            user=user,
            name=user.first_name,
            gender=gender,
            city_id=int(city),
            birth_date=birthdate,
        )
        lover.target_gender = Gender.objects.exclude(code=data[0]).first()
        age = lover.get_age()
        lover.age_min = max(age - 3, 18)
        lover.age_max = age + 3
        lover.save()
    return lover


@api_view(['GET'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
def my_profile(request):
    user = get_authenticated_user(request)
    lover = get_or_create_lover(user)
    return JsonResponse(LoverSerializer(lover).data, safe=False)


@api_view(['POST'])
def register_user(request):
    body = get_body(request)
    username = body.get('username')
    if User.objects.filter(username=username).exists():
        return JsonResponse(
            {"username": "Ce pseudo n'est pas disponible"},
            status=status.HTTP_400_BAD_REQUEST
        )
    name = body.get('name')
    if name is None:
        return JsonResponse(
            {"name": "Veuillez saisir votre prénom"},
            status=status.HTTP_400_BAD_REQUEST
        )
    gender = body.get('gender')
    if gender is None:
        return JsonResponse(
            {"gender": "Veuillez saisir un sexe"},
            statuts=status.HTTP_400_BAD_REQUEST
        )
    elif gender not in Gender.objects.all().values_list('code', flat=True):
        return JsonResponse(
            {"gender": "Le sexe choisi est ambigu"},
            status=status.HTTP_400_BAD_REQUEST
        )
    email = body.get('email')
    if email is None:
        return JsonResponse(
            {"email": "Veuillez saisir une adresse email"},
            statuts=status.HTTP_400_BAD_REQUEST
        )
    elif User.objects.filter(email=email).exists():
        return JsonResponse(
            {"email": "Cet adresse email est déjà utilisée"},
            status=status.HTTP_400_BAD_REQUEST
        )
    password = body.get('password')
    if password is None:
        return JsonResponse(
            {"password": "Veuillez saisir un mot de passe"},
            statuts=status.HTTP_400_BAD_REQUEST
        )
    birthdate = body.get("birthdate")
    if birthdate is None:
        return JsonResponse(
            {"birthdate": "Veuillez saisir une date de naissance"},
            statuts=status.HTTP_400_BAD_REQUEST
        )
    city = body.get('city')
    if city is None:
        return JsonResponse(
            {"city": "Veuillez saisir une ville"},
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        City.objects.get(pk=city)
    except City.DoesNotExist:
        return JsonResponse(
            {"city": "Ville invalide"},
            statuts=status.HTTP_400_BAD_REQUEST
        )

    user = User(
        username=username,
        email=email,
        first_name=name,
        last_name='%s;%s;%s' % (gender, birthdate, str(city)),
        is_active=True,
        is_staff=False,
        is_superuser=False
    )
    user.save()
    user.set_password(password)
    user.save()
    get_or_create_lover(user)
    return JsonResponse(UserSerializer(user).data, safe=False)


@api_view(['POST'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
def like(request, lover_id):
    user = get_authenticated_user(request)
    lover = get_or_create_lover(user)
    lover.likes.add(lover_id)
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
@permission_classes((IsAuthenticated,))
def cities(request):
    return JsonResponse(CitySerializer(City.objects.all(), many=True).data, safe=False)


@api_view(['GET'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
def genders(request):
    return JsonResponse(GenderSerializer(Gender.objects.all(), many=True).data, safe=False)

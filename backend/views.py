import json

from django.contrib.auth.models import User
from django.http import JsonResponse
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from backend.models import Lover
from backend.serializers import LoverSerializer, UserSerializer


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
        lover = Lover(user=user)
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
    user = User(
        username=body.get('username'),
        email=body.get('email'),
        is_staff=False,
        is_superuser=False
    )
    user.save()
    user.set_password(body.get('password'))
    user.save()
    return JsonResponse(UserSerializer(user).data, safe=False)


@api_view(['POST'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
def like(request, lover_id):
    user = get_authenticated_user(request)
    lover = get_or_create_lover(user)
    lover.likes.add(lover_id=lover_id)
    return JsonResponse({"status": "ok"})

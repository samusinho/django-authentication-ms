from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserSerializer
from rest_framework.authtoken.views import ObtainAuthToken
import jwt
import datetime
from authentication.settings import SECRET_KEY

class UserAPI(APIView):
    def post(self, request):
        serializer = UserSerializer(data = request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Login(ObtainAuthToken):
    def post(self, request):
        login_serializer = self.serializer_class(data=request.data, context= { 'request': request })
        if login_serializer.is_valid():
            user = login_serializer.validated_data['user']
            if user.is_active:
                date = datetime.datetime.now()
                token = jwt.encode(payload={
                    'exp': date + datetime.timedelta(hours=2),
                    'user': user.id
                }, key=SECRET_KEY)
                return Response({ 
                    'message': 'Sesión iniciada',
                    'token': token,
                    'user': user.id
                    }, status=status.HTTP_200_OK)
            else:
                return Response({ 'error': 'Este usuario no puede iniciar sesión'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({ 'error': 'Nombre de usuario y/o contraseña incorrectos' }, status=status.HTTP_400_BAD_REQUEST)

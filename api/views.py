from django.http.response import JsonResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserSerializer
from rest_framework.authtoken.views import ObtainAuthToken
import jwt
import datetime
from authentication.settings import SECRET_KEY
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

class UserAPI(APIView):
    def post(self, request):
        serializer = UserSerializer(data = request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    ####################################
    def get(self, request, *args, **kwargs):
        print(kwargs.get('id'))
        if kwargs.get('id') is None:
            users = User.objects.all()
            users_serializer = UserSerializer(users, many=True)
            return Response(users_serializer.data, status=status.HTTP_200_OK)
        else:
            user = User.objects.get(id=kwargs.get('id'))
            user_serializer = UserSerializer(user)
            return Response(user_serializer.data, status=status.HTTP_200_OK)
    
    def delete(self, request, *args, **kwargs):
        user = User.objects.get(id=kwargs.get('id'))
        user.delete()
        return Response({ 'message': 'El usuario ha sido eliminado' })
    

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

class AuthView(APIView): #middleware
    user: User
    def dispatch(self, request, *args, **kwargs):
        try:
            if not request.headers.get('Authorization'):
                raise Exception('Debes proporcionar un token')
            token = request.headers.get('Authorization').split(' ')[1]
            decoded = jwt.decode(token, key=SECRET_KEY, algorithms=['HS256'])
            print(decoded)
            self.user = User.objects.get(id=decoded.get('user_id'))
            if self.user.is_active:
                return super(AuthView, self).dispatch(request, *args, **kwargs) #next()
            #Comprobación de rol -> is_admin (true, false)

            else:
                raise Exception('El usuario no está activo')
        except Exception as e:
            return JsonResponse({'error': e.__str__()}, status=status.HTTP_401_UNAUTHORIZED)

class VerifyTokenManually(AuthView):
    def get(self, request):
        return Response({ 'message': 'Puedes ver esto porque estás autenticado' }, status=status.HTTP_200_OK)

class VerifyToken(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = (JWTAuthentication,)
    def get(self, request):
        data = UserSerializer(request.user).data
        del data['password']
        return Response(data, status=status.HTTP_200_OK)

from rest_framework.views import APIView
from .Serializers import LoginSerializer, UserSerializer 
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from .models import User    
import jwt, datetime

# Create your views here.
class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
class LoginView(APIView):
    def post(self, request):
        email = request.data['email']
        password = request.data['password']
        
        user = User.objects.filter(email=email).first()
        if user is None:
            raise AuthenticationFailed('User not found!!!')
        
        if not user.check_password(password):
            raise AuthenticationFailed('Incorrect password!!!')
        
        pyload = {
            'id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            'iat': datetime.datetime.utcnow()
        }
        
        token = jwt.encode(pyload, 'secret', algorithm='HS256')
        
        response = Response()
        response.set_cookie(key='jwt', value=token, httponly=True)
        response.data = {
            'jwt': token
        }
        return response
        
    
class UserView(APIView):
    def get(self, request):
        token = request.COOKIES.get('jwt')
        if not token:
            raise AuthenticationFailed('Unauthenticated!!!')
        
        try:
            pyload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!!!')
        
        User = User.objects.filter(id=pyload['id']).first()
        serializer = UserSerializer(User)
        return Response(serializer.data)
    
class LogoutView(APIView):
    def get(self, request):
        response = Response({'message': 'Successfully logged out!!!'})
        response.delete_cookie('jwt')
        return response
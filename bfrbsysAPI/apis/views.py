from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from .models import Item, TrainedModel

from .serializers import (ItemSerializer, TrainedModelSerializer, UserSerializer,
    RegisterSerializer, LoginSerializer)

from rest_framework.permissions import IsAuthenticated
from rest_framework import status, generics
from rest_framework.authentication import TokenAuthentication, SessionAuthentication, BasicAuthentication
from rest_framework.authtoken.models import Token
from .utils import hex_to_c_array, rmv_file_spaces
from django.conf import settings
from django.core.files.base import File
import os

from knox.models import AuthToken
from knox.views import LoginView as KnoxLoginView

from rest_framework.permissions import AllowAny
from rest_framework.authtoken.serializers import AuthTokenSerializer
from django.contrib.auth import login



def home(request):
    return render(request, 'apis/home.html', {})

class NeuralNetworkBuilder(APIView):
    """
    TEST TEST TEST TEST TEST TEST TEST TEST 
    """
    
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)



    def get(self, request, format=None):
        items = Item.objects.all()
        serializer = ItemSerializer(items, many=True)
        # token, _ = Token.objects.get(user=request.user)
        

        return Response(serializer.data)

    def post(self, request, format=None):
        data = request.data.get('data')
        named_model = request.data.get('model_name')

        if named_model == '':
            named_model = 'NO_NAME'
        # Save as temporary
        USER_TEMP_FILE = os.path.join(settings.MEDIA_ROOT, request.user.username + '_TEMPFILE.h')
        with open(USER_TEMP_FILE, 'w') as temp:
            # temp.write(hex_to_c_array(tflite_model))
            temp.write('hello')

        # Then save to database
        f = open(USER_TEMP_FILE, 'rb')
        data = {
            'model_name': named_model,
            'file': File(f, name=str(named_model).replace(" ", "_") + f'--{request.user.username}' + '.h')
        }
            
        model_string = rmv_file_spaces(USER_TEMP_FILE)
        print(model_string)

        serializer = TrainedModelSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            f.close()
            os.remove(USER_TEMP_FILE) # end of using temp model
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class UserCreation(APIView):
#     """
#     API View to create or get a list of all the registered
#     users. GET request returns the registered users whereas
#     a POST request allows to create a new user.
#     """
#     permission_classes = [AllowAny]
    

#     # Delete later
#     def get(self, format=None):
#         users = User.objects.all()
#         serializer = UserSerializer(users, many=True)
#         return Response(serializer.data)

#     def post(self, request):
#         serializer = UserSerializer(data=request.data)
#         if serializer.is_valid(raise_exception=ValueError):
#             serializer.create(validated_data=request.data)
#             return Response(
#                 serializer.data,
#                 status=status.HTTP_201_CREATED
#             )
#         return Response(
#             {
#                 "error": True,
#                 "error_msg": serializer.error_messages,
#             },
#             status=status.HTTP_400_BAD_REQUEST
#         )

class RegisterAPI(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        _, token = AuthToken.objects.create(user)
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": token
        })



class LoginAPI(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = ()

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        _, token = AuthToken.objects.create(user)
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": token
        })


class UserAPI(generics.RetrieveAPIView):
  permission_classes = [IsAuthenticated]
  serializer_class = UserSerializer

  def get_object(self):
    return self.request.user
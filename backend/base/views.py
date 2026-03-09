from django.shortcuts import render
from django.http import JsonResponse, Http404

from rest_framework.decorators import api_view
from rest_framework.response import Response

from django.contrib.auth.models import User
from django.forms.models import model_to_dict
from .models import *
try:
    from . import products as products_module
    # Use the products list from the module when it exists; allow it to be commented out.
    static_products = getattr(products_module, 'products', [])
except Exception:
    # If import fails for any reason, fall back to an empty list so the app keeps working.
    static_products = []

from .serializers import ProductSerializer
from rest_framework import serializers


# Create your views here.
@api_view(['GET'])
def getRoutes(request):
    routes = [
        '/api/products/',
        '/api/products/<id>/',
        '/api/users/login/',
        '/api/users/register/',
    ]
    return JsonResponse(routes, safe=False)


@api_view(['GET'])
def getProducts(request):
    products = Product.objects.all().order_by('-createdAt')
    serializer = ProductSerializer(products, many=True)
    db_products = list(serializer.data)

    # Return DB products plus static products together (no deduplication)
    combined = db_products + static_products
    return Response(combined)


@api_view(['GET'])
def getProduct(request, pk):
    # If pk is numeric, try DB first; otherwise treat as static id
    if str(pk).isdigit():
        try:
            product = Product.objects.get(_id=pk)
            serializer = ProductSerializer(product, many=False)
            return Response(serializer.data)
        except Product.DoesNotExist:
            raise Http404
    else:
        # static product id (e.g. 's1')
        for item in static_products:
            if item['_id'] == str(pk):
                return Response(item)
        raise Http404
    
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import viewsets, permissions
from rest_framework.response import Response as DRFResponse
from rest_framework.decorators import action
import traceback

class UserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField(read_only=True)
    _id = serializers.SerializerMethodField(read_only=True)
    isAdmin = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = User
        # include SerializerMethodField names here ('name', '_id', 'isAdmin')
        fields = ['id', 'username', 'email', 'isAdmin', 'name', '_id']
    def get__id(self, obj):
        return obj.id
    def get_isAdmin(self, obj):
        return obj.is_staff
    def get_name(self, obj):
        name = obj.first_name
        if name == '':
            # fallback to email, then username when no first name provided
            name = obj.email if obj.email else obj.username
        return name

@api_view(['GET'])
def getUserProfile(request):
    user = request.user
    serializer = UserSerializer(user, many=False)
    return Response(serializer.data)


@api_view(['POST'])
def registerUser(request):
    data = request.data

    try:
        # Accept username (preferred) and optional email. Email is not required.
        # Also allow using `name` as the username when `username` is not provided.
        username = data.get('username') or data.get('email') or data.get('name')
        if not username:
            return Response({'detail': 'username (or name) is required'}, status=400)

        user = User.objects.create_user(
            username=username,
            email=data.get('email',''),
            password=data['password'],
            first_name=data.get('name','')
        )
        user.save()

        refresh = RefreshToken.for_user(user)

        serializer = UserSerializer(user, many=False).data

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            **serializer
        })

    except Exception as e:
        return Response({'detail': str(e)}, status=400)

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        
        serializer = UserSerializer(self.user).data

        for k, v in serializer.items():
            data[k] = v

        return data


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


# DRF ViewSets for API
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by('-createdAt')
    serializer_class = ProductSerializer

    def get_permissions(self):
        # Allow anyone to read, but require auth for write actions
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [p() for p in permission_classes]

    def list(self, request, *args, **kwargs):
        try:
            # Return DB products plus static products together (no deduplication)
            products = Product.objects.all().order_by('-createdAt')
            serializer = ProductSerializer(products, many=True)
            db_products = list(serializer.data)

            # Ensure static_products is a list
            extras = static_products if isinstance(static_products, list) else []
            combined = db_products + extras
            return DRFResponse(combined)
        except Exception as e:
            print('Error in ProductViewSet.list:', e)
            traceback.print_exc()
            return DRFResponse({'detail': 'Server error while listing products', 'error': str(e)}, status=500)

    def retrieve(self, request, pk=None, *args, **kwargs):
        try:
            # If pk is numeric, try DB first; otherwise treat as static id
            if str(pk).isdigit():
                try:
                    product = Product.objects.get(_id=pk)
                    serializer = ProductSerializer(product, many=False)
                    return DRFResponse(serializer.data)
                except Product.DoesNotExist:
                    # fall through to 404
                    pass

            # static product id (e.g. 's1')
            extras = static_products if isinstance(static_products, list) else []
            for item in extras:
                try:
                    if item and item.get('_id') == str(pk):
                        return DRFResponse(item)
                except Exception:
                    # skip malformed static entries
                    continue

            return DRFResponse({'detail': 'Not found.'}, status=404)
        except Exception as e:
            print('Error in ProductViewSet.retrieve:', e)
            traceback.print_exc()
            return DRFResponse({'detail': 'Server error while retrieving product', 'error': str(e)}, status=500)


class UserViewSet(viewsets.ViewSet):
    # list: admin only, retrieve: authenticated, create: open
    def list(self, request):
        if not request.user.is_staff:
            return DRFResponse({'detail': 'Not authorized'}, status=403)
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return DRFResponse(serializer.data)

    def retrieve(self, request, pk=None):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return DRFResponse({'detail': 'Not found'}, status=404)
        # allow user to fetch own profile or admins
        if request.user.is_authenticated and (request.user.id == user.id or request.user.is_staff):
            serializer = UserSerializer(user, many=False)
            return DRFResponse(serializer.data)
        return DRFResponse({'detail': 'Not authorized'}, status=403)

    def create(self, request):
        data = request.data
        username = data.get('username') or data.get('email') or data.get('name')
        if not username:
            return DRFResponse({'detail': 'username (or name) is required'}, status=400)
        password = data.get('password')
        if not password:
            return DRFResponse({'detail': 'password is required'}, status=400)
        try:
            user = User.objects.create_user(
                username=username,
                email=data.get('email',''),
                password=password,
                first_name=data.get('name','')
            )
            user.save()
            serializer = UserSerializer(user, many=False).data
            refresh = RefreshToken.for_user(user)
            return DRFResponse({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                **serializer
            })
        except Exception as e:
            return DRFResponse({'detail': str(e)}, status=400)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        serializer = UserSerializer(request.user, many=False)
        return DRFResponse(serializer.data)

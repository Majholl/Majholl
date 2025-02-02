from rest_framework.response import Response
from rest_framework.decorators import api_view 
from mainrobot.models import users
from django.core.serializers import serialize
from .seri import UserSerializer
from drf_yasg import openapi
from drf_yasg.views import get_schema_view


schema_view = get_schema_view(
    openapi.Info(
        title="Your API",
        default_version='v1',
        description="API documentation for Your Django Project",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="contact@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    
)





@api_view(['GET'])
def get_all_users(request):
    all_users = users.objects.all()
    serialize_users = UserSerializer(all_users , many=True)
    return Response(serialize_users.data)



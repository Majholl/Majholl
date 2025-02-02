from rest_framework import serializers
from mainrobot.models import users


class UserSerializer(serializers.ModelSerializer):
    class Meta : 
        model = users
        fields = ['id' , 'user_id' , 'phone_number']
from rest_framework import serializers
import json

class UserCVSerializer(serializers.Serializer):
    cv = serializers.FileField()
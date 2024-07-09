from rest_framework import serializers
import json

class UserCVSerializer(serializers.Serializer):
    cv = serializers.FileField()

    def validate_cv(self, value):
        """
        Check that the uploaded file is a PDF.
        """
        if not value.name.endswith('.pdf'):
            raise serializers.ValidationError("Only PDF files are allowed.")
        return value
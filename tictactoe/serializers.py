from rest_framework import serializers
from .models import Room

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ["id", "code", "created_at", "host_id", "players"]
        read_only_fields = ["id", "code", "created_at", "host_id", "players"]
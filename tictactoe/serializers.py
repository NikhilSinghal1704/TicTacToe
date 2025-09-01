from rest_framework import serializers
from .models import Room

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ["id", "code", "created_at"]
        read_only_fields = ["id", "code", "created_at"]
        
class AddPlayerSerializer(serializers.ModelSerializer):
    # extra input fields
    player_id = serializers.CharField(write_only=True, max_length=100)
    code = serializers.CharField(write_only=True, max_length=6)

    class Meta:
        model = Room
        fields = ["player_id", "code", "id", "created_at", "players"]
        read_only_fields = ["id", "created_at", "players"]

    def validate(self, data):
        # ensure room exists
        try:
            room = Room.objects.get(code=data["code"])
        except Room.DoesNotExist:
            raise serializers.ValidationError({"code": "Room not found"})
        
        # store room instance for later use in .save()
        self.context["room"] = room
        return data

    def save(self, **kwargs):
        room = self.context["room"]
        player_id = self.validated_data["player_id"]

        if not room.add_player(player_id):
            raise serializers.ValidationError({"players": "Room is full"})
        return room

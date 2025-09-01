from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import *
from .serializers import *


class CreateRoomView(APIView):
    """
    Create a new room and assign the creator as host.
    Expects JSON: {"player_id": "some-uuid"}
    """
    def post(self, request, *args, **kwargs):
        player_id = request.data.get("player_id")
        if not player_id:
            return Response(
                {"error": "player_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        # Create room and set host
        room = Room.objects.create(host_id=player_id, players=[player_id])
        serializer = RoomSerializer(room)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class DeleteRoomView(APIView):
    """
    Delete a room by code
    """
    def delete(self, request, code, *args, **kwargs):
        try:
            room = Room.objects.get(code=code)
            room.delete()
            return Response({"message": f"Room {code} deleted successfully"}, status=status.HTTP_200_OK)
        except Room.DoesNotExist:
            return Response({"error": "Room not found"}, status=status.HTTP_404_NOT_FOUND)

from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import *
from .serializers import *

# Create
class CreateRoomView(APIView):
    def get(self, request, *args, **kwargs):
        room = Room.objects.create()
        serializer = RoomSerializer(room)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class AddPlayerView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = AddPlayerSerializer(data=request.data)
        if serializer.is_valid():
            room = serializer.save()
            return Response(AddPlayerSerializer(room).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Delete
class DeleteRoomView(APIView):
    def delete(self, request, code, *args, **kwargs):
        try:
            room = Room.objects.get(code=code)
            room.delete()
            return Response({"message": f"Room {code} deleted successfully"}, status=status.HTTP_200_OK)
        except Room.DoesNotExist:
            return Response({"error": "Room not found"}, status=status.HTTP_404_NOT_FOUND)


from rest_framework.decorators import api_view
from rest_framework.response import Response
from base.models import Room
from .serializers import RoomSerializer


@api_view(['GET'])

def getRoutes(request):#function to get all the routes
   routes=[
      'GET/api/',#api to get the routes
      'GET/api/rooms',#api to get all the rooms for the users to see
      'GET/api/rooms/:id',#api to get a single room depesnding on the id
   ]
   return Response(routes)#returning the routes as a json response.safe means we can use just more than python dictionaries
@api_view(['GET'])
def getRooms(request):
   rooms=Room.objects.all()
   serializer=RoomSerializer(rooms,many=True)
   return Response(serializer.data) 

@api_view(['GET'])
def getRoom(reques,pk):
   room=Room.objects.get(id=pk)
   serializer=RoomSerializer(room,many=False)
   return Response(serializer.data) 
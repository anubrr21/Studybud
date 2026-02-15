from rest_framework.serializers import ModelSerializer
from base.models import Room


class RoomSerializer(ModelSerializer):#serializer for the room model
    class Meta:
        model=Room
        fields='__all__'#gives us all the fields of the model 
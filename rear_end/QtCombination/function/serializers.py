# serializers.py
from rest_framework import serializers
from basic.models import Shelter, PointFeature, IdlePerson

class PointFeatureSerializer(serializers.ModelSerializer):
    longitude = serializers.SerializerMethodField()
    latitude = serializers.SerializerMethodField()

    class Meta:
        model = PointFeature
        fields = ['name', 'longitude', 'latitude']

    def get_longitude(self, obj):
        return obj.coordinates.x if obj.coordinates else None

    def get_latitude(self, obj):
        return obj.coordinates.y if obj.coordinates else None


class ShelterSerializer(serializers.ModelSerializer):
    point = PointFeatureSerializer(read_only=True)

    class Meta:
        model = Shelter
        fields = ['shelter_id', 'point']


class IdlePersonSerializer(serializers.ModelSerializer):
    location = PointFeatureSerializer(read_only=True)

    class Meta:
        model = IdlePerson
        fields = ['id', 'name', 'contact', 'location']


class LocationSerializer(serializers.ModelSerializer):
    longitude = serializers.SerializerMethodField()
    latitude = serializers.SerializerMethodField()

    class Meta:
        model = PointFeature
        fields = ['name', 'longitude', 'latitude']

    def get_longitude(self, obj):
        return obj.coordinates.x if obj.coordinates else None

    def get_latitude(self, obj):
        return obj.coordinates.y if obj.coordinates else None


class RescueStationSerializer(serializers.ModelSerializer):
    point = LocationSerializer(read_only=True)

    class Meta:
        model = Shelter
        fields = ['shelter_id', 'point']

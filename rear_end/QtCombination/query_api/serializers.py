from rest_framework import serializers
from basic.models import WeatherData

class QuerySerializer(serializers.ModelSerializer):

    class Meta:
        model = WeatherData
        fields = ['weather_id', 'precipitation', 'wind_speed', 'temperature', 'datetime']
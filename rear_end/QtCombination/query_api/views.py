# from django.shortcuts import render
#
# # Create your views here.
#  # vivew.py
# from django.db.models import F
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from basic.models import WeatherData
# from .serializers import QuerySerializer
# from rest_framework.permissions import AllowAny
#
#
# # 商店排序列表视图
# class QuerySortedListView(APIView):
#     permission_classes = [AllowAny]
#
#     def get(self, request, format=None):
#         query = Bicycle.objects.all().order_by('-id')  # 直接使用 order_by 进行排序
#         serializer = QuerySerializer(query, many=True)
#         print()
#         return Response({'code': 0, 'data': serializer.data})
#
#
# class QuerySearchView(APIView):
#     permission_classes = [AllowAny]
#
#     def get(self, request, format=None):
#         queryset = Bicycle.objects.all()
#         condition = request.query_params.get('selectedOption', None)
#         if condition is not None:
#             if condition == 'normal':
#                 queryset = queryset.filter(status__icontains='正常')
#             elif condition == 'Low_battery':
#                 queryset = queryset.filter(remaining_battery__lte=20)
#             elif condition == 'maintenance':
#                 queryset = queryset.filter(status__icontains='维护')
#             else:
#                 return Response(status=status.HTTP_400_BAD_REQUEST)
#
#         if not queryset.exists():
#             return Response({'code': 1, 'message': 'No data found'}, status=status.HTTP_404_NOT_FOUND)
#
#         serializer = QuerySerializer(queryset, many=True)
#         print(f"查询成功，查询的数据为：{serializer.data}")
#         return Response({'code': 0, 'data': serializer.data})

from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from basic.models import WeatherData
from .serializers import QuerySerializer

class QuerySortedListView(APIView):
    """
    获取所有天气数据并按 weather_id 降序排序
    返回字段：weather_id、precipitation、wind_speed、temperature
    """
    permission_classes = [AllowAny]

    def get(self, request, format=None):
        queryset = WeatherData.objects.all().order_by('-weather_id')
        serializer = QuerySerializer(queryset, many=True)
        return Response({'code': 0, 'data': serializer.data})


class QuerySearchView(APIView):
    """
    根据降水量筛选天气数据：
    - 等于 0
    - 大于 0 小于等于 300
    - 大于 300
    """
    permission_classes = [AllowAny]

    def get(self, request, format=None):
        condition = request.query_params.get('precip_condition', None)

        if condition == 'zero':
            queryset = WeatherData.objects.filter(precipitation=0)
        elif condition == 'low':
            queryset = WeatherData.objects.filter(precipitation__gt=0, precipitation__lte=300)
        elif condition == 'high':
            queryset = WeatherData.objects.filter(precipitation__gt=300)
        else:
            return Response({'code': 1, 'message': '无效的条件'}, status=status.HTTP_400_BAD_REQUEST)

        if not queryset.exists():
            print("🔍 查询结果为空")
            return Response({'code': 2, 'message': '没有找到数据'}, status=status.HTTP_404_NOT_FOUND)

        serializer = QuerySerializer(queryset, many=True)

        # ✅ 打印序列化后的数据内容（用于调试）
        print("✅ 查询结果如下：")
        for item in serializer.data:
            print(item)

        return Response({'code': 0, 'data': serializer.data})

class LatestWeatherAPIView(APIView):
    def get(self, request):
        latest_data = WeatherData.objects.order_by('-datetime').first()  # 最新一条
        if latest_data:
            serializer = QuerySerializer(latest_data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "No weather data available."}, status=status.HTTP_404_NOT_FOUND)

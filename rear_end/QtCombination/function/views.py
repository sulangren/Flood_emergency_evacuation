from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D
from basic.models import IdlePerson, Shelter,EmergencyRescueSite
from .serializers import IdlePersonSerializer, ShelterSerializer, RescueStationSerializer
import requests


class NearbySheltersAPIView(APIView):
    """
    查询给定点2000米范围内的所有避难场所，递增半径不断扩展搜索范围
    """

    def get(self, request):
        try:
            lng = float(request.query_params.get('x'))
            lat = float(request.query_params.get('y'))
            print(f"✅ 接收到坐标参数：lng = {lng}, lat = {lat}")
        except (TypeError, ValueError):
            return Response({"detail": "Invalid or missing coordinates."}, status=status.HTTP_400_BAD_REQUEST)

        user_point = Point(lng, lat, srid=4326)

        radius = 50
        max_radius = 2000
        step = 50

        shelters_qs = Shelter.objects.select_related('point')
        result = []
        seen_ids = set()

        while radius <= max_radius:
            nearby_shelters = shelters_qs.filter(
                point__coordinates__distance_lte=(user_point, D(m=radius))
            ).annotate(
                distance=Distance('point__coordinates', user_point)
            ).order_by('distance')

            for shelter in nearby_shelters:
                if shelter.shelter_id not in seen_ids:
                    s_data = ShelterSerializer(shelter).data
                    result.append({
                        "shelter_id": s_data["shelter_id"],
                        "name": s_data["point"]["name"],
                        "distance": shelter.distance.m,
                        "longitude": s_data["point"]["longitude"],
                        "latitude": s_data["point"]["latitude"],
                    })
                    seen_ids.add(shelter.shelter_id)

            radius += step

        print("🔚 最终返回数据：", result)
        return Response(result)


class RescuePathAPIView(APIView):
    """
    1) 搜索闲散人员（递增半径）
    2) 搜索避难所（递增半径）
    3) 整合调用以上2个函数，返回完整路径数据
    """

    def search_idle_persons(self, start_point, count):
        print("代码已被调用：search_idle_persons")
        rescued = []
        rescued_ids = set()
        current_point = start_point

        radius_min = 50
        radius_max = 2000
        radius_step = 50

        while len(rescued) < count:
            found = False
            radius = radius_min
            while radius <= radius_max:
                candidates = IdlePerson.objects.filter(
                    location__coordinates__distance_lte=(current_point, D(m=radius))
                ).exclude(id__in=rescued_ids).annotate(
                    distance=Distance('location__coordinates', current_point)
                ).order_by('distance')

                if candidates.exists():
                    nearest = candidates.first()
                    rescued.append(nearest)
                    rescued_ids.add(nearest.id)
                    current_point = nearest.location.coordinates
                    found = True
                    break
                radius += radius_step
            if not found:
                break
        return rescued, current_point

    def search_shelter(self, point):
        print("代码已被调用：search_shelter")
        radius_min = 200
        radius_max = 3000
        radius_step = 200

        shelter = None
        for radius in range(radius_min, radius_max + radius_step, radius_step):
            shelters = Shelter.objects.filter(
                point__coordinates__distance_lte=(point, D(m=radius))
            ).annotate(
                distance=Distance('point__coordinates', point)
            ).order_by('distance')

            if shelters.exists():
                shelter = shelters.first()
                break
        return shelter

    def get(self, request):
        print("代码已被调用：get")
        try:
            x = float(request.query_params.get("x"))
            y = float(request.query_params.get("y"))
            count = int(request.query_params.get("count"))
            if count <= 0:
                raise ValueError
        except (TypeError, ValueError):
            return Response({"error": "参数格式错误"}, status=status.HTTP_400_BAD_REQUEST)

        start_point = Point(x, y, srid=4326)

        # 调用1，搜索闲散人员
        rescued, last_point = self.search_idle_persons(start_point, count)

        # 调用2，搜索避难所
        shelter = self.search_shelter(last_point if rescued else start_point)

        # 构造返回结果
        result = [{
            "type": "start",
            "x": x,
            "y": y,
        }]

        rescued_data = IdlePersonSerializer(rescued, many=True).data
        for person in rescued_data:
            result.append({
                "type": "idle_person",
                "id": person["id"],
                "name": person["name"],
                "contact": person.get("contact"),
                "x": person["location"]["longitude"],
                "y": person["location"]["latitude"],
            })

        if shelter:
            shelter_data = ShelterSerializer(shelter).data
            result.append({
                "type": "shelter",
                "id": shelter_data["shelter_id"],
                "x": shelter_data["point"]["longitude"],
                "y": shelter_data["point"]["latitude"],
            })

        return Response({"points": result}, status=status.HTTP_200_OK)

# 初始化救助站救助代码
class ShelterListAPIView(APIView):
    def get(self, request):
        shelters = Shelter.objects.all()
        serializer = RescueStationSerializer(shelters, many=True)
        print(serializer.data)
        return Response(serializer.data)


class RescuePriorityDispatchAPIView(APIView):
    """
    计算起点到所有 EmergencyRescueSite 的路径距离 + 救援优先级排序（内存模拟，不更新数据库）
    返回每次调度的 dispatch_id、点ID、名称、坐标、剩余人数
    """

    def get(self, request):
        try:
            x = float(request.query_params.get('x'))
            y = float(request.query_params.get('y'))
            dispatch_count = int(request.query_params.get('count', 1))
        except (TypeError, ValueError):
            return Response({"error": "无效参数"}, status=status.HTTP_400_BAD_REQUEST)

        start_point = f"{x},{y}"
        gaode_key = "e9a721ea653d671cc3a28de9bc2cb897"
        max_range = 50000  # 最大路径距离

        rescue_sites = list(EmergencyRescueSite.objects.select_related("location").all())

        # 复制现场数据（内存模拟）
        site_data = {}
        for site in rescue_sites:
            site_data[site.id] = {
                "current_people": site.current_people,
                "material_weight": max(site.material_weight, 1),
                "emergency_people": site.emergency_rescue_people,
                "water_depth": site.water_depth,
                "location": site.location.coordinates,
                "name": site.location.name or "未命名"
            }

        dispatch_path = []

        while True:
            candidates = []

            for site in rescue_sites:
                sd = site_data[site.id]
                if sd["current_people"] <= 0:
                    continue

                loc = sd["location"]
                end_point = f"{loc.x},{loc.y}"

                url = f"https://restapi.amap.com/v3/direction/walking?origin={start_point}&destination={end_point}&key={gaode_key}"
                try:
                    res = requests.get(url, timeout=5)
                    data = res.json()
                    if data.get("status") != "1":
                        continue

                    distance = int(data["route"]["paths"][0]["distance"])
                    if distance > max_range:
                        continue

                    norm_distance = max_range - distance

                    # 救援等级
                    matrix1 = [
                        sd["current_people"],
                        sd["material_weight"],
                        sd["emergency_people"],
                    ]
                    w1 = [0.068236804, 0.213733483, 0.718029713]
                    rescue_level = sum(a * b for a, b in zip(matrix1, w1))

                    # 救援优先级
                    matrix2 = [norm_distance, sd["water_depth"], rescue_level]
                    w2 = [0.088202089, 0.24310092, 0.668696991]
                    priority_score = sum(a * b for a, b in zip(matrix2, w2))

                    candidates.append({
                        "id": site.id,
                        "name": sd["name"],
                        "x": loc.x,
                        "y": loc.y,
                        "distance": distance,
                        "priority": priority_score,
                        "current_people": sd["current_people"],
                    })
                except Exception as e:
                    print(f"❌ 高德API调用失败: {e}")
                    continue

            if not candidates:
                break

            # 选出优先级最高的点
            top = max(candidates, key=lambda x: x["priority"])

            dispatch_path.append({
                "dispatch_id": len(dispatch_path) + 1,  # 第几次调度
                "id": top["id"],
                "name": top["name"],
                "x": top["x"],
                "y": top["y"],
                "remaining_people": max(top["current_people"] - dispatch_count, 0),
            })

            # 模拟更新
            sd = site_data[top["id"]]
            sd["current_people"] = max(sd["current_people"] - dispatch_count, 0)
            sd["material_weight"] = max(sd["material_weight"] - 1, 1)
            sd["emergency_people"] = max(sd["emergency_people"] - dispatch_count, 0)

            start_point = f"{top['x']},{top['y']}"

            if all(s["current_people"] <= 0 for s in site_data.values()):
                break

        print(dispatch_path)

        return Response({
            "start_point": [x, y],
            "dispatch_path": dispatch_path,
        }, status=status.HTTP_200_OK)
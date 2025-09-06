import requests

# 替换成你自己的高德Key
AMAP_KEY = ""
CITY_NAME = "郑州市"

def get_city_boundary(city_name, amap_key):
    url = "https://restapi.amap.com/v3/config/district"
    params = {
        "keywords": city_name,
        "key": amap_key,
        "subdistrict": 0,
        "extensions": "all"
    }

    response = requests.get(url, params=params)
    data = response.json()

    if data.get("status") != "1":
        print("请求失败:", data.get("info"))
        return []

    districts = data.get("districts", [])
    if not districts:
        print("没有找到对应城市")
        return []

    # 可能会有多个 polyline，需要合并处理
    polyline_str = districts[0].get("polyline", "")
    # polyline 字符串可能是多个区域用 | 分隔
    polygon_list = polyline_str.split('|')

    boundary_coords = []
    for polygon in polygon_list:
        coords = []
        points = polygon.split(';')
        for point in points:
            lng, lat = map(float, point.split(','))
            coords.append([lng, lat])
        boundary_coords.append(coords)

    return boundary_coords

# 使用示例
boundary = get_city_boundary(CITY_NAME, AMAP_KEY)

# 输出坐标
for i, polygon in enumerate(boundary):
    print(f"Polygon {i+1}:")
    for coord in polygon:
        print(coord)

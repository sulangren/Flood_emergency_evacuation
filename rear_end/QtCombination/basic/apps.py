from django.apps import AppConfig

class WeatherConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'basic'  # 确保这里是你的 app 名字

    def ready(self):
        import os
        import sys
        import threading
        import time
        import requests
        import json
        from datetime import datetime

        if os.environ.get('RUN_MAIN') != 'true' and 'runserver' in sys.argv:
            return

        def fetch_weather_loop():
            while True:
                try:
                    # ⬇️ 这里才导入 models，避免 AppRegistryNotReady
                    from .models import WeatherData, City

                    API_KEY = '26e422db9831445d892bb2d732a15826'
                    LOCATION = '101180101'
                    BASE_URL = 'https://pm2tun7rtp.re.qweatherapi.com/v7/weather/now'
                    headers = {
                        'X-QW-Api-Key': API_KEY,
                        'Accept-Encoding': 'gzip'
                    }
                    params = {
                        'location': LOCATION
                    }

                    response = requests.get(BASE_URL, headers=headers, params=params)
                    response.raise_for_status()
                    data = response.json()

                    now = data.get('now', {})
                    text = now.get('text', '未知')
                    wind_speed = float(now.get('windSpeed', 0))
                    temp = float(now.get('temp', 0))
                    precip = float(now.get('precip', 0))
                    obs_time = datetime.strptime(now.get('obsTime'), '%Y-%m-%dT%H:%M%z')
                    date_only = obs_time.date()

                    text_map = {
                        '晴': 'sunny', '多云': 'cloudy', '雨': 'rainy', '雪': 'snowy',
                        '雾': 'foggy', '暴风雨': 'stormy'
                    }
                    weather_condition = text_map.get(text, 'unknown')

                    city = City.objects.get(name='郑州市')  # 或你的实际城市

                    # 修改的行在这里
                    WeatherData.objects.update_or_create(
                        city=city,
                        datetime=obs_time,  # 使用 datetime 字段
                        defaults={
                            'precipitation': precip,
                            'wind_speed': wind_speed,
                            'temperature': temp,
                            'weather_condition': weather_condition,
                        }
                    )

                    filename = obs_time.strftime('weather_data/%Y%m%d_%H.json')
                    os.makedirs('weather_data', exist_ok=True)
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=4)

                    print(f"✅ [{datetime.now()}] 数据入库并保存文件：{filename}")
                except Exception as e:
                    print(f"❌ 错误: {e}")
                print("⏳ 等待1小时...")
                time.sleep(3600)

        threading.Thread(target=fetch_weather_loop, daemon=True).start()


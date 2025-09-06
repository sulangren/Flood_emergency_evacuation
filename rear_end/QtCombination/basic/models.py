# from django.contrib.gis.db import models
from django.contrib.gis.db import models

# 用户表
class staffUser(models.Model):
    class Meta():
        db_table = 'db_staff_user'

    # 用户名
    staff_username = models.CharField(max_length=15, unique=True, null=False)
    # 密码
    staff_password = models.CharField(max_length=15, null=False)
    # 电话号码
    staff_telephone = models.CharField(max_length=12, unique=True,null=True)

class City(models.Model):
    """
    城市模型
    """
    city_id = models.AutoField(primary_key=True, verbose_name='城市ID')
    name = models.CharField(max_length=100, verbose_name='城市名')
    area = models.FloatField(verbose_name='城市面积', null=True, blank=True)  # 单位可以是平方公里
    boundary = models.PolygonField(verbose_name='城市范围', srid=4326)  # 面数据，使用WGS84坐标系统
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '城市'
        verbose_name_plural = '城市'
        indexes = [
            models.Index(fields=['name']),
        ]

    def __str__(self):
        return self.name

class PointFeature(models.Model):
    """
    点要素模型
    """
    pid = models.AutoField(primary_key=True, verbose_name='编号')
    name = models.CharField(max_length=100, verbose_name='场所名', null=True, blank=True)
    elevation = models.FloatField(verbose_name='高程', null=True, blank=True)  # 单位可以是米
    coordinates = models.PointField(verbose_name='坐标', srid=4326)  # 使用WGS84坐标系统
    city = models.ForeignKey(
        City,
        on_delete=models.CASCADE,
        verbose_name='所属城市',
        related_name='points'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '点要素'
        verbose_name_plural = '点要素'
        indexes = [
            models.Index(fields=['city']),
            models.Index(fields=['coordinates']),
        ]

    def __str__(self):
        return f"点{self.pid}" + (f" - {self.name}" if self.name else "")

class Shelter(models.Model):
    """
    避难场所模型
    """
    shelter_id = models.AutoField(primary_key=True, verbose_name='避难场所ID')
    point = models.OneToOneField(
        PointFeature,
        on_delete=models.CASCADE,
        verbose_name='避难场所点',
        related_name='shelter'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '避难场所'
        verbose_name_plural = '避难场所'

    def __str__(self):
        return f"避难场所 {self.shelter_id}"

class FloodProneArea(models.Model):
    """
    容易积水处模型
    """
    flood_id = models.AutoField(primary_key=True, verbose_name='容易积水处ID')
    point = models.OneToOneField(
        PointFeature,
        on_delete=models.CASCADE,
        verbose_name='积水处中心点',
        related_name='flood_prone_area'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '容易积水处'
        verbose_name_plural = '容易积水处'

    def __str__(self):
        return f"积水点 {self.flood_id}"

class Pipeline(models.Model):
    """
    管线数据模型
    """
    pipeline_id = models.IntegerField(verbose_name='管线编号')
    sub_id = models.IntegerField(verbose_name='所属子编号', default=0)
    start_point = models.ForeignKey(
        PointFeature,
        on_delete=models.CASCADE,
        verbose_name='起始点',
        related_name='pipeline_starts'
    )
    end_point = models.ForeignKey(
        PointFeature,
        on_delete=models.CASCADE,
        verbose_name='终点',
        related_name='pipeline_ends'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '管线数据'
        verbose_name_plural = '管线数据'
        unique_together = (('pipeline_id', 'sub_id'),)
        indexes = [
            models.Index(fields=['pipeline_id', 'sub_id']),
        ]

    def __str__(self):
        return f"管线 {self.pipeline_id}-{self.sub_id}"

class WeatherData(models.Model):
    """
    气象数据模型
    """
    WEATHER_CHOICES = [
        ('sunny', '晴'),
        ('cloudy', '多云'),
        ('rainy', '雨'),
        ('snowy', '雪'),
        ('foggy', '雾'),
        ('stormy', '暴风雨'),
        ('unknown', '未知'),
    ]

    weather_id = models.AutoField(primary_key=True, verbose_name='ID')
    precipitation = models.FloatField(verbose_name='降水量', null=True, blank=True)  # 单位可以是毫米
    wind_speed = models.FloatField(verbose_name='风速', null=True, blank=True)  # 单位可以是米/秒
    temperature = models.FloatField(verbose_name='温度', null=True, blank=True)  # 单位可以是摄氏度
    weather_condition = models.CharField(
        max_length=20,
        choices=WEATHER_CHOICES,
        verbose_name='天气',
        null=True,
        blank=True,
        default='unknown'
    )
    datetime = models.DateTimeField(verbose_name='日期时间', null=True, blank=True)
    city = models.ForeignKey(
        City,
        on_delete=models.CASCADE,
        verbose_name='城市',
        related_name='weather_data'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '气象数据'
        verbose_name_plural = '气象数据'
        indexes = [
            models.Index(fields=['datetime']),
            models.Index(fields=['city']),
        ]
        unique_together = (('city', 'datetime'),)

    def __str__(self):
        return f"{self.city.name} - {self.datetime or '无日期'} 天气数据"

class IdlePerson(models.Model):
    """
    待救援闲散人员
    """
    id = models.AutoField(primary_key=True, verbose_name='人员ID')
    location = models.ForeignKey(
        PointFeature,
        on_delete=models.CASCADE,
        verbose_name='位置',
        related_name='idle_persons'
    )
    name = models.CharField(max_length=100, verbose_name='姓名')
    contact = models.BigIntegerField(null=True, blank=True, verbose_name='联系方式')  # int型，支持11位手机号

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '待救援闲散人员'
        verbose_name_plural = '待救援闲散人员'

    def __str__(self):
        return f"{self.name}（{self.id}）"

class EmergencyRescueSite(models.Model):
    """
    待救援紧急地点
    """
    id = models.AutoField(primary_key=True, verbose_name='紧急地点ID')
    location = models.ForeignKey(
        PointFeature,
        on_delete=models.CASCADE,
        verbose_name='位置',
        related_name='emergency_sites'
    )
    nearest_safe_distance = models.FloatField(verbose_name='距安全点最近距离（米）')
    water_depth = models.FloatField(verbose_name='水淹深度（米）')
    current_people = models.IntegerField(verbose_name='现有人数')
    material_weight = models.IntegerField(verbose_name='物资权重')
    emergency_rescue_people = models.IntegerField(verbose_name='紧急救援人数')
    capacity = models.IntegerField(null=True, blank=True, verbose_name='紧急救援地容量')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '紧急救援地点'
        verbose_name_plural = '紧急救援地点'

    def __str__(self):
        return f"紧急点 {self.id}"
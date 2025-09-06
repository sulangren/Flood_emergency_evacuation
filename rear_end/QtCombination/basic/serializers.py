from django.contrib.auth.models import User
from rest_framework import serializers
from .models import staffUser  # 导入自定义的 staffUser 模型

class UserLoginSerializer(serializers.Serializer):
    staff_username = serializers.CharField()
    staff_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        staff_username = attrs.get('staff_username')
        staff_password = attrs.get('staff_password')

        if staff_username and staff_password:
            try:
                # 获取对应的 staffUser 实例
                staff_user = staffUser.objects.get(staff_username=staff_username)
            except staffUser.DoesNotExist:
                raise serializers.ValidationError('Invalid username or password.', code='authorization')

            # 使用自定义 staffUser 模型验证密码
            if staff_user.staff_password != staff_password:
                raise serializers.ValidationError('Invalid username or password.', code='authorization')

            # 将 staffUser 转换为 Django 默认的 User 实例
            user, created = User.objects.get_or_create(
                username=staff_user.staff_username,
                defaults={'password': staff_user.staff_password}
            )

            if created:
                user.set_password(staff_user.staff_password)  # 使用 set_password 来加密密码
                user.save()

        else:
            raise serializers.ValidationError('Must include "staff_username" and "staff_password".', code='authorization')

        attrs['user'] = user
        return attrs

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = staffUser
        fields = ['id','staff_username', 'staff_password','staff_telephone']
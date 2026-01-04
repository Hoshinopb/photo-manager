from djoser.serializers import UserSerializer as BaseUserSerializer
from rest_framework import serializers
from .models import UserProfile


class CustomUserSerializer(BaseUserSerializer):
    """自定义用户序列化器，包含角色信息和头像"""
    avatar_url = serializers.SerializerMethodField()
    avatar_id = serializers.SerializerMethodField()
    has_vision_api_key = serializers.SerializerMethodField()
    
    class Meta(BaseUserSerializer.Meta):
        fields = BaseUserSerializer.Meta.fields + ('is_staff', 'is_superuser', 'avatar_url', 'avatar_id', 'has_vision_api_key')
        read_only_fields = BaseUserSerializer.Meta.read_only_fields + ('is_staff', 'is_superuser', 'avatar_url', 'avatar_id', 'has_vision_api_key')
    
    def get_avatar_url(self, obj):
        """获取用户头像完整 URL"""
        try:
            if hasattr(obj, 'profile') and obj.profile.avatar:
                request = self.context.get('request')
                avatar_path = obj.profile.avatar_url
                if avatar_path and request:
                    return request.build_absolute_uri(avatar_path)
                return avatar_path
        except UserProfile.DoesNotExist:
            pass
        return None
    
    def get_avatar_id(self, obj):
        """获取用户头像图片ID"""
        try:
            if hasattr(obj, 'profile') and obj.profile.avatar:
                return obj.profile.avatar.id
        except UserProfile.DoesNotExist:
            pass
        return None
    
    def get_has_vision_api_key(self, obj):
        """检查用户是否设置了 Vision API Key"""
        try:
            if hasattr(obj, 'profile'):
                return obj.profile.has_vision_api_key
        except UserProfile.DoesNotExist:
            pass
        return False
    
    def update(self, instance, validated_data):
        """更新用户信息，包括头像"""
        # 从请求数据中获取 avatar_id（不是 validated_data）
        request = self.context.get('request')
        avatar_id = None
        if request and hasattr(request, 'data'):
            avatar_id = request.data.get('avatar_id')
        
        # 更新用户基本信息
        instance = super().update(instance, validated_data)
        
        # 更新头像
        if avatar_id is not None:
            from apps.images.models import Image
            try:
                # 确保图片属于该用户
                image = Image.objects.get(id=avatar_id, owner=instance)
                # 获取或创建 profile
                profile, created = UserProfile.objects.get_or_create(user=instance)
                profile.avatar = image
                profile.save()
            except Image.DoesNotExist:
                pass
        
        return instance


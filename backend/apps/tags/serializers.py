from rest_framework import serializers
from .models import Tag


class TagSerializer(serializers.ModelSerializer):
    """标签序列化器"""
    image_count = serializers.SerializerMethodField()
    usage_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Tag
        fields = ['id', 'name', 'type', 'color', 'created_at', 'image_count', 'usage_count']
        read_only_fields = ['id', 'created_at']
    
    def get_image_count(self, obj):
        """获取使用该标签的图片数量"""
        # 优先使用 annotated 的 usage_count（如果有的话）
        if hasattr(obj, 'usage_count'):
            return obj.usage_count
        return obj.images.count()
    
    def get_usage_count(self, obj):
        """获取使用次数 - 优先使用 annotated 的值"""
        if hasattr(obj, 'usage_count'):
            return obj.usage_count
        return obj.images.count()


class TagCreateSerializer(serializers.ModelSerializer):
    """标签创建序列化器"""
    
    class Meta:
        model = Tag
        fields = ['name', 'color']
    
    def validate_name(self, value):
        """验证标签名称"""
        name = value.strip().lower()
        if len(name) < 1:
            raise serializers.ValidationError("标签名称不能为空")
        if len(name) > 100:
            raise serializers.ValidationError("标签名称不能超过100个字符")
        return name
    
    def create(self, validated_data):
        """创建标签（如果已存在则返回已有的）"""
        name = validated_data['name']
        color = validated_data.get('color', '')
        
        tag, created = Tag.objects.get_or_create(
            name=name,
            defaults={
                'type': 'user',
                'color': color,
            }
        )
        return tag

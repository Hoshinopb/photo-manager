from djoser.serializers import UserSerializer as BaseUserSerializer


class CustomUserSerializer(BaseUserSerializer):
    """自定义用户序列化器，包含角色信息"""
    
    class Meta(BaseUserSerializer.Meta):
        fields = BaseUserSerializer.Meta.fields + ('is_staff', 'is_superuser')
        read_only_fields = BaseUserSerializer.Meta.read_only_fields + ('is_staff', 'is_superuser')

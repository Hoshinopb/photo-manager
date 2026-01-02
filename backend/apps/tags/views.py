from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Count, Q as DQ

from .models import Tag
from .serializers import TagSerializer, TagCreateSerializer


class TagViewSet(viewsets.ModelViewSet):
    """
    标签视图集
    
    提供标签的增删改查功能
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return TagCreateSerializer
        return TagSerializer
    
    def get_queryset(self):
        """
        获取标签列表，支持筛选
        """
        queryset = Tag.objects.annotate(
            usage_count=Count('images')
        ).order_by('-usage_count', 'name')
        
        # 按类型筛选
        tag_type = self.request.query_params.get('type')
        if tag_type:
            queryset = queryset.filter(type=tag_type)
        
        # 搜索
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """
        获取热门标签
        规则：
        1. 排除只出现1次的标签
        2. 取前50%的标签
        3. 至少返回10个（如果总数不足10个则返回全部）
        4. 最多返回30个
        """
        # 获取所有使用次数大于1的标签
        all_tags = Tag.objects.annotate(
            usage_count=Count('images')
        ).filter(usage_count__gt=1).order_by('-usage_count')
        
        total_count = all_tags.count()
        
        if total_count == 0:
            # 如果没有使用超过1次的标签，返回空列表
            return Response([])
        
        # 计算返回数量：前50%，但至少10个，最多30个
        target_count = max(10, total_count // 2)
        target_count = min(target_count, 30, total_count)
        
        queryset = all_tags[:target_count]
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_tags(self, request):
        """获取当前用户图片使用的所有标签"""
        from apps.images.models import Image
        
        user = request.user
        # 获取用户所有图片的标签
        queryset = Tag.objects.filter(
            images__owner=user
        ).annotate(
            usage_count=Count('images', filter=DQ(images__owner=user))
        ).distinct().order_by('-usage_count', 'name')
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def auto_tags(self, request):
        """获取自动生成的标签"""
        queryset = Tag.objects.filter(type='auto').annotate(
            usage_count=Count('images')
        ).order_by('-usage_count')
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def user_tags(self, request):
        """获取用户自定义的标签"""
        queryset = Tag.objects.filter(type='user').annotate(
            usage_count=Count('images')
        ).order_by('-usage_count')
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

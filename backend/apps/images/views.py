from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.decorators import action
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta

from .models import Image, ImageTag
from .serializers import ImageSerializer, ImageUploadSerializer


class ImageViewSet(viewsets.ModelViewSet):
    """
    图片视图集
    
    提供图片的增删改查功能
    支持筛选参数：
    - owner: 按用户ID筛选
    - is_public: 按公开状态筛选 (true/false)
    - date_from: 上传时间起始
    - date_to: 上传时间截止
    - search: 搜索文件名或描述
    - ordering: 排序字段 (upload_time, -upload_time, size, -size)
    """
    serializer_class = ImageSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        获取当前用户可见的图片列表
        - 用户自己的所有图片
        - 其他用户的公开图片
        支持多种筛选条件
        """
        user = self.request.user
        queryset = Image.objects.filter(
            Q(owner=user) | Q(is_public=True)
        ).select_related('owner')
        
        # 按用户筛选
        owner_id = self.request.query_params.get('owner')
        if owner_id:
            queryset = queryset.filter(owner_id=owner_id)
        
        # 按公开状态筛选
        is_public = self.request.query_params.get('is_public')
        if is_public is not None:
            if is_public.lower() == 'true':
                queryset = queryset.filter(is_public=True)
            elif is_public.lower() == 'false':
                queryset = queryset.filter(is_public=False)
        
        # 按上传时间筛选
        date_from = self.request.query_params.get('date_from')
        if date_from:
            queryset = queryset.filter(upload_time__gte=date_from)
        
        date_to = self.request.query_params.get('date_to')
        if date_to:
            queryset = queryset.filter(upload_time__lte=date_to)
        
        # 按时间范围快捷筛选
        time_range = self.request.query_params.get('time_range')
        if time_range:
            now = timezone.now()
            if time_range == 'today':
                queryset = queryset.filter(upload_time__date=now.date())
            elif time_range == 'week':
                queryset = queryset.filter(upload_time__gte=now - timedelta(days=7))
            elif time_range == 'month':
                queryset = queryset.filter(upload_time__gte=now - timedelta(days=30))
        
        # 搜索文件名或描述
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(filename__icontains=search) | Q(description__icontains=search)
            )
        
        # 按标签筛选（支持多种模式）
        # tags: 逗号分隔的标签列表
        # tag_mode: 筛选模式 - 'and'(包含全部), 'or'(包含任一), 'not'(不包含)
        tags = self.request.query_params.get('tags')
        tag_mode = self.request.query_params.get('tag_mode', 'and')
        
        if tags:
            tag_list = [t.strip() for t in tags.split(',') if t.strip()]
            if tag_list:
                if tag_mode == 'or':
                    # OR模式：包含任意一个标签
                    queryset = queryset.filter(tags__name__in=tag_list)
                elif tag_mode == 'not':
                    # NOT模式：不包含这些标签
                    queryset = queryset.exclude(tags__name__in=tag_list)
                else:
                    # AND模式（默认）：包含所有标签
                    for tag_name in tag_list:
                        queryset = queryset.filter(tags__name__iexact=tag_name)
        
        # 兼容旧的单标签筛选
        tag = self.request.query_params.get('tag')
        if tag:
            queryset = queryset.filter(tags__name__iexact=tag)
        
        # 排序
        ordering = self.request.query_params.get('ordering', '-upload_time')
        if ordering in ['upload_time', '-upload_time', 'size', '-size', 'filename', '-filename']:
            queryset = queryset.order_by(ordering)
        
        return queryset.distinct()
    
    def get_serializer_class(self):
        """根据操作类型返回不同的序列化器"""
        if self.action == 'create':
            return ImageUploadSerializer
        return ImageSerializer
    
    @action(detail=False, methods=['get'])
    def public(self, request):
        """获取所有公开图片"""
        queryset = Image.objects.filter(is_public=True).select_related('owner')
        
        # 支持搜索
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(filename__icontains=search) | Q(description__icontains=search)
            )
        
        # 排序
        ordering = request.query_params.get('ordering', '-upload_time')
        if ordering in ['upload_time', '-upload_time', 'size', '-size']:
            queryset = queryset.order_by(ordering)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """获取当前用户的图片统计信息"""
        user = request.user
        my_images = Image.objects.filter(owner=user)
        public_images = Image.objects.filter(is_public=True)
        
        return Response({
            'my_total': my_images.count(),
            'my_public': my_images.filter(is_public=True).count(),
            'my_private': my_images.filter(is_public=False).count(),
            'all_public': public_images.count(),
        })
    
    def create(self, request, *args, **kwargs):
        """上传新图片"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # 传入当前用户作为 owner
        image = serializer.save(owner=request.user)
        
        # 返回完整的图片信息
        response_serializer = ImageSerializer(image, context={'request': request})
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    def destroy(self, request, *args, **kwargs):
        """删除图片 - 只能删除自己的图片"""
        instance = self.get_object()
        
        if instance.owner != request.user:
            return Response(
                {'detail': '您没有权限删除此图片'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # 删除文件
        if instance.file:
            instance.file.delete(save=False)
        
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def update(self, request, *args, **kwargs):
        """更新图片信息 - 只能更新自己的图片"""
        instance = self.get_object()
        
        if instance.owner != request.user:
            return Response(
                {'detail': '您没有权限修改此图片'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        return super().update(request, *args, **kwargs)
    
    def partial_update(self, request, *args, **kwargs):
        """部分更新图片信息"""
        instance = self.get_object()
        
        if instance.owner != request.user:
            return Response(
                {'detail': '您没有权限修改此图片'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        return super().partial_update(request, *args, **kwargs)
    
    @action(detail=True, methods=['post'])
    def add_tag(self, request, pk=None):
        """为图片添加标签"""
        image = self.get_object()
        
        if image.owner != request.user:
            return Response(
                {'detail': '您没有权限修改此图片'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        from .serializers import ImageTagAddSerializer
        serializer = ImageTagAddSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        tag_name = serializer.validated_data['tag_name']
        
        from apps.tags.models import Tag
        tag = Tag.get_or_create_tag(tag_name, tag_type='user')
        
        # 检查是否已存在
        if not ImageTag.objects.filter(image=image, tag=tag).exists():
            ImageTag.objects.create(image=image, tag=tag)
        
        return Response({
            'detail': '标签添加成功',
            'tag': {'id': tag.id, 'name': tag.name, 'type': tag.type}
        })
    
    @action(detail=True, methods=['delete'], url_path='remove_tag/(?P<tag_id>[^/.]+)')
    def remove_tag(self, request, pk=None, tag_id=None):
        """移除图片的标签"""
        image = self.get_object()
        
        if image.owner != request.user:
            return Response(
                {'detail': '您没有权限修改此图片'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            image_tag = ImageTag.objects.get(image=image, tag_id=tag_id)
            image_tag.delete()
            return Response({'detail': '标签已移除'})
        except ImageTag.DoesNotExist:
            return Response(
                {'detail': '标签不存在'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def parse_exif(self, request, pk=None):
        """手动触发 EXIF 解析"""
        image = self.get_object()
        
        if image.owner != request.user:
            return Response(
                {'detail': '您没有权限修改此图片'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        from .exif_utils import apply_exif_to_image
        try:
            exif_data = apply_exif_to_image(image)
            image.refresh_from_db()
            serializer = ImageSerializer(image, context={'request': request})
            return Response({
                'detail': 'EXIF 解析成功',
                'image': serializer.data
            })
        except Exception as e:
            return Response(
                {'detail': f'EXIF 解析失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class MyImagesViewSet(viewsets.ReadOnlyModelViewSet):
    """
    我的图片视图集
    
    只展示当前用户自己上传的图片
    """
    serializer_class = ImageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """获取当前用户的所有图片"""
        return Image.objects.filter(owner=self.request.user).select_related('owner').prefetch_related('tags')


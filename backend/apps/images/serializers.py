from rest_framework import serializers
from .models import Image, ImageTag
from apps.tags.serializers import TagSerializer


class ImageTagSerializer(serializers.ModelSerializer):
    """图片标签关联序列化器"""
    tag_name = serializers.CharField(source='tag.name', read_only=True)
    tag_type = serializers.CharField(source='tag.type', read_only=True)
    tag_color = serializers.CharField(source='tag.color', read_only=True)
    
    class Meta:
        model = ImageTag
        fields = ['id', 'tag', 'tag_name', 'tag_type', 'tag_color', 'created_at']
        read_only_fields = ['id', 'created_at']


class ImageSerializer(serializers.ModelSerializer):
    """图片序列化器"""
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    file_url = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()
    tags = TagSerializer(many=True, read_only=True)
    tag_list = serializers.SerializerMethodField()
    exif_info = serializers.SerializerMethodField()
    
    class Meta:
        model = Image
        fields = [
            'id', 'filename', 'file', 'file_url', 'thumbnail_url',
            'thumbnail_generated', 'processing_status', 'size', 
            'width', 'height', 'upload_time', 'is_public', 
            'description', 'owner', 'owner_username',
            'tags', 'tag_list', 'exif_info', 'exif_parsed',
            'exif_datetime'
        ]
        read_only_fields = ['id', 'owner', 'size', 'width', 'height', 'upload_time', 'filename', 'exif_parsed', 'thumbnail_generated', 'processing_status']
    
    def get_file_url(self, obj):
        """获取完整的文件URL"""
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return None
    
    def get_thumbnail_url(self, obj):
        """获取缩略图URL"""
        request = self.context.get('request')
        if obj.thumbnail and obj.thumbnail_generated and request:
            return request.build_absolute_uri(obj.thumbnail.url)
        # 如果没有缩略图，返回原图URL作为备选
        return self.get_file_url(obj)
    
    def get_tag_list(self, obj):
        """获取标签名称列表"""
        return [tag.name for tag in obj.tags.all()]
    
    def get_exif_info(self, obj):
        """获取 EXIF 信息"""
        if not obj.exif_parsed:
            return None
        return {
            'camera_make': obj.exif_camera_make,
            'camera_model': obj.exif_camera_model,
            'datetime': obj.exif_datetime,
            'exposure_time': obj.exif_exposure_time,
            'f_number': obj.exif_f_number,
            'iso': obj.exif_iso,
            'focal_length': obj.exif_focal_length,
            'gps_latitude': obj.exif_gps_latitude,
            'gps_longitude': obj.exif_gps_longitude,
        }


class ImageUploadSerializer(serializers.ModelSerializer):
    """图片上传序列化器"""
    tags = serializers.ListField(
        child=serializers.CharField(max_length=100),
        required=False,
        default=list
    )
    
    class Meta:
        model = Image
        fields = ['file', 'is_public', 'description', 'tags']
    
    def validate_file(self, value):
        """验证上传的文件"""
        # 检查文件扩展名
        filename = value.name
        ext = filename.split('.')[-1].lower()
        
        if ext not in Image.ALLOWED_EXTENSIONS:
            raise serializers.ValidationError(
                f"不支持的文件格式。允许的格式: {', '.join(Image.ALLOWED_EXTENSIONS)}"
            )
        
        # 检查文件大小（最大 10MB）
        max_size = 10 * 1024 * 1024
        if value.size > max_size:
            raise serializers.ValidationError(
                f"文件大小超过限制。最大允许: {max_size // (1024 * 1024)}MB"
            )
        
        return value
    
    def create(self, validated_data):
        """创建图片记录"""
        file = validated_data['file']
        user_tags = validated_data.pop('tags', [])
        
        # 获取图片尺寸
        from PIL import Image as PILImage
        try:
            img = PILImage.open(file)
            width, height = img.size
        except Exception:
            width, height = None, None
        
        # 重置文件指针
        file.seek(0)
        
        image = Image.objects.create(
            owner=validated_data['owner'],
            file=file,
            filename=file.name,
            size=file.size,
            width=width,
            height=height,
            is_public=validated_data.get('is_public', False),
            description=validated_data.get('description', ''),
            processing_status='pending'  # 初始状态为等待处理
        )
        
        # 添加用户指定的标签（同步处理，因为用户需要立即看到）
        if user_tags:
            from apps.tags.models import Tag
            for tag_name in user_tags:
                tag = Tag.get_or_create_tag(tag_name.strip(), tag_type='user')
                if not ImageTag.objects.filter(image=image, tag=tag).exists():
                    ImageTag.objects.create(image=image, tag=tag)
        
        # 触发异步处理任务（缩略图生成、EXIF解析、AI标注）
        try:
            from .tasks import process_image_async
            process_image_async.delay(image.id)
        except Exception as e:
            # 如果 Celery 不可用，则同步处理作为降级方案
            print(f"异步任务触发失败，使用同步处理: {e}")
            from .exif_utils import apply_exif_to_image
            try:
                apply_exif_to_image(image)
                image.processing_status = 'completed'
                image.save(update_fields=['processing_status'])
            except Exception as ex:
                print(f"同步 EXIF 解析失败: {ex}")
                image.processing_status = 'failed'
                image.save(update_fields=['processing_status'])
        
        return image


class ImageTagAddSerializer(serializers.Serializer):
    """添加标签序列化器"""
    tag_name = serializers.CharField(max_length=100)
    
    def validate_tag_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("标签名不能为空")
        return value.strip()
